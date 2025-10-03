# options_dialog.py
import json
import re
import traceback
import os
import subprocess
import sys
from pathlib import Path

# --- PyQt6 Imports ---
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QSpinBox,
    QCheckBox, QTabWidget, QSlider, QComboBox, QFrame, QSpacerItem, QSizePolicy,
    QGroupBox, QListWidget, QListWidgetItem, QTextEdit, QFileDialog, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QStandardPaths, QUrl
from PyQt6.QtGui import QDesktopServices, QIcon

# --- Local Module Imports ---
import config_manager
from config_manager import (
    ENTRY_TYPE_PREDEFINED, ENTRY_TYPE_ANYTHING, ENTRY_TYPE_CUSTOM,
    VALID_ENTRY_TYPES, PREDEFINED_COMMANDS,
    ANIM_TYPE_HACKING, ANIM_TYPE_TRIGLAVIAN, # ANIM_TYPE_LIST removed
    ANIM_TYPE_NODE_PATH, ANIM_TYPE_TRIG_CONDUIT,
    ANIM_TYPE_TRIG_CODE_REVEAL,
    ANIM_TYPE_RANDOM_TECH,
    VALID_ANIMATION_TYPES,
    TRIG_SPEED_FAST, TRIG_SPEED_NORMAL, TRIG_SPEED_SLOW, VALID_TRIG_SPEEDS,
    NODE_PATH_SPEED_NORMAL, NODE_PATH_SPEED_SLOW, NODE_PATH_SPEED_VERY_SLOW, VALID_NODE_PATH_SPEEDS,
    TRIG_CONDUIT_SPEED_FAST, TRIG_CONDUIT_SPEED_NORMAL, TRIG_CONDUIT_SPEED_SLOW, VALID_TRIG_CONDUIT_SPEEDS,
    TRIG_CODE_REVEAL_SPEED_FAST, TRIG_CODE_REVEAL_SPEED_NORMAL, TRIG_CODE_REVEAL_SPEED_SLOW, VALID_TRIG_CODE_REVEAL_SPEEDS,
    TRIG_CODE_ALPHANUMERIC_GLYPHS,
    _validate_geometry_string,
    APP_NAME, ORG_NAME,
    PRIZE_MODE_STREAMER, PRIZE_MODE_POLL, VALID_PRIZE_MODES
)

# Map internal names to config keys
WIDGET_CONFIG_MAP = {
    "main_action_buttons": "main_action_buttons_geometry",
    "prize_controls": "top_controls_geometry",
    "entrants_panel": "entrants_panel_geometry",
    "main_stack": "main_stack_geometry"
}


class OptionsDialog(QDialog):
    reset_layout_signal = pyqtSignal()
    save_layout_signal = pyqtSignal()
    font_size_changed = pyqtSignal(float) 
    lock_state_changed = pyqtSignal(bool)
    apply_font_now_signal = pyqtSignal(float) 

    def __init__(self, current_config, parent=None):
        super().__init__(parent)
        self.initial_config_snapshot = json.loads(json.dumps(current_config))
        self.working_config_snapshot = json.loads(json.dumps(current_config))
        self.parent_app = parent 
        self.setWindowTitle("Giveaway Options")
        
        # Dynamic sizing based on font multiplier
        font_multiplier = current_config.get('font_size_multiplier', 1.0)
        base_width = 650
        base_height = 750
        scaled_width = int(base_width * font_multiplier)
        scaled_height = int(base_height * font_multiplier)
        self.setMinimumWidth(max(scaled_width, 650))  # At least 650px
        self.setMinimumHeight(max(scaled_height, 750))  # At least 750px
        self.resize(scaled_width, scaled_height)


        self.tab_widget = QTabWidget(self)
        self.general_tab = QWidget()
        self.layout_tab = QWidget()
        self.sound_tab = QWidget()
        self.draw_style_tab = QWidget()
        self.prizes_tab = QWidget()
        self.analytics_tab = QWidget()

        # Populate tabs first (they need to have content before scrolling)
        self._populate_general_tab()
        self._populate_layout_tab()
        self._populate_sound_tab()
        self._populate_draw_style_tab()
        self._populate_prizes_tab()
        self._populate_analytics_tab()

        # Add tabs with scroll areas for content overflow
        self.tab_widget.addTab(self._make_tab_scrollable(self.general_tab), "General")
        self.tab_widget.addTab(self._make_tab_scrollable(self.layout_tab), "Layout")
        self.tab_widget.addTab(self._make_tab_scrollable(self.sound_tab), "Sound")
        self.tab_widget.addTab(self._make_tab_scrollable(self.draw_style_tab), "Draw Style")
        self.tab_widget.addTab(self._make_tab_scrollable(self.prizes_tab), "Prizes")
        self.tab_widget.addTab(self._make_tab_scrollable(self.analytics_tab), "Analytics & Logging")

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(self.button_box)

        if QApplication.instance():
            self.setStyleSheet(QApplication.instance().styleSheet())
    
    def _make_tab_scrollable(self, tab_widget):
        """Wrap a tab widget in a scroll area for better content handling"""
        scroll = QScrollArea()
        scroll.setWidget(tab_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return scroll

    def _populate_general_tab(self):
        layout = QFormLayout(self.general_tab)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Confirmation timeout
        self.confirm_timeout_spin = QSpinBox()
        self.confirm_timeout_spin.setRange(5, 999)
        self.confirm_timeout_spin.setValue(self.working_config_snapshot.get("confirmation_timeout", 90))
        self.confirm_timeout_spin.setSuffix(" sec")
        layout.addRow("Confirmation Timeout:", self.confirm_timeout_spin)

        # EVE2Twitch response timeout
        self.eve_timeout_label = QLabel("Eve2Twitch IGN Timeout:")
        self.eve_timeout_label.setWordWrap(True)
        self.eve_timeout_spin = QSpinBox()
        self.eve_timeout_spin.setRange(10, 999)
        self.eve_timeout_spin.setValue(self.working_config_snapshot.get("eve_response_timeout", 300))
        self.eve_timeout_spin.setSuffix(" sec")
        self.eve_timeout_spin.setToolTip("How long to wait for the EVE Bot response after !ign.")
        layout.addRow(self.eve_timeout_label, self.eve_timeout_spin)

        # How long to wait for automatic EVE2Twitch lookup before asking the winner to type !ign
        self.eve2twitch_lookup_label = QLabel("Auto-lookup Timeout:")
        self.eve2twitch_lookup_label.setWordWrap(True)
        self.eve2twitch_lookup_spin = QSpinBox()
        self.eve2twitch_lookup_spin.setRange(1, 300)
        self.eve2twitch_lookup_spin.setValue(self.working_config_snapshot.get("eve2twitch_lookup_timeout", config_manager.DEFAULT_CONFIG.get("eve2twitch_lookup_timeout", 10)))
        self.eve2twitch_lookup_spin.setSuffix(" sec")
        self.eve2twitch_lookup_spin.setToolTip("How long to wait for automatic EVE2Twitch lookup before falling back to asking the winner to use !ign.")
        layout.addRow(self.eve2twitch_lookup_label, self.eve2twitch_lookup_spin)

        # Short timeout for quick ESI response after an auto-lookup (used to prompt for !ign if ESI is slow)
        self.esi_short_label = QLabel("Quick ESI Timeout:")
        self.esi_short_label.setWordWrap(True)
        self.esi_short_spin = QSpinBox()
        self.esi_short_spin.setRange(1, 120)
        self.esi_short_spin.setValue(self.working_config_snapshot.get("esi_short_timeout", config_manager.DEFAULT_CONFIG.get("esi_short_timeout", 5)))
        self.esi_short_spin.setSuffix(" sec")
        self.esi_short_spin.setToolTip("How long to wait for a quick ESI response after auto-lookup before prompting the winner to type !ign in chat.")
        layout.addRow(self.esi_short_label, self.esi_short_spin)

        # Multi-draw toggle
        self.multi_draw_check = QCheckBox("Enable Multi-Draw")
        self.multi_draw_check.setChecked(self.working_config_snapshot.get("multi_draw_enabled", False))
        self.multi_draw_check.setToolTip("If enabled, a confirmed winner is NOT removed from the entry list.\nThis allows them to win again in the same session.\nUsers who time out are always removed.")
        layout.addRow(self.multi_draw_check)

        # Entry type controls
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setFrameShadow(QFrame.Shadow.Sunken); layout.addRow(line)
        self.entry_type_label = QLabel("Entry Method:")
        self.entry_type_combo = QComboBox()
        self.entry_type_combo.addItems(VALID_ENTRY_TYPES)
        self.entry_type_combo.setCurrentText(self.working_config_snapshot.get("entry_condition_type", ENTRY_TYPE_PREDEFINED))
        layout.addRow(self.entry_type_label, self.entry_type_combo)
        self.predefined_command_label = QLabel("Preset Command:")
        self.predefined_command_combo = QComboBox()
        self.predefined_command_combo.addItems(PREDEFINED_COMMANDS)
        current_predefined_cmd = self.working_config_snapshot.get("join_command", config_manager.DEFAULT_CONFIG["join_command"]) 
        if current_predefined_cmd not in PREDEFINED_COMMANDS: current_predefined_cmd = config_manager.DEFAULT_CONFIG["join_command"]
        self.predefined_command_combo.setCurrentText(current_predefined_cmd)
        layout.addRow(self.predefined_command_label, self.predefined_command_combo)
        self.custom_command_label = QLabel("Custom Command:")
        self.custom_command_edit = QLineEdit(self.working_config_snapshot.get("custom_join_command", config_manager.DEFAULT_CONFIG["custom_join_command"]))
        layout.addRow(self.custom_command_label, self.custom_command_edit)
        self.entry_type_combo.currentTextChanged.connect(self._update_entry_control_visibility)
        self._update_entry_control_visibility()
        line1 = QFrame(); line1.setFrameShape(QFrame.Shape.HLine); line1.setFrameShadow(QFrame.Shadow.Sunken); layout.addRow(line1)
        
        # Target Channel - load from user_config.json
        self.target_channel_label = QLabel("Your Twitch Channel:")
        from first_run_setup import load_user_channel
        user_channel = load_user_channel()
        initial_channel = user_channel or self.working_config_snapshot.get("target_channel") or ""
        self.target_channel_edit = QLineEdit(initial_channel)
        self.target_channel_edit.setPlaceholderText("Enter your Twitch channel name")
        self.target_channel_edit.setToolTip("The Twitch channel where RustyBot will monitor for giveaway entries.\nChanging this will update your channel for future sessions.")
        layout.addRow(self.target_channel_label, self.target_channel_edit)
        line2 = QFrame(); line2.setFrameShape(QFrame.Shape.HLine); line2.setFrameShadow(QFrame.Shadow.Sunken); layout.addRow(line2)
        self.enable_test_check = QCheckBox("Allow adding test entries")
        self.enable_test_check.setChecked(self.working_config_snapshot.get("enable_test_entries", False))
        self.add_test_button = QPushButton("Add Test Entries Now")
        self.add_test_button.setEnabled(self.enable_test_check.isChecked())
        self.enable_test_check.toggled.connect(self.add_test_button.setEnabled)
        if self.parent_app and hasattr(self.parent_app, 'add_test_entries'):
            self.add_test_button.clicked.connect(self.parent_app.add_test_entries)
        else:
            self.add_test_button.setEnabled(False)
            print("WARN: OptionsDialog cannot connect Add Test Entries button.")
        layout.addRow(self.enable_test_check)
        layout.addRow(self.add_test_button)

        self.debug_mode_check = QCheckBox("Enable Debug Mode")
        self.debug_mode_check.setChecked(self.working_config_snapshot.get("debug_mode_enabled", False))
        self.debug_mode_check.setToolTip("Show additional debugging information in confirmations and responses.\nUseful for troubleshooting but may clutter the interface.")
        layout.addRow(self.debug_mode_check)
        # --- Configurable chat messages ---
        self.chat_msgs_label = QLabel("Chat Messages (use placeholders: {winner}, {prize}, {timeout})")
        self.chat_msgs_label.setWordWrap(True)
        layout.addRow(self.chat_msgs_label)
        
        # Scale text edit heights based on font multiplier
        font_multiplier = self.working_config_snapshot.get('font_size_multiplier', 1.0)
        
        self.chat_msg_confirmation_edit = QTextEdit()
        self.chat_msg_confirmation_edit.setFixedHeight(int(60 * font_multiplier))
        self.chat_msg_confirmation_edit.setPlainText(self.working_config_snapshot.get("chat_msg_winner_confirmation_needed", config_manager.DEFAULT_CONFIG.get("chat_msg_winner_confirmation_needed", "")))
        conf_label = QLabel("Confirmation Prompt:")
        conf_label.setWordWrap(True)
        layout.addRow(conf_label, self.chat_msg_confirmation_edit)

        self.chat_msg_auto_lookup_attempt_edit = QTextEdit()
        self.chat_msg_auto_lookup_attempt_edit.setFixedHeight(int(50 * font_multiplier))
        self.chat_msg_auto_lookup_attempt_edit.setPlainText(self.working_config_snapshot.get("chat_msg_auto_lookup_attempt", config_manager.DEFAULT_CONFIG.get("chat_msg_auto_lookup_attempt", "")))
        lookup_label = QLabel("Auto Lookup Attempt:")
        lookup_label.setWordWrap(True)
        layout.addRow(lookup_label, self.chat_msg_auto_lookup_attempt_edit)

        self.chat_msg_auto_lookup_failed_edit = QTextEdit()
        self.chat_msg_auto_lookup_failed_edit.setFixedHeight(int(60 * font_multiplier))
        self.chat_msg_auto_lookup_failed_edit.setPlainText(self.working_config_snapshot.get("chat_msg_auto_lookup_failed", config_manager.DEFAULT_CONFIG.get("chat_msg_auto_lookup_failed", "")))
        failed_label = QLabel("Auto Lookup Failed:")
        failed_label.setWordWrap(True)
        layout.addRow(failed_label, self.chat_msg_auto_lookup_failed_edit)

        self.chat_msg_awaiting_ign_edit = QTextEdit()
        self.chat_msg_awaiting_ign_edit.setFixedHeight(int(50 * font_multiplier))
        self.chat_msg_awaiting_ign_edit.setPlainText(self.working_config_snapshot.get("chat_msg_awaiting_ign", config_manager.DEFAULT_CONFIG.get("chat_msg_awaiting_ign", "")))
        awaiting_label = QLabel("Awaiting IGN Prompt:")
        awaiting_label.setWordWrap(True)
        layout.addRow(awaiting_label, self.chat_msg_awaiting_ign_edit)

        line3 = QFrame(); line3.setFrameShape(QFrame.Shape.HLine); line3.setFrameShadow(QFrame.Shadow.Sunken); layout.addRow(line3)
        self.open_data_folder_button = QPushButton("Open Config/Data Folder")
        self.open_data_folder_button.setToolTip("Opens the folder containing config.json and output_entry_method.txt in your file explorer.")
        self.open_data_folder_button.clicked.connect(self._open_data_folder)
        layout.addRow(self.open_data_folder_button)

    def _update_entry_control_visibility(self):
        selected_type = self.entry_type_combo.currentText()
        is_predefined = (selected_type == ENTRY_TYPE_PREDEFINED)
        is_custom = (selected_type == ENTRY_TYPE_CUSTOM)
        self.predefined_command_label.setVisible(is_predefined)
        self.predefined_command_combo.setVisible(is_predefined)
        self.custom_command_label.setVisible(is_custom)
        self.custom_command_edit.setVisible(is_custom)

    def _populate_layout_tab(self):
        layout = QVBoxLayout(self.layout_tab)
        layout_mode_group = QWidget(); layout_mode_hbox = QHBoxLayout(layout_mode_group); layout_mode_hbox.setContentsMargins(0,0,0,0)
        custom_ui_label = QLabel("Customisable UI is currently: ENABLED")
        custom_ui_label.setStyleSheet("font-style: italic; color: #a0a0a0;")
        layout_mode_hbox.addWidget(custom_ui_label)
        layout_mode_hbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.lock_ui_check = QCheckBox("Lock UI Panels")
        self.lock_ui_check.setChecked(self.working_config_snapshot.get("ui_locked", True))
        self.lock_ui_check.setToolTip("When checked, prevents moving or resizing UI panels.\nUncheck to allow adjustments (yellow border appears).")
        self.lock_ui_check.stateChanged.connect(self._on_lock_ui_changed)
        layout_mode_hbox.addWidget(self.lock_ui_check)
        layout.addWidget(layout_mode_group)

        self.layout_actions_group = QWidget(); button_layout = QHBoxLayout(self.layout_actions_group); button_layout.setContentsMargins(0,5,0,5)
        self.save_layout_button = QPushButton("Save Current Panel Layout"); self.save_layout_button.setToolTip("Saves current panel positions/sizes."); self.save_layout_button.clicked.connect(self.emit_save_layout_signal); button_layout.addWidget(self.save_layout_button)
        self.reset_layout_button = QPushButton("Reset Panel Positions"); self.reset_layout_button.setToolTip("Resets panel positions to their default arrangement."); self.reset_layout_button.clicked.connect(self.emit_reset_layout_signal); button_layout.addWidget(self.reset_layout_button)
        self.save_window_geom_button = QPushButton("Save Window Size"); self.save_window_geom_button.setToolTip("Saves the main window's current size and position."); self.save_window_geom_button.clicked.connect(self.save_current_geometry); button_layout.addWidget(self.save_window_geom_button)
        button_layout.addStretch(1); layout.addWidget(self.layout_actions_group)

        font_size_group = QWidget(); font_layout_main = QVBoxLayout(font_size_group); font_layout_main.setContentsMargins(0,10,0,5) # Main VBox for font controls
        font_slider_hbox = QHBoxLayout(); font_slider_hbox.setContentsMargins(0,0,0,0) # HBox for slider and label
        font_label = QLabel("Global Font Size:"); font_label.setMinimumWidth(140); font_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter); font_slider_hbox.addWidget(font_label)
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal); self.font_size_slider.setRange(70, 250); current_multiplier = self.working_config_snapshot.get("font_size_multiplier", 1.0); self.font_size_slider.setValue(int(current_multiplier * 100)); self.font_size_slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed); self.font_size_slider.setToolTip("Adjust the base size of most text elements in the app.\nClick 'Apply Font Size' to see changes immediately, or 'Save' below for permanent change."); font_slider_hbox.addWidget(self.font_size_slider)
        self.font_size_value_label = QLabel(f"{self.font_size_slider.value()}%"); self.font_size_value_label.setMinimumWidth(40); self.font_size_value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter); font_slider_hbox.addWidget(self.font_size_value_label)
        self.font_size_slider.valueChanged.connect(lambda value: self.font_size_value_label.setText(f"{value}%"))
        font_layout_main.addLayout(font_slider_hbox) # Add HBox to VBox

        font_apply_button_hbox = QHBoxLayout(); font_apply_button_hbox.setContentsMargins(0,5,0,0) # HBox for apply button
        font_apply_button_hbox.addStretch(1) # Push button to the right
        self.apply_font_size_button = QPushButton("Apply Font Size")
        self.apply_font_size_button.setToolTip("Applies the current font size setting immediately to the application.\nThis change is temporary until you click 'Save' below.")
        self.apply_font_size_button.clicked.connect(self._on_apply_font_size_button_clicked)
        font_apply_button_hbox.addWidget(self.apply_font_size_button)
        font_layout_main.addLayout(font_apply_button_hbox) # Add apply button HBox to VBox

        layout.addWidget(font_size_group)
        layout.addStretch(1)

    @pyqtSlot()
    def _on_apply_font_size_button_clicked(self):
        new_multiplier_percent = self.font_size_slider.value()
        new_multiplier = round(new_multiplier_percent / 100.0, 2)
        # Update working config immediately so if they hit Save later, it's correct
        self.working_config_snapshot["font_size_multiplier"] = new_multiplier
        self.apply_font_now_signal.emit(new_multiplier)
        QMessageBox.information(self, "Font Size Applied", "Font size applied temporarily.\nClick 'Save' at the bottom of the Options window to make this change permanent.")


    def _on_lock_ui_changed(self, state):
        is_locked = bool(state == Qt.CheckState.Checked.value)
        self.working_config_snapshot["ui_locked"] = is_locked
        self.lock_state_changed.emit(is_locked)

    @pyqtSlot()
    def emit_reset_layout_signal(self):
        reply = QMessageBox.question(self, "Confirm Reset",
                                     "Reset panel positions to their default arrangement?\nThis will clear any custom positions you have saved.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.working_config_snapshot["customisable_ui_enabled"] = True
            self.working_config_snapshot["ui_locked"] = True
            for key in WIDGET_CONFIG_MAP.values():
                self.working_config_snapshot[key] = None

            self.lock_ui_check.setChecked(True)
            self.reset_layout_signal.emit()

            if self.parent_app:
                print("OptionsDialog: Refreshing working_config_snapshot panel geometries from parent_app.config after Reset Panel Positions.")
                for key_config in WIDGET_CONFIG_MAP.values():
                    self.working_config_snapshot[key_config] = self.parent_app.config.get(key_config)

            QMessageBox.information(self, "Layout Reset", "Panel positions reset to default.\nClick 'Save' below to persist this change.")

    @pyqtSlot()
    def emit_save_layout_signal(self):
        self.save_layout_signal.emit()

        if self.parent_app:
            print("OptionsDialog: Refreshing working_config_snapshot panel geometries from parent_app.config after Save Current Panel Layout.")
            for key_config in WIDGET_CONFIG_MAP.values():
                self.working_config_snapshot[key_config] = self.parent_app.config.get(key_config)

        QMessageBox.information(self, "Layout Saved", "Current panel layout temporarily saved.\nClick 'Save' in the main Options window to make it permanent.")


    @pyqtSlot(str, str)
    def update_working_geometry(self, config_key, geo_str):
         if _validate_geometry_string(geo_str): self.working_config_snapshot[config_key] = geo_str
         else: print(f"OptionsDialog: Invalid geometry {geo_str} for {config_key}")

    def _populate_sound_tab(self):
        layout = QVBoxLayout(self.sound_tab)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        self.volume_sliders = {}
        vol_main_layout = QVBoxLayout()
        vol_main_layout.setSpacing(10)
        master_row_layout, self.volume_sliders["master_volume"] = self._create_volume_slider("Master Volume:", self.working_config_snapshot.get("master_volume", 0.75), is_master=True)
        vol_main_layout.addLayout(master_row_layout)
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setFrameShadow(QFrame.Shadow.Sunken); vol_main_layout.addWidget(line)
        volume_categories = {"AI Voice": "ai_voice_volume", "Warning Sounds": "warning_sounds_volume", "Hacking Background": "hacking_background_volume", "Countdown": "countdown_volume"}
        for label_text, config_key in volume_categories.items():
            default_value = config_manager.DEFAULT_CONFIG.get(config_key, 0.5)
            row_layout, slider_tuple = self._create_volume_slider(f"{label_text}:", self.working_config_snapshot.get(config_key, default_value))
            self.volume_sliders[config_key] = slider_tuple
            vol_main_layout.addLayout(row_layout)
        layout.addLayout(vol_main_layout)
        layout.addStretch(1)


    def _populate_draw_style_tab(self):
        layout = QFormLayout(self.draw_style_tab)
        layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        self.anim_type_combo = QComboBox()
        self.ANIMATION_TYPES_OPTIONS = config_manager.VALID_ANIMATION_TYPES
        self.anim_type_combo.addItems(self.ANIMATION_TYPES_OPTIONS)
        current_anim_type = self.working_config_snapshot.get("animation_type", config_manager.DEFAULT_CONFIG["animation_type"])
        if current_anim_type not in self.ANIMATION_TYPES_OPTIONS: current_anim_type = config_manager.DEFAULT_CONFIG["animation_type"]
        self.anim_type_combo.setCurrentText(current_anim_type)
        layout.addRow("Draw Style Type:", self.anim_type_combo)
        self.anim_box_speed_combo = QComboBox(); self.BOX_SPEED_OPTIONS = ["Normal", "Slow", "Very Slow"]; self.anim_box_speed_combo.addItems(self.BOX_SPEED_OPTIONS); self.anim_box_speed_combo.setCurrentText(self.working_config_snapshot.get("animation_box_speed", "Normal")); self.hacking_speed_label = QLabel("Hacking Reveal Speed:"); self.hacking_speed_label.setWordWrap(True); layout.addRow(self.hacking_speed_label, self.anim_box_speed_combo)

        self.anim_list_duration_combo = None
        self.list_duration_label = None

        self.anim_trig_speed_combo = QComboBox(); self.TRIG_SPEED_OPTIONS = VALID_TRIG_SPEEDS; self.anim_trig_speed_combo.addItems(self.TRIG_SPEED_OPTIONS); self.anim_trig_speed_combo.setCurrentText(self.working_config_snapshot.get("animation_trig_speed", TRIG_SPEED_NORMAL)); self.trig_speed_label = QLabel("Triglavian Reveal Speed:"); self.trig_speed_label.setWordWrap(True); layout.addRow(self.trig_speed_label, self.anim_trig_speed_combo)
        self.anim_node_path_speed_combo = QComboBox(); self.NODE_PATH_SPEED_OPTIONS = VALID_NODE_PATH_SPEEDS; self.anim_node_path_speed_combo.addItems(self.NODE_PATH_SPEED_OPTIONS); self.anim_node_path_speed_combo.setCurrentText(self.working_config_snapshot.get("animation_node_path_speed", NODE_PATH_SPEED_NORMAL)); self.node_path_speed_label = QLabel("Node Path Reveal Speed:"); self.node_path_speed_label.setWordWrap(True); layout.addRow(self.node_path_speed_label, self.anim_node_path_speed_combo)
        self.anim_trig_conduit_speed_combo = QComboBox(); self.TRIG_CONDUIT_SPEED_OPTIONS = VALID_TRIG_CONDUIT_SPEEDS; self.anim_trig_conduit_speed_combo.addItems(self.TRIG_CONDUIT_SPEED_OPTIONS); self.anim_trig_conduit_speed_combo.setCurrentText(self.working_config_snapshot.get("animation_trig_conduit_speed", TRIG_CONDUIT_SPEED_NORMAL)); self.trig_conduit_speed_label = QLabel("Trig Conduit Pulse Speed:"); self.trig_conduit_speed_label.setWordWrap(True); layout.addRow(self.trig_conduit_speed_label, self.anim_trig_conduit_speed_combo)
        self.trig_code_length_label = QLabel("Trig Code Length (5-12):"); self.trig_code_length_label.setWordWrap(True); self.trig_code_length_spin = QSpinBox(); self.trig_code_length_spin.setRange(5, 12); self.trig_code_length_spin.setValue(self.working_config_snapshot.get("animation_trig_code_length", config_manager.DEFAULT_CONFIG["animation_trig_code_length"])); self.trig_code_length_spin.setToolTip("Number of characters in the generated Triglavian code."); layout.addRow(self.trig_code_length_label, self.trig_code_length_spin)
        self.trig_code_reveal_speed_label = QLabel("Trig Code Reveal Speed:"); self.trig_code_reveal_speed_label.setWordWrap(True); self.trig_code_reveal_speed_combo = QComboBox(); self.TRIG_CODE_REVEAL_SPEED_OPTIONS = VALID_TRIG_CODE_REVEAL_SPEEDS; self.trig_code_reveal_speed_combo.addItems(self.TRIG_CODE_REVEAL_SPEED_OPTIONS); self.trig_code_reveal_speed_combo.setCurrentText(self.working_config_snapshot.get("animation_trig_code_reveal_speed", TRIG_CODE_REVEAL_SPEED_NORMAL)); self.trig_code_reveal_speed_combo.setToolTip("Speed of letter-by-letter reveal and participant elimination."); layout.addRow(self.trig_code_reveal_speed_label, self.trig_code_reveal_speed_combo)
        self.trig_code_char_set_label = QLabel("Trig Code Char Set:"); self.trig_code_char_set_label.setWordWrap(True); default_charset = config_manager.DEFAULT_CONFIG["animation_trig_code_char_set"]; self.trig_code_char_set_edit = QLineEdit(self.working_config_snapshot.get("animation_trig_code_char_set", default_charset)); self.trig_code_char_set_edit.setToolTip("Characters used for Triglavian Code Reveal.\nDefault includes A-Z, 0-9, and Triglavian Glyphs."); self.trig_code_char_set_edit.setMinimumWidth(250); layout.addRow(self.trig_code_char_set_label, self.trig_code_char_set_edit)
        self.trig_code_finalist_count_label = QLabel("Trig Code Finalists (2-20):"); self.trig_code_finalist_count_label.setWordWrap(True); self.trig_code_finalist_count_spin = QSpinBox(); self.trig_code_finalist_count_spin.setRange(2, 20); self.trig_code_finalist_count_spin.setValue(self.working_config_snapshot.get("animation_trig_code_finalist_count", config_manager.DEFAULT_CONFIG["animation_trig_code_finalist_count"])); self.trig_code_finalist_count_spin.setToolTip("Number of participants to keep visible on screen during the final stages of code reveal."); layout.addRow(self.trig_code_finalist_count_label, self.trig_code_finalist_count_spin)
        self.anim_type_combo.currentTextChanged.connect(self._update_anim_control_visibility)
        self._update_anim_control_visibility()

    def _populate_prizes_tab(self):
        layout = QVBoxLayout(self.prizes_tab)
        layout.setSpacing(12)
        layout.setContentsMargins(10, 10, 10, 10)

        prize_options_group = QGroupBox("Prize Options for Poll / Streamer Choice")
        prize_options_layout = QVBoxLayout(prize_options_group)
        prize_options_layout.setSpacing(8)
        prize_options_layout.setContentsMargins(10, 15, 10, 10)
        add_prize_layout = QHBoxLayout()
        add_prize_layout.setSpacing(5)
        self.new_prize_edit = QLineEdit()
        self.new_prize_edit.setPlaceholderText("Enter prize (e.g., Item Name (Donator))")
        self.new_prize_edit.setMaxLength(100)
        self.add_prize_button = QPushButton("Add Prize")
        self.add_prize_button.clicked.connect(self._add_prize_option)
        self.new_prize_edit.returnPressed.connect(self.add_prize_button.click)
        add_prize_layout.addWidget(self.new_prize_edit, 1)
        add_prize_layout.addWidget(self.add_prize_button)
        prize_options_layout.addLayout(add_prize_layout)
        self.prize_options_list_widget = QListWidget()
        self.prize_options_list_widget.setToolTip("List of prize options for poll/streamer selection. Select to edit or remove.")
        # Scale list height based on font multiplier
        font_multiplier = self.working_config_snapshot.get('font_size_multiplier', 1.0)
        self.prize_options_list_widget.setMinimumHeight(int(120 * font_multiplier))
        self.prize_options_list_widget.setMaximumHeight(int(200 * font_multiplier))

        self.edit_prize_button = QPushButton("Edit Selected")
        self.remove_prize_button = QPushButton("Remove Selected")
        self.import_prizes_button = QPushButton("Import from File")
        self.update_prizes_button = QPushButton("Update from File")
        self.clear_prizes_button = QPushButton("Clear All")

        self._load_prize_options_to_list_widget()
        self.prize_options_list_widget.itemDoubleClicked.connect(self._edit_prize_option)
        prize_options_layout.addWidget(self.prize_options_list_widget)
        
        prize_options_info = QLabel("<small><i>Double-click to edit. Format: Prize Name (Donator Name)</i></small>")
        prize_options_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prize_options_info.setStyleSheet("color: #a0a0a0; margin-top: 2px; margin-bottom: 5px;")
        prize_options_layout.addWidget(prize_options_info)

        # Button layout - organized in rows
        prize_buttons_container = QWidget()
        prize_buttons_vlayout = QVBoxLayout(prize_buttons_container)
        prize_buttons_vlayout.setContentsMargins(0, 0, 0, 0)
        prize_buttons_vlayout.setSpacing(5)
        
        # First row: Edit and management buttons
        prize_list_buttons_row1 = QHBoxLayout()
        self.edit_prize_button.clicked.connect(self._edit_prize_option)
        self.remove_prize_button.clicked.connect(self._remove_prize_option)
        self.clear_prizes_button.clicked.connect(self._clear_prize_options_list)
        prize_list_buttons_row1.addWidget(self.edit_prize_button)
        prize_list_buttons_row1.addWidget(self.remove_prize_button)
        prize_list_buttons_row1.addWidget(self.clear_prizes_button)
        prize_list_buttons_row1.addStretch(1)
        
        # Second row: Import/Update buttons
        prize_list_buttons_row2 = QHBoxLayout()
        self.import_prizes_button.setToolTip("Import prizes from a .txt file, replacing the current list.")
        self.import_prizes_button.clicked.connect(self._import_prizes_from_file)
        self.update_prizes_button.setToolTip("Add new prizes from a .txt file, skipping any duplicates.")
        self.update_prizes_button.clicked.connect(self._update_prizes_from_file)
        prize_list_buttons_row2.addWidget(self.import_prizes_button)
        prize_list_buttons_row2.addWidget(self.update_prizes_button)
        prize_list_buttons_row2.addStretch(1)
        
        prize_buttons_vlayout.addLayout(prize_list_buttons_row1)
        prize_buttons_vlayout.addLayout(prize_list_buttons_row2)
        prize_options_layout.addWidget(prize_buttons_container)
        layout.addWidget(prize_options_group)

        common_prizes_group = QGroupBox("Common Giveaway Prizes")
        common_prizes_layout = QVBoxLayout(common_prizes_group)
        common_prizes_layout.setSpacing(8)
        common_prizes_layout.setContentsMargins(10, 15, 10, 10)
        add_common_prize_layout = QHBoxLayout()
        add_common_prize_layout.setSpacing(5)
        self.new_common_prize_edit = QLineEdit()
        self.new_common_prize_edit.setPlaceholderText("Enter common prize (e.g., PLEX (CCP))")
        self.new_common_prize_edit.setMaxLength(100)
        self.add_common_prize_button = QPushButton("Add Common Prize")
        self.add_common_prize_button.clicked.connect(self._add_common_prize_option)
        self.new_common_prize_edit.returnPressed.connect(self.add_common_prize_button.click)
        add_common_prize_layout.addWidget(self.new_common_prize_edit, 1)
        add_common_prize_layout.addWidget(self.add_common_prize_button)
        common_prizes_layout.addLayout(add_common_prize_layout)
        self.common_prizes_list_widget = QListWidget()
        self.common_prizes_list_widget.setToolTip("List of common prizes. Select to edit or remove.")
        # Scale list height based on font multiplier
        font_multiplier = self.working_config_snapshot.get('font_size_multiplier', 1.0)
        self.common_prizes_list_widget.setMinimumHeight(int(80 * font_multiplier))
        self.common_prizes_list_widget.setMaximumHeight(int(150 * font_multiplier))

        self.edit_common_prize_button = QPushButton("Edit Selected")
        self.remove_common_prize_button = QPushButton("Remove Selected")
        self.import_common_prizes_button = QPushButton("Import from File")
        self.update_common_prizes_button = QPushButton("Update from File")
        self.clear_common_prizes_button = QPushButton("Clear All")

        self._load_common_prizes_to_list_widget()
        self.common_prizes_list_widget.itemDoubleClicked.connect(self._edit_common_prize_option)
        common_prizes_layout.addWidget(self.common_prizes_list_widget)
        
        common_prizes_info = QLabel("<small><i>Double-click to edit. Format: Prize Name (Donator Name)</i></small>")
        common_prizes_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        common_prizes_info.setStyleSheet("color: #a0a0a0; margin-top: 2px; margin-bottom: 5px;")
        common_prizes_layout.addWidget(common_prizes_info)

        # Button layout - organized in rows
        common_buttons_container = QWidget()
        common_buttons_vlayout = QVBoxLayout(common_buttons_container)
        common_buttons_vlayout.setContentsMargins(0, 0, 0, 0)
        common_buttons_vlayout.setSpacing(5)
        
        # First row: Edit and management buttons
        common_prize_buttons_row1 = QHBoxLayout()
        self.edit_common_prize_button.clicked.connect(self._edit_common_prize_option)
        self.remove_common_prize_button.clicked.connect(self._remove_common_prize_option)
        self.clear_common_prizes_button.clicked.connect(self._clear_common_prizes_list)
        common_prize_buttons_row1.addWidget(self.edit_common_prize_button)
        common_prize_buttons_row1.addWidget(self.remove_common_prize_button)
        common_prize_buttons_row1.addWidget(self.clear_common_prizes_button)
        common_prize_buttons_row1.addStretch(1)
        
        # Second row: Import/Update buttons
        common_prize_buttons_row2 = QHBoxLayout()
        self.import_common_prizes_button.setToolTip("Import common prizes from a .txt file, replacing the current list.")
        self.import_common_prizes_button.clicked.connect(self._import_common_prizes_from_file)
        self.update_common_prizes_button.setToolTip("Add new common prizes from a .txt file, skipping any duplicates.")
        self.update_common_prizes_button.clicked.connect(self._update_common_prizes_from_file)
        common_prize_buttons_row2.addWidget(self.import_common_prizes_button)
        common_prize_buttons_row2.addWidget(self.update_common_prizes_button)
        common_prize_buttons_row2.addStretch(1)
        
        common_buttons_vlayout.addLayout(common_prize_buttons_row1)
        common_buttons_vlayout.addLayout(common_prize_buttons_row2)
        common_prizes_layout.addWidget(common_buttons_container)
        layout.addWidget(common_prizes_group)

        poll_settings_group = QGroupBox("Poll Settings (if 'Twitch Chat Poll' mode is active)")
        poll_settings_form_layout = QFormLayout(poll_settings_group)
        poll_settings_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        poll_settings_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        poll_settings_form_layout.setVerticalSpacing(8)
        poll_settings_form_layout.setContentsMargins(10, 15, 10, 10)
        
        self.poll_duration_spin = QSpinBox()
        self.poll_duration_spin.setRange(10, 300)
        self.poll_duration_spin.setValue(self.working_config_snapshot.get("poll_duration", 30))
        self.poll_duration_spin.setSuffix(" sec")
        self.poll_duration_spin.setToolTip("Duration for Twitch chat to vote on the prize if 'Twitch Chat Poll' mode is active.")
        poll_label = QLabel("Poll Duration:")
        poll_label.setWordWrap(True)
        poll_settings_form_layout.addRow(poll_label, self.poll_duration_spin)
        layout.addWidget(poll_settings_group)

        layout.addStretch(1)
        self._update_prize_add_button_state()
        self._update_common_prize_add_button_state()

    def _load_prize_options_to_list_widget(self):
        self.prize_options_list_widget.clear()
        current_prizes = self.working_config_snapshot.get("prize_options", [])
        for prize_text in current_prizes:
            item = QListWidgetItem(prize_text)
            self.prize_options_list_widget.addItem(item)
        self._update_prize_add_button_state()

    def _add_prize_option(self):
        prize_text = self.new_prize_edit.text().strip()
        if prize_text:
            if len(prize_text) > 100:
                QMessageBox.warning(self, "Prize Too Long", "Prize description cannot exceed 100 characters.")
                return
            items = [self.prize_options_list_widget.item(i).text() for i in range(self.prize_options_list_widget.count())]
            if prize_text in items:
                QMessageBox.information(self, "Duplicate Prize", "This prize is already in the list.")
                return
            item = QListWidgetItem(prize_text)
            self.prize_options_list_widget.addItem(item)
            self.new_prize_edit.clear()
            self._update_prize_add_button_state()
        else:
            QMessageBox.warning(self, "Empty Prize", "Please enter a description for the prize.")

    def _edit_prize_option(self):
        self._edit_list_item_generic(self.prize_options_list_widget, "Prize", 100)

    def _remove_prize_option(self):
        self._remove_list_item_generic(self.prize_options_list_widget, "Prize Options", self._update_prize_add_button_state)

    def _clear_prize_options_list(self):
        self._clear_list_generic(self.prize_options_list_widget, "prize options", self._update_prize_add_button_state)

    def _update_prize_add_button_state(self):
        self.add_prize_button.setEnabled(True)
        count = self.prize_options_list_widget.count()
        self.edit_prize_button.setEnabled(count > 0)
        self.remove_prize_button.setEnabled(count > 0)
        self.clear_prizes_button.setEnabled(count > 0)
        self.import_prizes_button.setEnabled(True)
        self.update_prizes_button.setEnabled(True)

    def _import_prizes_from_file(self):
        self._import_items_from_file_generic(self.prize_options_list_widget, "Prizes", 9999, self._update_prize_add_button_state, 100)
        
    def _update_prizes_from_file(self):
        self._update_items_from_file_generic(self.prize_options_list_widget, "Prizes", 9999, self._update_prize_add_button_state, 100)

    def _load_common_prizes_to_list_widget(self):
        self.common_prizes_list_widget.clear()
        current_common_prizes = self.working_config_snapshot.get("common_prizes_list", [])
        for prize_text in current_common_prizes:
            item = QListWidgetItem(prize_text)
            self.common_prizes_list_widget.addItem(item)
        self._update_common_prize_add_button_state()

    def _add_common_prize_option(self):
        prize_text = self.new_common_prize_edit.text().strip()
        if prize_text:
            if len(prize_text) > 100:
                QMessageBox.warning(self, "Common Prize Too Long", "Common prize description cannot exceed 100 characters.")
                return
            items = [self.common_prizes_list_widget.item(i).text() for i in range(self.common_prizes_list_widget.count())]
            if prize_text in items:
                QMessageBox.information(self, "Duplicate Common Prize", "This common prize is already in the list.")
                return
            item = QListWidgetItem(prize_text)
            self.common_prizes_list_widget.addItem(item)
            self.new_common_prize_edit.clear()
            self._update_common_prize_add_button_state()
        else:
            QMessageBox.warning(self, "Empty Common Prize", "Please enter a description for the common prize.")

    def _edit_common_prize_option(self):
        self._edit_list_item_generic(self.common_prizes_list_widget, "Common Prize", 100)

    def _remove_common_prize_option(self):
        self._remove_list_item_generic(self.common_prizes_list_widget, "Common Prizes", self._update_common_prize_add_button_state)

    def _clear_common_prizes_list(self):
        self._clear_list_generic(self.common_prizes_list_widget, "common prizes", self._update_common_prize_add_button_state)

    def _update_common_prize_add_button_state(self):
        self.add_common_prize_button.setEnabled(True)
        count = self.common_prizes_list_widget.count()
        self.edit_common_prize_button.setEnabled(count > 0)
        self.remove_common_prize_button.setEnabled(count > 0)
        self.clear_common_prizes_button.setEnabled(count > 0)
        self.import_common_prizes_button.setEnabled(True)
        self.update_common_prizes_button.setEnabled(True)

    def _import_common_prizes_from_file(self):
        self._import_items_from_file_generic(self.common_prizes_list_widget, "Common Prizes", 9999, self._update_common_prize_add_button_state, 100)

    def _update_common_prizes_from_file(self):
        self._update_items_from_file_generic(self.common_prizes_list_widget, "Common Prizes", 9999, self._update_common_prize_add_button_state, 100)

    def _edit_list_item_generic(self, list_widget: QListWidget, item_type_name: str, max_length: int):
        selected_item = list_widget.currentItem()
        if not selected_item: QMessageBox.information(self, f"No {item_type_name} Selected", f"Please select a {item_type_name.lower()} from the list to edit."); return
        dialog = QDialog(self); dialog.setWindowTitle(f"Edit {item_type_name}"); layout = QVBoxLayout(dialog)
        edit_label = QLabel(f"Editing: {selected_item.text()}"); edit_line = QLineEdit(selected_item.text()); edit_line.setMaxLength(max_length)
        button_box_edit = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        def accept_edit():
            new_text = edit_line.text().strip()
            if new_text:
                if len(new_text) > max_length: QMessageBox.warning(self, f"{item_type_name} Too Long", f"{item_type_name} description cannot exceed {max_length} characters."); return
                items = []
                for i in range(list_widget.count()):
                    if list_widget.item(i) != selected_item: items.append(list_widget.item(i).text())
                if new_text in items: QMessageBox.information(self, f"Duplicate {item_type_name}", f"This {item_type_name.lower()} description is already in the list."); return
                selected_item.setText(new_text); dialog.accept()
            else: QMessageBox.warning(self, f"Empty {item_type_name}", f"{item_type_name} description cannot be empty.")
        button_box_edit.accepted.connect(accept_edit); button_box_edit.rejected.connect(dialog.reject)
        layout.addWidget(edit_label); layout.addWidget(edit_line); layout.addWidget(button_box_edit); dialog.exec()

    def _remove_list_item_generic(self, list_widget: QListWidget, list_name_for_messages: str, update_button_state_func: callable):
        selected_item = list_widget.currentItem()
        if selected_item: row = list_widget.row(selected_item); list_widget.takeItem(row); update_button_state_func()
        else: QMessageBox.information(self, f"No Item Selected", f"Please select an item from the {list_name_for_messages} list to remove.")
        
    def _clear_list_generic(self, list_widget: QListWidget, list_name_for_messages: str, update_button_state_func: callable):
        if list_widget.count() == 0:
            return
        reply = QMessageBox.question(self, "Confirm Clear",
                                     f"Are you sure you want to clear the entire {list_name_for_messages} list?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            list_widget.clear()
            update_button_state_func()

    def _import_items_from_file_generic(self, list_widget: QListWidget, item_type_plural: str, max_items: int, update_button_state_func: callable, item_max_length: int):
        file_name, _ = QFileDialog.getOpenFileName(self, f"Import {item_type_plural}", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f: items_from_file = [line.strip() for line in f if line.strip()]
                if not items_from_file: QMessageBox.information(self, "Empty File", "The selected file is empty or contains no valid lines."); return
                
                list_widget.clear() # Clear the list for a fresh import
                
                imported_count, skipped_length, skipped_limit = 0, 0, 0
                
                for item_text in items_from_file:
                    if list_widget.count() >= max_items:
                        skipped_limit += 1; continue
                    if len(item_text) > item_max_length: skipped_length += 1; continue
                    item = QListWidgetItem(item_text); list_widget.addItem(item); imported_count += 1
                
                update_button_state_func()
                summary_message = f"Imported {imported_count} {item_type_plural.lower()}.\n"
                if skipped_length > 0: summary_message += f"Skipped {skipped_length} item(s) longer than {item_max_length} characters.\n"
                if skipped_limit > 0: summary_message += f"Skipped {skipped_limit} item(s) due to reaching the {max_items} item limit.\n"
                QMessageBox.information(self, "Import Complete", summary_message.strip())
            except Exception as e: QMessageBox.critical(self, "Import Error", f"Could not import {item_type_plural.lower()}: {e}"); traceback.print_exc()

    def _update_items_from_file_generic(self, list_widget: QListWidget, item_type_plural: str, max_items: int, update_button_state_func: callable, item_max_length: int):
        file_name, _ = QFileDialog.getOpenFileName(self, f"Update {item_type_plural} From File", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f: items_from_file = {line.strip() for line in f if line.strip()}
                if not items_from_file:
                    QMessageBox.information(self, "Empty File", "The selected file is empty or contains no valid lines."); return
                
                existing_items = {list_widget.item(i).text() for i in range(list_widget.count())}
                new_items = items_from_file - existing_items
                
                added_count, skipped_length, skipped_limit = 0, 0, 0
                
                for item_text in sorted(list(new_items)): # Sort for consistent order
                    if list_widget.count() >= max_items:
                        skipped_limit += 1; continue
                    if len(item_text) > item_max_length:
                        skipped_length += 1; continue
                    item = QListWidgetItem(item_text)
                    list_widget.addItem(item)
                    added_count += 1
                
                update_button_state_func()
                summary_message = f"Update complete.\n\nAdded {added_count} new {item_type_plural.lower()}.\n"
                skipped_duplicates = len(items_from_file) - len(new_items)
                if skipped_duplicates > 0: summary_message += f"Skipped {skipped_duplicates} duplicate item(s).\n"
                if skipped_length > 0: summary_message += f"Skipped {skipped_length} new item(s) longer than {item_max_length} characters.\n"
                if skipped_limit > 0: summary_message += f"Skipped {skipped_limit} new item(s) due to reaching the {max_items} item limit.\n"
                QMessageBox.information(self, "Update Complete", summary_message.strip())

            except Exception as e:
                QMessageBox.critical(self, "Update Error", f"Could not update {item_type_plural.lower()}: {e}"); traceback.print_exc()


    def _populate_analytics_tab(self):
        main_layout = QVBoxLayout(self.analytics_tab)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        ga_group = QGroupBox("Google Analytics (Optional)")
        ga_layout = QVBoxLayout(ga_group)
        ga_layout.setSpacing(10)
        ga_layout.setContentsMargins(15, 20, 15, 15)
        
        self.ga_enabled_check = QCheckBox("Enable Google Analytics")
        self.ga_enabled_check.setChecked(self.working_config_snapshot.get("google_analytics_enabled", False))
        self.ga_enabled_check.setToolTip("Allow the application to send anonymous usage data (like draw entries and app launches)\nto Google Analytics. This helps the developer understand feature usage and improve the app.\nNo personal Twitch information beyond entry counts is sent without explicit !ign usage.")
        ga_layout.addWidget(self.ga_enabled_check)
        
        # Create form layout for fields
        ga_form_layout = QFormLayout()
        ga_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        ga_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        ga_form_layout.setVerticalSpacing(10)
        ga_form_layout.setContentsMargins(0, 5, 0, 0)
        
        self.ga_measurement_id_edit = QLineEdit(self.working_config_snapshot.get("ga_measurement_id", ""))
        self.ga_measurement_id_edit.setPlaceholderText("G-XXXXXXXXXX")
        self.ga_measurement_id_edit.setToolTip("Your GA4 Measurement ID.")
        ga_form_layout.addRow("GA Measurement ID:", self.ga_measurement_id_edit)
        
        self.ga_api_secret_edit = QLineEdit(self.working_config_snapshot.get("ga_api_secret", ""))
        self.ga_api_secret_edit.setPlaceholderText("Enter your API Secret")
        self.ga_api_secret_edit.setToolTip("Your GA4 Measurement Protocol API Secret.")
        self.ga_api_secret_edit.setEchoMode(QLineEdit.EchoMode.Password)
        ga_form_layout.addRow("GA API Secret:", self.ga_api_secret_edit)
        
        ga_layout.addLayout(ga_form_layout)
        
        # Add spacer before privacy notice
        ga_layout.addSpacing(15)
        
        privacy_notice = QLabel("<small><i>By enabling Google Analytics, you agree to send anonymous usage data. This data helps improve the application. No personally identifiable Twitch information is sent automatically. A unique, anonymous Client ID will be generated and stored locally in your config.json.</i></small>")
        privacy_notice.setWordWrap(True)
        privacy_notice.setMinimumHeight(70)
        privacy_notice.setContentsMargins(0, 10, 0, 5)
        privacy_notice.setStyleSheet("color: #a0a0a0; padding: 10px 5px;")
        ga_layout.addWidget(privacy_notice)
        self.ga_enabled_check.toggled.connect(self._update_ga_controls_visibility)
        main_layout.addWidget(ga_group)
        
        remote_log_group = QGroupBox("Remote Logging (Advanced/Developer)")
        remote_log_layout = QVBoxLayout(remote_log_group)
        remote_log_layout.setSpacing(10)
        remote_log_layout.setContentsMargins(15, 20, 15, 15)
        
        self.remote_log_enabled_check = QCheckBox("Enable Remote Logging")
        self.remote_log_enabled_check.setChecked(self.working_config_snapshot.get("remote_logging_enabled", False))
        self.remote_log_enabled_check.setToolTip("Enable sending of specific event logs to a remote server (for debugging or statistics).")
        remote_log_layout.addWidget(self.remote_log_enabled_check)
        
        # Create form layout for fields
        remote_log_form_layout = QFormLayout()
        remote_log_form_layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        remote_log_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        remote_log_form_layout.setVerticalSpacing(10)
        remote_log_form_layout.setContentsMargins(0, 5, 0, 0)
        
        self.remote_log_url_edit = QLineEdit(self.working_config_snapshot.get("remote_logging_url", ""))
        self.remote_log_url_edit.setPlaceholderText("https://your-logging-endpoint.com/api/log")
        remote_log_form_layout.addRow("Logging URL:", self.remote_log_url_edit)
        
        self.remote_log_api_key_edit = QLineEdit(self.working_config_snapshot.get("remote_logging_api_key", ""))
        self.remote_log_api_key_edit.setPlaceholderText("Optional API Key")
        self.remote_log_api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        remote_log_form_layout.addRow("Logging API Key:", self.remote_log_api_key_edit)
        
        remote_log_layout.addLayout(remote_log_form_layout)
        
        self.remote_log_enabled_check.toggled.connect(self._update_remote_log_controls_visibility)
        main_layout.addWidget(remote_log_group)
        main_layout.addStretch(1)
        self._update_ga_controls_visibility(); self._update_remote_log_controls_visibility()

    def _update_ga_controls_visibility(self, checked=None):
        is_enabled = self.ga_enabled_check.isChecked() if checked is None else checked
        self.ga_measurement_id_edit.setEnabled(is_enabled)
        self.ga_api_secret_edit.setEnabled(is_enabled)

    def _update_remote_log_controls_visibility(self, checked=None):
        is_enabled = self.remote_log_enabled_check.isChecked() if checked is None else checked
        self.remote_log_url_edit.setEnabled(is_enabled)
        self.remote_log_api_key_edit.setEnabled(is_enabled)

    def _update_anim_control_visibility(self):
         selected_type = self.anim_type_combo.currentText()
         is_hacking = selected_type == ANIM_TYPE_HACKING
         is_list = False
         is_trig = selected_type == ANIM_TYPE_TRIGLAVIAN
         is_node_path = selected_type == ANIM_TYPE_NODE_PATH
         is_trig_conduit = selected_type == ANIM_TYPE_TRIG_CONDUIT
         is_trig_code_reveal = selected_type == ANIM_TYPE_TRIG_CODE_REVEAL
         is_random_tech = selected_type == ANIM_TYPE_RANDOM_TECH

         self.hacking_speed_label.setVisible(is_hacking and not is_random_tech); self.anim_box_speed_combo.setVisible(is_hacking and not is_random_tech)

         if self.list_duration_label: self.list_duration_label.setVisible(False) # Keep hidden
         if self.anim_list_duration_combo: self.anim_list_duration_combo.setVisible(False) # Keep hidden

         self.trig_speed_label.setVisible(is_trig and not is_random_tech); self.anim_trig_speed_combo.setVisible(is_trig and not is_random_tech)
         self.node_path_speed_label.setVisible(is_node_path and not is_random_tech); self.anim_node_path_speed_combo.setVisible(is_node_path and not is_random_tech)
         self.trig_conduit_speed_label.setVisible(is_trig_conduit and not is_random_tech); self.anim_trig_conduit_speed_combo.setVisible(is_trig_conduit and not is_random_tech)
         show_trig_code_options = is_trig_code_reveal and not is_random_tech
         self.trig_code_length_label.setVisible(show_trig_code_options); self.trig_code_length_spin.setVisible(show_trig_code_options)
         self.trig_code_reveal_speed_label.setVisible(show_trig_code_options); self.trig_code_reveal_speed_combo.setVisible(show_trig_code_options)
         self.trig_code_char_set_label.setVisible(show_trig_code_options); self.trig_code_char_set_edit.setVisible(show_trig_code_options)
         self.trig_code_finalist_count_label.setVisible(show_trig_code_options); self.trig_code_finalist_count_spin.setVisible(show_trig_code_options)

    def _create_volume_slider(self, label_text, initial_value, is_master=False):
        slider = QSlider(Qt.Orientation.Horizontal); slider.setRange(0, 100); slider.setValue(int(initial_value * 100)); slider.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        value_label = QLabel(f"{slider.value()}%"); value_label.setMinimumWidth(40); value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        slider.valueChanged.connect(lambda value, lbl=value_label: lbl.setText(f"{value}%"))
        row_layout = QHBoxLayout(); label_widget = QLabel(label_text); label_widget.setMinimumWidth(140); label_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row_layout.addWidget(label_widget); row_layout.addWidget(slider); row_layout.addWidget(value_label)
        return row_layout, (slider, value_label)

    def save_current_geometry(self):
        if self.parent_app and self.parent_app.isVisible(): geom = self.parent_app.geometry(); geo_str = f"{geom.width()}x{geom.height()}+{geom.x()}+{geom.y()}"; self.working_config_snapshot["window_geometry"] = geo_str; print(f"Options: Set window geometry in snapshot: {geo_str}"); QMessageBox.information(self, "Geometry Saved", f"Window size saved:\n{geo_str}")
        else: QMessageBox.warning(self, "Error", "Cannot get geometry, main window not available.")

    @pyqtSlot()
    def _open_data_folder(self):
        try:
            data_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
            if not data_dir_str:
                data_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation)
                if data_dir_str: data_dir = Path(data_dir_str) / ORG_NAME / APP_NAME
                else: QMessageBox.warning(self, "Error", "Could not determine the application data directory path."); return
            else: data_dir = Path(data_dir_str)
            folder_to_open = data_dir
            if not data_dir.exists():
                parent_dir = data_dir.parent
                if parent_dir.exists() and parent_dir.is_dir(): folder_to_open = parent_dir
                else: QMessageBox.information(self, "Info", f"Data directory ({data_dir}) hasn't been created yet. It will be created when settings are saved."); return
            folder_url = QUrl.fromLocalFile(str(folder_to_open.resolve())); print(f"Attempting to open data folder: {folder_url.toString()}")
            if not QDesktopServices.openUrl(folder_url):
                QMessageBox.warning(self, "Error", f"Could not automatically open the folder:\n{folder_to_open}\n\nPlease navigate there manually.")
                if sys.platform.startswith('linux'):
                    try: subprocess.run(['xdg-open', str(folder_to_open.resolve())], check=True)
                    except Exception as linux_e: print(f"xdg-open fallback failed: {linux_e}"); QMessageBox.warning(self, "Error", f"Could not open the folder using fallback:\n{folder_to_open}\n\nPlease navigate there manually.")
        except Exception as e: print(f"Error opening data folder: {e}"); traceback.print_exc(); QMessageBox.critical(self, "Error", f"An unexpected error occurred while trying to open the data folder: {e}")

    def accept(self):
        temp_config_from_dialog = {}
        print("OptionsDialog.accept(): Starting to gather values...")
        try:
            temp_config_from_dialog["confirmation_timeout"] = self.confirm_timeout_spin.value()
            temp_config_from_dialog["eve_response_timeout"] = self.eve_timeout_spin.value()
            temp_config_from_dialog["multi_draw_enabled"] = self.multi_draw_check.isChecked()
            temp_config_from_dialog["entry_condition_type"] = self.entry_type_combo.currentText()
            temp_config_from_dialog["join_command"] = self.predefined_command_combo.currentText()
            temp_config_from_dialog["custom_join_command"] = self.custom_command_edit.text()
            channel_text = self.target_channel_edit.text().strip(); validated_channel = None
            if channel_text:
                if ' ' in channel_text or not re.match(r'^[a-zA-Z0-9_]+$', channel_text): 
                    raise ValueError("Invalid character(s) in channel name. Only A-Z, 0-9, _ allowed.")
                validated_channel = channel_text.lower()
                
                # Save to user_config.json for persistence across sessions
                from first_run_setup import update_user_channel
                update_user_channel(validated_channel)
                print(f"✅ Updated user channel to: {validated_channel}")
            
            temp_config_from_dialog["target_channel"] = validated_channel
            temp_config_from_dialog["enable_test_entries"] = self.enable_test_check.isChecked()
            temp_config_from_dialog["debug_mode_enabled"] = self.debug_mode_check.isChecked()

            temp_config_from_dialog["customisable_ui_enabled"] = True
            temp_config_from_dialog["ui_locked"] = self.lock_ui_check.isChecked()

            for key_config in WIDGET_CONFIG_MAP.values():
                temp_config_from_dialog[key_config] = self.working_config_snapshot.get(key_config)
                print(f"  Gathering panel geo for '{key_config}': {temp_config_from_dialog[key_config]}")

            temp_config_from_dialog["window_geometry"] = self.working_config_snapshot.get("window_geometry")
            if "font_size_multiplier" not in self.working_config_snapshot or \
               abs(self.working_config_snapshot["font_size_multiplier"] - round(self.font_size_slider.value() / 100.0, 2)) > 0.001:
                font_size_value = self.font_size_slider.value()
                temp_config_from_dialog["font_size_multiplier"] = round(font_size_value / 100.0, 2)
            else:
                temp_config_from_dialog["font_size_multiplier"] = self.working_config_snapshot["font_size_multiplier"]


            for config_key_vol, (slider, _) in self.volume_sliders.items(): value = slider.value() / 100.0; temp_config_from_dialog[config_key_vol] = value
            temp_config_from_dialog["animation_type"] = self.anim_type_combo.currentText()
            temp_config_from_dialog["animation_box_speed"] = self.anim_box_speed_combo.currentText()

            temp_config_from_dialog["animation_list_duration"] = self.working_config_snapshot.get("animation_list_duration", "Normal")

            temp_config_from_dialog["animation_trig_speed"] = self.anim_trig_speed_combo.currentText()
            temp_config_from_dialog["animation_node_path_speed"] = self.anim_node_path_speed_combo.currentText()
            temp_config_from_dialog["animation_trig_conduit_speed"] = self.anim_trig_conduit_speed_combo.currentText()
            temp_config_from_dialog["animation_trig_code_length"] = self.trig_code_length_spin.value()
            temp_config_from_dialog["animation_trig_code_reveal_speed"] = self.trig_code_reveal_speed_combo.currentText()
            char_set_text = self.trig_code_char_set_edit.text().strip()
            if not char_set_text: raise ValueError("Triglavian Code Character Set cannot be empty.")
            temp_config_from_dialog["animation_trig_code_char_set"] = char_set_text
            temp_config_from_dialog["animation_trig_code_finalist_count"] = self.trig_code_finalist_count_spin.value()
            temp_config_from_dialog["google_analytics_enabled"] = self.ga_enabled_check.isChecked()
            temp_config_from_dialog["ga_measurement_id"] = self.ga_measurement_id_edit.text().strip()
            temp_config_from_dialog["ga_api_secret"] = self.ga_api_secret_edit.text().strip()
            temp_config_from_dialog["ga_client_id"] = self.working_config_snapshot.get("ga_client_id")
            temp_config_from_dialog["remote_logging_enabled"] = self.remote_log_enabled_check.isChecked()
            temp_config_from_dialog["remote_logging_url"] = self.remote_log_url_edit.text().strip()
            temp_config_from_dialog["remote_logging_api_key"] = self.remote_log_api_key_edit.text().strip()
            prize_options_from_list = [self.prize_options_list_widget.item(i).text() for i in range(self.prize_options_list_widget.count())]
            temp_config_from_dialog["prize_options"] = prize_options_from_list
            common_prizes_from_list = [self.common_prizes_list_widget.item(i).text() for i in range(self.common_prizes_list_widget.count())]
            temp_config_from_dialog["common_prizes_list"] = common_prizes_from_list
            temp_config_from_dialog["poll_duration"] = self.poll_duration_spin.value()
            temp_config_from_dialog["prize_selection_mode"] = self.working_config_snapshot.get("prize_selection_mode", PRIZE_MODE_POLL)

            # Chat messages from editable fields
            try:
                temp_config_from_dialog["chat_msg_winner_confirmation_needed"] = self.chat_msg_confirmation_edit.toPlainText().strip()
                temp_config_from_dialog["chat_msg_auto_lookup_attempt"] = self.chat_msg_auto_lookup_attempt_edit.toPlainText().strip()
                temp_config_from_dialog["chat_msg_auto_lookup_failed"] = self.chat_msg_auto_lookup_failed_edit.toPlainText().strip()
                temp_config_from_dialog["chat_msg_awaiting_ign"] = self.chat_msg_awaiting_ign_edit.toPlainText().strip()
                # Save quick ESI watchdog timeout
                temp_config_from_dialog["esi_short_timeout"] = int(self.esi_short_spin.value())
                # Save the new auto-lookup timeout value
                temp_config_from_dialog["eve2twitch_lookup_timeout"] = int(self.eve2twitch_lookup_spin.value())
            except Exception:
                # If fields are missing for some reason, fall back to existing snapshot
                temp_config_from_dialog.setdefault("chat_msg_winner_confirmation_needed", self.working_config_snapshot.get("chat_msg_winner_confirmation_needed"))
                temp_config_from_dialog.setdefault("chat_msg_auto_lookup_attempt", self.working_config_snapshot.get("chat_msg_auto_lookup_attempt"))
                temp_config_from_dialog.setdefault("chat_msg_auto_lookup_failed", self.working_config_snapshot.get("chat_msg_auto_lookup_failed"))
                temp_config_from_dialog.setdefault("chat_msg_awaiting_ign", self.working_config_snapshot.get("chat_msg_awaiting_ign"))

            if temp_config_from_dialog["confirmation_timeout"] <= 0: raise ValueError("Confirmation timeout must be positive.")
            if temp_config_from_dialog["eve_response_timeout"] <= 0: raise ValueError("EVE Response timeout must be a positive number.")
            if not (0.7 <= temp_config_from_dialog["font_size_multiplier"] <= 2.5): raise ValueError("Font size multiplier out of range (70% - 250%).")
            if temp_config_from_dialog["animation_type"] not in VALID_ANIMATION_TYPES: raise ValueError("Selected Draw Style Type is invalid.")
            if temp_config_from_dialog["animation_node_path_speed"] not in VALID_NODE_PATH_SPEEDS: raise ValueError("Selected Node Path Reveal Speed is invalid.")
            if temp_config_from_dialog["animation_trig_conduit_speed"] not in VALID_TRIG_CONDUIT_SPEEDS: raise ValueError("Selected Triglavian Conduit Speed is invalid.")
            if not (5 <= temp_config_from_dialog["animation_trig_code_length"] <= 12): raise ValueError("Triglavian code length must be between 5 and 12.")
            if temp_config_from_dialog["animation_trig_code_reveal_speed"] not in VALID_TRIG_CODE_REVEAL_SPEEDS: raise ValueError("Selected Triglavian Code Reveal Speed is invalid.")
            if not (2 <= temp_config_from_dialog["animation_trig_code_finalist_count"] <= 20): raise ValueError("Triglavian code finalist count must be between 2 and 20.")
            if temp_config_from_dialog["google_analytics_enabled"]:
                if not temp_config_from_dialog["ga_measurement_id"] or not temp_config_from_dialog["ga_measurement_id"].startswith("G-"): raise ValueError("GA Measurement ID is required and must start with 'G-' if Analytics is enabled.")
                if not temp_config_from_dialog["ga_api_secret"]: raise ValueError("GA API Secret is required if Analytics is enabled.")
            if temp_config_from_dialog["remote_logging_enabled"] and not temp_config_from_dialog["remote_logging_url"]: raise ValueError("Remote Logging URL is required if Remote Logging is enabled.")
            if temp_config_from_dialog["poll_duration"] <= 0: raise ValueError("Poll duration must be a positive number of seconds.")
        except ValueError as e: print(f"DEBUG: Validation failed: {e}"); QMessageBox.warning(self, "Invalid Input", f"Error: {e}"); return
        except Exception as e: print(f"DEBUG: Unexpected error gathering options: {e}"); QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}"); traceback.print_exc(); return

        self.working_config_snapshot.update(temp_config_from_dialog)
        print(f"OptionsDialog.accept(): Panel geometries in working_config_snapshot before apply_options_changes:")
        for k_cfg in WIDGET_CONFIG_MAP.values():
            print(f"  {k_cfg}: {self.working_config_snapshot.get(k_cfg)}")

        if self.parent_app: self.parent_app.apply_options_changes(self.working_config_snapshot)
        else: print("ERROR: OptionsDialog cannot find parent_app to apply changes!"); QMessageBox.critical(self, "Error", "Cannot apply changes (Internal error)."); return
        super().accept()

    def reject(self):
        print("DEBUG: OptionsDialog reject.")
        if self.parent_app:
            current_app_font_multiplier = self.parent_app.config.get("font_size_multiplier")
            initial_snapshot_font_multiplier = self.initial_config_snapshot.get("font_size_multiplier")

            if abs(current_app_font_multiplier - initial_snapshot_font_multiplier) > 0.001:
                print(f"DEBUG: Font size mismatch on reject. App: {current_app_font_multiplier}, Initial: {initial_snapshot_font_multiplier}. Reverting font.")
                self.parent_app.config["font_size_multiplier"] = initial_snapshot_font_multiplier
                self.parent_app._apply_font_size()

            self.parent_app.config = self.initial_config_snapshot.copy()
            self.parent_app.config["customisable_ui_enabled"] = True

            self.parent_app._discard_layout_changes()
            self.parent_app._update_layout_mode()

            if self.parent_app.animation_type_selector_main:
                self.parent_app.animation_type_selector_main.setCurrentText(self.parent_app.config.get("animation_type", config_manager.ANIM_TYPE_HACKING))
            if self.parent_app.prize_mode_selector:
                self.parent_app.prize_mode_selector.setCurrentText(self.parent_app.config.get("prize_selection_mode", PRIZE_MODE_POLL))

            self.parent_app._load_prize_options_into_dropdown()
            self.parent_app._update_prize_dropdown_behavior()
            self.parent_app.update_ui_button_states()
        super().reject()