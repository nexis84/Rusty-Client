# ui_manager.py

import os
from pathlib import Path
import sys

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QFrame, QSizePolicy,
    QStackedWidget, QGridLayout, QTextEdit, QComboBox, QApplication, QCheckBox
)
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QFont, QFontDatabase, QFontMetrics, QTextCursor

# --- Resource Path Helper ---
def resource_path_ui(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(Path(sys.argv[0]).parent)
    return os.path.join(base_path, relative_path)

# --- Constants ---
DEFAULT_MARGIN_LEFT = 8
DEFAULT_MARGIN_TOP = 8
DEFAULT_MARGIN_RIGHT = 8
DEFAULT_MARGIN_BOTTOM = 4

WIDGET_NAME_MAIN_ACTION_BUTTONS = "main_action_buttons"
WIDGET_NAME_PRIZE_CONTROLS = "prize_controls"
WIDGET_NAME_ENTRANTS = "entrants_panel"
WIDGET_NAME_MAIN_STACK = "main_stack"

WIDGET_CONFIG_MAP = {
    WIDGET_NAME_MAIN_ACTION_BUTTONS: "main_action_buttons_geometry",
    WIDGET_NAME_PRIZE_CONTROLS: "top_controls_geometry",
    WIDGET_NAME_ENTRANTS: "entrants_panel_geometry",
    WIDGET_NAME_MAIN_STACK: "main_stack_geometry"
}

VALID_ANIMATION_TYPES = [
    "Hacking", "Triglavian Translation", "Node Path Reveal",
    "Triglavian Conduit", "Triglavian Code Reveal", "Random"
]
ANIM_TYPE_HACKING = "Hacking"
PRIZE_MODE_POLL = "Twitch Chat Poll"
VALID_PRIZE_MODES = ["Streamer Choice", "Twitch Chat Poll"]


class UIManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self._initial_geometry_load_retry_done = False

    def load_custom_fonts(self):
        fonts_dir = resource_path_ui('fonts')
        print(f"UI_FONT_LOAD: Attempting to load fonts from: {fonts_dir}")
        loaded_count = 0
        expected_fonts_files = {
            "Shentox-SemiBold.ttf": "Shentox-SemiBold",
            "Triglavian-Complete.otf": "Triglavian"
        }
        self.app.loaded_font_families = {}

        if not os.path.isdir(fonts_dir):
            print(f"UI_FONT_LOAD ERROR: Fonts directory not found at: {fonts_dir}")
            return

        for font_file, font_key in expected_fonts_files.items():
            font_path = os.path.join(fonts_dir, font_file)
            if os.path.isfile(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        actual_family_name = families[0]
                        self.app.loaded_font_families[font_key] = actual_family_name
                        print(f"UI_FONT_LOAD: Font '{font_file}' -> Family: '{actual_family_name}' (Key: '{font_key}')")
                        loaded_count += 1
                    else:
                        print(f"UI_FONT_LOAD WARNING: Loaded font '{font_file}', but no family name (id: {font_id}).")
                else:
                    print(f"UI_FONT_LOAD ERROR: Failed to load font: '{font_file}'.")
            else:
                print(f"UI_FONT_LOAD ERROR: Font file not found: '{font_path}'.")
        print(f"UI_FONT_LOAD: Finished. Loaded {loaded_count} custom fonts.")

    def get_base_font_specs(self):
        return {
            "Shentox-SemiBold": ("Shentox-SemiBold", 9, QFont.Weight.DemiBold),
            "labels":           ("Shentox-SemiBold", 9, QFont.Weight.DemiBold),
            "entries_count":    ("Shentox-SemiBold", 9, QFont.Weight.DemiBold),
            "list":             ("Shentox-SemiBold", 11, QFont.Weight.Normal),
            "prize_donator_info": ("Shentox-SemiBold", 11, QFont.Weight.DemiBold),
            "requirement":      ("Shentox-SemiBold", 9, QFont.Weight.DemiBold),
            "winner":           ("Shentox-SemiBold", 11, QFont.Weight.DemiBold),
            "log":              ("Consolas", 8, QFont.Weight.Normal),
            "status":           ("Consolas", 8, QFont.Weight.Bold),
        }

    def create_fonts(self):
        multiplier = self.app.config.get("font_size_multiplier", 1.0)
        self.app.fonts = {}
        system_families = QFontDatabase.families()
        base_font_specs = self.get_base_font_specs()

        for name_key, (preferred_font_key, base_size, weight) in base_font_specs.items():
            actual_family_to_use = None
            if preferred_font_key in self.app.loaded_font_families:
                actual_family_to_use = self.app.loaded_font_families[preferred_font_key]
            else:
                if preferred_font_key in system_families:
                     actual_family_to_use = preferred_font_key
                else:
                    if preferred_font_key == "Shentox-SemiBold":
                        fb_options = ["Segoe UI Semibold", "Segoe UI", "Arial", "SansSerif"]
                    elif preferred_font_key == "Consolas":
                        fb_options = ["Courier New", "Monospace"]
                    else:
                        fb_options = [preferred_font_key, "Arial", "SansSerif"]

                    for fb in fb_options:
                        if fb in system_families:
                            actual_family_to_use = fb
                            break
                    if not actual_family_to_use:
                        actual_family_to_use = QFont().defaultFamily()
                        print(f"UI_FONT: Ultimate fallback for '{preferred_font_key}' to system default: '{actual_family_to_use}'")

            new_size = max(1, round(base_size * multiplier))
            font = QFont(actual_family_to_use, new_size)
            font.setWeight(weight)
            self.app.fonts[name_key] = font
        print("UI_Manager: Fonts created/recreated.")

    def _configure_dynamic_size_for_infobox(self, frame_widget: QFrame, display_label: QLabel, num_lines_for_min_text_height: int):
        if not frame_widget or not display_label:
            print(f"UIManager Warning: Invalid frame or display_label passed to _configure_dynamic_size_for_infobox.")
            return

        label_widget = frame_widget.findChild(QLabel, "infoBoxLabel")
        if not label_widget:
            print(f"UIManager Warning: Could not find 'infoBoxLabel' in frame {frame_widget.objectName()}")
            return

        layout = frame_widget.layout()
        if not layout:
            print(f"UIManager Warning: Frame {frame_widget.objectName()} has no layout.")
            return

        # Calculate minimum height for the main display text based on its font
        font_metrics_display = QFontMetrics(display_label.font())
        min_display_height_calc = int(font_metrics_display.height() * num_lines_for_min_text_height)
        
        display_label.setMinimumHeight(min_display_height_calc)
        # Allow the display label to expand vertically if more content is added (like a long donator name)
        display_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)


        # Calculate height for the title label
        font_metrics_label = QFontMetrics(label_widget.font())
        label_height_calc = font_metrics_label.height()

        # Calculate total minimum frame height including margins and spacing
        margins = layout.contentsMargins()
        frame_top_margin = margins.top()
        frame_bottom_margin = margins.bottom()
        frame_spacing = layout.spacing()
        
        min_frame_height_calc = (frame_top_margin + 
                                 label_height_calc + 
                                 frame_spacing + 
                                 min_display_height_calc + 
                                 frame_bottom_margin)
        
        # Set the minimum height of the entire frame and fix its vertical size policy
        frame_widget.setMinimumHeight(min_frame_height_calc)
        frame_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        print(f"UIManager: Configured infobox {frame_widget.objectName()}: Display MinH={min_display_height_calc}, Frame MinH={min_frame_height_calc}, Frame VPolicy=Fixed (for {num_lines_for_min_text_height} lines)")


    def init_main_window_ui(self):
        # --- Main Action Buttons ---
        self.app.main_action_buttons_widget = QWidget(self.app)
        self.app.main_action_buttons_widget.setObjectName(WIDGET_NAME_MAIN_ACTION_BUTTONS)
        action_buttons_layout = QHBoxLayout(self.app.main_action_buttons_widget)
        action_buttons_layout.setContentsMargins(2, 2, 2, 2)
        action_buttons_layout.setSpacing(4)
        
        self.app.open_draw_button = QPushButton("OPEN DRAW")
        self.app.open_draw_button.setFont(self.app.fonts["Shentox-SemiBold"])
        self.app.start_draw_button = QPushButton("START DRAW")
        self.app.start_draw_button.setFont(self.app.fonts["Shentox-SemiBold"])
        self.app.abandon_draw_button = QPushButton("ABANDON DRAW")
        self.app.abandon_draw_button.setFont(self.app.fonts["Shentox-SemiBold"])
        self.app.purge_list_button = QPushButton("PURGE LIST")
        self.app.purge_list_button.setFont(self.app.fonts["Shentox-SemiBold"])
        self.app.options_button = QPushButton("OPTIONS")
        self.app.options_button.setFont(self.app.fonts["Shentox-SemiBold"])

        action_buttons_layout.addWidget(self.app.open_draw_button, 1)
        action_buttons_layout.addWidget(self.app.start_draw_button, 1)
        action_buttons_layout.addWidget(self.app.abandon_draw_button, 1)
        action_buttons_layout.addWidget(self.app.purge_list_button, 1)
        action_buttons_layout.addWidget(self.app.options_button, 1)
        
        self.app.main_action_buttons_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # --- Prize Input & Controls ---
        self.app.prize_controls_widget = QWidget(self.app)
        self.app.prize_controls_widget.setObjectName(WIDGET_NAME_PRIZE_CONTROLS)
        prize_controls_main_v_layout = QVBoxLayout(self.app.prize_controls_widget)
        prize_controls_main_v_layout.setContentsMargins(5, 2, 5, 2); prize_controls_main_v_layout.setSpacing(3)
        prize_input_row_layout = QHBoxLayout(); prize_input_row_layout.setSpacing(5)
        prize_label = QLabel("SET PRIZE:"); prize_label.setObjectName("prize_label"); prize_label.setFont(self.app.fonts["labels"]); prize_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        prize_input_row_layout.addWidget(prize_label)
        self.app.prize_input = QLineEdit(); self.app.prize_input.setFont(self.app.fonts["Shentox-SemiBold"]); self.app.prize_input.setMinimumWidth(100); self.app.prize_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.app.prize_input.setPlaceholderText("Prize Name (Donator in parenthesis)")
        prize_input_row_layout.addWidget(self.app.prize_input, 1)
        self.app.prize_options_dropdown = QComboBox(); self.app.prize_options_dropdown.setObjectName("prizeListDropdown"); self.app.prize_options_dropdown.setFont(self.app.fonts["Shentox-SemiBold"]); self.app.prize_options_dropdown.setMinimumWidth(130); self.app.prize_options_dropdown.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        prize_input_row_layout.addWidget(self.app.prize_options_dropdown, 1)
        prize_controls_main_v_layout.addLayout(prize_input_row_layout)
        
        prize_action_buttons_layout = QHBoxLayout()
        prize_action_buttons_layout.setSpacing(4)
        
        self.app.start_prize_poll_button = QPushButton("START POLL"); self.app.start_prize_poll_button.setFont(self.app.fonts["Shentox-SemiBold"]); self.app.start_prize_poll_button.setToolTip("Start a Twitch chat poll for the configured prize options.")
        prize_action_buttons_layout.addWidget(self.app.start_prize_poll_button)
        self.app.set_prize_button = QPushButton("SET"); self.app.set_prize_button.setFont(self.app.fonts["Shentox-SemiBold"])
        prize_action_buttons_layout.addWidget(self.app.set_prize_button)
        
        self.app.set_prize_and_open_button = QPushButton("SET / OPEN")
        self.app.set_prize_and_open_button.setFont(self.app.fonts["Shentox-SemiBold"]); self.app.set_prize_and_open_button.setToolTip("Set the prize (and parsed donator) and open the draw.")
        prize_action_buttons_layout.addWidget(self.app.set_prize_and_open_button)
        self.app.clear_prize_button = QPushButton("CLEAR PRIZE"); self.app.clear_prize_button.setFont(self.app.fonts["Shentox-SemiBold"])
        self.app.clear_prize_button.setObjectName("clearPrizeButton")
        prize_action_buttons_layout.addWidget(self.app.clear_prize_button)
        
        self.app.animation_type_selector_main = QComboBox(); self.app.animation_type_selector_main.setFont(self.app.fonts["Shentox-SemiBold"]); self.app.animation_type_selector_main.addItems(VALID_ANIMATION_TYPES); self.app.animation_type_selector_main.setCurrentText(self.app.config.get("animation_type", ANIM_TYPE_HACKING)); self.app.animation_type_selector_main.setToolTip("Select Draw Animation Style."); self.app.animation_type_selector_main.setMinimumWidth(120); self.app.animation_type_selector_main.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        prize_action_buttons_layout.addWidget(self.app.animation_type_selector_main)
        
        self.app.prize_mode_selector = QComboBox(); self.app.prize_mode_selector.setFont(self.app.fonts["Shentox-SemiBold"]); self.app.prize_mode_selector.addItems(VALID_PRIZE_MODES); self.app.prize_mode_selector.setCurrentText(self.app.config.get("prize_selection_mode", PRIZE_MODE_POLL)); self.app.prize_mode_selector.setToolTip("Select how the prize is determined."); self.app.prize_mode_selector.setMinimumWidth(130); self.app.prize_mode_selector.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        prize_action_buttons_layout.addWidget(self.app.prize_mode_selector)

        prize_controls_main_v_layout.addLayout(prize_action_buttons_layout)
        self.app.prize_controls_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # DEPRECATED: Top Overall Widget is no longer needed for layout but kept as an unused member
        self.app.top_overall_widget = QWidget(self.app)

        # --- Entrants Panel ---
        self.app.entrants_panel_widget = QWidget(self.app); self.app.entrants_panel_widget.setObjectName(WIDGET_NAME_ENTRANTS); entrants_layout = QVBoxLayout(self.app.entrants_panel_widget); entrants_layout.setContentsMargins(5, 5, 5, 5); entrants_layout.setSpacing(4);
        self.app.entries_count_label = QLabel("ENTRIES: 0"); self.app.entries_count_label.setFont(self.app.fonts["entries_count"]);
        self.app.participant_list = QListWidget(); self.app.participant_list.setFont(self.app.fonts["list"]); self.app.participant_list.setToolTip("List of users who have entered.");
        self.app.remove_selected_button = QPushButton("REMOVE SELECTED"); self.app.remove_selected_button.setFont(self.app.fonts["Shentox-SemiBold"]);
        entrants_layout.addWidget(self.app.entries_count_label); entrants_layout.addWidget(self.app.participant_list, 1); entrants_layout.addWidget(self.app.remove_selected_button);
        self.app.entrants_panel_widget.setMinimumWidth(180); self.app.entrants_panel_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred);

        # --- Main Stacked Widget (Info Panel / Animation Panel) ---
        self.app.main_stack = QStackedWidget(self.app); self.app.main_stack.setObjectName(WIDGET_NAME_MAIN_STACK);
        self.app.info_panel = QWidget(); info_layout = QVBoxLayout(self.app.info_panel); info_layout.setContentsMargins(5, 5, 5, 5); info_layout.setSpacing(6);

        def create_info_box(label_text, font_key_label, font_key_display):
            frame = QFrame(); frame.setObjectName("infoBox"); frame.setFrameShape(QFrame.Shape.StyledPanel);
            layout = QVBoxLayout(frame); layout.setContentsMargins(6, 3, 6, 6); layout.setSpacing(2);
            label = QLabel(label_text); label.setFont(self.app.fonts[font_key_label]); label.setObjectName("infoBoxLabel");
            display = QLabel("---"); display.setFont(self.app.fonts[font_key_display]); display.setWordWrap(True); display.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft);
            layout.addWidget(label); layout.addWidget(display, 1);
            return frame, display

        self.app.prize_donator_box_frame, self.app.current_prize_donator_display = create_info_box("CURRENT PRIZE & DONATOR", "labels", "prize_donator_info")
        self._configure_dynamic_size_for_infobox(self.app.prize_donator_box_frame, self.app.current_prize_donator_display, 4)

        self.app.req_box_frame, self.app.entry_requirement_display = create_info_box("ENTRY REQUIREMENT", "labels", "requirement")
        self._configure_dynamic_size_for_infobox(self.app.req_box_frame, self.app.entry_requirement_display, 2)

        self.app.winner_box_frame, self.app.selected_winner_display = create_info_box("SELECTED WINNER", "labels", "winner")
        self._configure_dynamic_size_for_infobox(self.app.winner_box_frame, self.app.selected_winner_display, 2)
        
        self.app.conf_frame = QFrame(); self.app.conf_frame.setObjectName("infoBox"); self.app.conf_frame.setFrameShape(QFrame.Shape.StyledPanel); conf_layout = QVBoxLayout(self.app.conf_frame); conf_layout.setContentsMargins(8, 5, 8, 8); conf_layout.setSpacing(6);
        conf_label = QLabel("CONFIRMATION & RESPONSE"); conf_label.setFont(self.app.fonts["labels"]); conf_label.setObjectName("infoBoxLabel");
        self.app.confirmation_log = QTextEdit(); self.app.confirmation_log.setReadOnly(True); self.app.confirmation_log.setFont(self.app.fonts["log"]);
        self.app.confirmation_log.setObjectName("confirmation_log"); self.app.confirmation_log.setToolTip("Shows status, entries, errors, and winner details.");
        self.app.confirmation_log.setAcceptRichText(True)
        # Set alignment to center for better display of timeout cards
        self.app.confirmation_log.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Auto-scroll to bottom whenever confirmation_log content changes so the IGN and latest messages are visible
        def _scroll_confirmation_to_bottom():
            try:
                cursor = self.app.confirmation_log.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.app.confirmation_log.setTextCursor(cursor)
                self.app.confirmation_log.ensureCursorVisible()
            except Exception:
                pass

        # Use a single-shot timer to ensure scrolling happens after the text update is applied
        self.app.confirmation_log.textChanged.connect(lambda: QTimer.singleShot(0, _scroll_confirmation_to_bottom))
        conf_button_layout = QHBoxLayout(); conf_button_layout.addStretch(1);
        self.app.copy_log_button = QPushButton("COPY"); self.app.copy_log_button.setFont(self.app.fonts["log"]); self.app.copy_log_button.setObjectName("copyButton"); conf_button_layout.addWidget(self.app.copy_log_button);
        conf_layout.addWidget(conf_label); conf_layout.addWidget(self.app.confirmation_log, 1); conf_layout.addLayout(conf_button_layout);
        
        info_layout.addWidget(self.app.prize_donator_box_frame)
        info_layout.addWidget(self.app.req_box_frame)
        info_layout.addWidget(self.app.winner_box_frame)
        info_layout.addWidget(self.app.conf_frame, 1)

        self.app.main_stack.addWidget(self.app.info_panel)
        self.app.main_stack.addWidget(self.app._animation_widget_ref)
        self.app.main_stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding);

        # --- Status Bar ---
        self.app.status_bar_label = QLabel(""); self.app.status_bar_label.setObjectName("statusBar"); self.app.status_bar_label.setFont(self.app.fonts["status"]); self.app.status_bar_label.setFixedHeight(20); self.app.status_bar_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter); self.app.status_bar_label.setStyleSheet("padding-left: 5px;"); self.app.status_bar_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed);

        # --- Main Layout Container & Grid ---
        self.app.main_content_area = QWidget(self.app); self.app.main_content_area.setObjectName("mainContentArea");
        self.app.main_content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.app.main_grid_layout = QGridLayout(self.app);
        self.app.main_grid_layout.setContentsMargins(DEFAULT_MARGIN_LEFT, DEFAULT_MARGIN_TOP, DEFAULT_MARGIN_RIGHT, DEFAULT_MARGIN_BOTTOM);
        self.app.main_grid_layout.setSpacing(8);
        self.app.setLayout(self.app.main_grid_layout);
        print("UI_Manager: Main window UI elements initialized.")


    def setup_manual_layout(self):
        print("UI_Manager: Setting up Manual (Customisable) Layout")
        self._initial_geometry_load_retry_done = False

        # List of widgets that will be manually placed
        widgets_to_move = [
            self.app.main_action_buttons_widget,
            self.app.prize_controls_widget,
            self.app.entrants_panel_widget,
            self.app.main_stack
        ]

        # Clear the grid layout of all widgets
        if self.app.main_grid_layout.indexOf(self.app.top_overall_widget) != -1:
             self.app.main_grid_layout.removeWidget(self.app.top_overall_widget)
             self.app.top_overall_widget.setParent(None)
        
        for widget in widgets_to_move:
            if widget and self.app.main_grid_layout.indexOf(widget) != -1:
                self.app.main_grid_layout.removeWidget(widget)
        
        if self.app.main_grid_layout.indexOf(self.app.status_bar_label) != -1:
            self.app.main_grid_layout.removeWidget(self.app.status_bar_label)

        # Ensure the main content area is a child of the main window
        if self.app.main_content_area.parent() != self.app:
            self.app.main_content_area.setParent(self.app)
        
        # Clear out any remaining items from the grid layout
        while self.app.main_grid_layout.count():
            item = self.app.main_grid_layout.takeAt(0)
            if item and item.widget():
                item.widget().setParent(None)

        # Re-add the content area and status bar to the grid
        self.app.main_grid_layout.addWidget(self.app.main_content_area, 0, 0, 1, 1)
        self.app.main_grid_layout.addWidget(self.app.status_bar_label, 1, 0, 1, 1)
        self.app.main_grid_layout.setRowStretch(0, 1)
        self.app.main_grid_layout.setRowStretch(1, 0)
        self.app.main_grid_layout.setColumnStretch(0, 1)

        # Parent the draggable widgets to the main_content_area
        for widget_to_move in widgets_to_move:
            if widget_to_move and widget_to_move.parent() != self.app.main_content_area:
                widget_to_move.setParent(self.app.main_content_area)
            if widget_to_move:
                widget_to_move.show()
        
        self.app.main_content_area.show()
        self.app.status_bar_label.show()
        
        self.app.layout().invalidate()
        self.app.layout().activate()
        self.app.main_content_area.updateGeometry()
        self.app.updateGeometry()
        
        # KEY CHANGE: Delay loading geometries until the window is fully shown and sized
        QApplication.processEvents()
        QTimer.singleShot(250, self.load_widget_geometries)
        self.app.update()

    def load_widget_geometries(self):
        print("UI_Manager: Loading widget geometries for manual layout...")
        QApplication.processEvents()

        # Use the content area's rect as the basis for all calculations
        parent_rect_for_panels = self.app.main_content_area.rect()
        pw = parent_rect_for_panels.width()
        ph = parent_rect_for_panels.height()
        
        print(f"UI_Manager: Parent rect for panel calculations: {pw}x{ph}")

        if pw < 200 or ph < 200: 
            print(f"UI_Manager WARNING: main_content_area ({pw}x{ph}) is too small for layout calculation.")
            if not self._initial_geometry_load_retry_done: 
                self._initial_geometry_load_retry_done = True 
                QTimer.singleShot(300, self.load_widget_geometries) 
                print("UI_Manager: Retrying load_widget_geometries due to small parent rect.")
                return
            else: 
                print("UI_Manager: Retry failed, parent rect still small. This may lead to incorrect default layouts.")
        
        default_spacing = 8 
        min_panel_width = 150 
        min_panel_height = 100

        # --- Default Layout Calculation ---
        # Get dynamic heights based on current font
        main_actions_h = self.app.main_action_buttons_widget.sizeHint().height()
        prize_controls_sh = self.app.prize_controls_widget.sizeHint()
        prize_controls_h = prize_controls_sh.height() if prize_controls_sh.isValid() else 60
        top_row_h = max(main_actions_h, prize_controls_h, 35)

        # Widths for the two top panels
        left_top_w_ratio = 0.40
        final_main_actions_w = int((pw - (default_spacing * 2)) * left_top_w_ratio)
        main_actions_x = default_spacing
        
        prize_controls_x = main_actions_x + final_main_actions_w + default_spacing
        final_prize_controls_w = pw - prize_controls_x - default_spacing

        # Y position and height for the bottom row panels
        bottom_row_y = default_spacing + top_row_h + default_spacing
        final_bottom_row_h = max(min_panel_height, ph - bottom_row_y - default_spacing)

        # Widths for bottom row panels
        entrants_w_ratio = 0.22
        final_entrants_w = max(self.app.entrants_panel_widget.minimumSizeHint().width(), int((pw - (default_spacing*2)) * entrants_w_ratio))
        entrants_x = default_spacing

        main_stack_x = entrants_x + final_entrants_w + default_spacing
        final_main_stack_w = pw - main_stack_x - default_spacing

        # Define the default geometries
        defaults = {
            "main_action_buttons_geometry": f"{main_actions_x},{default_spacing},{final_main_actions_w},{top_row_h}",
            "top_controls_geometry":  f"{prize_controls_x},{default_spacing},{final_prize_controls_w},{top_row_h}",
            "entrants_panel_geometry": f"{entrants_x},{bottom_row_y},{final_entrants_w},{final_bottom_row_h}",
            "main_stack_geometry": f"{main_stack_x},{bottom_row_y},{final_main_stack_w},{final_bottom_row_h}"
        }
        
        print(f"Calculated defaults based on parent {pw}x{ph}: {defaults}")

        widgets_to_load = {
            WIDGET_NAME_MAIN_ACTION_BUTTONS: self.app.main_action_buttons_widget,
            WIDGET_NAME_PRIZE_CONTROLS: self.app.prize_controls_widget,
            WIDGET_NAME_ENTRANTS: self.app.entrants_panel_widget,
            WIDGET_NAME_MAIN_STACK: self.app.main_stack
        }

        for name, widget_to_set in widgets_to_load.items(): 
            if widget_to_set:
                config_key = WIDGET_CONFIG_MAP[name]
                default_geo_str = defaults.get(config_key) 
                
                # Prioritize unsaved, then saved, then default geometry
                geo_from_config = self.app.config.get(config_key)
                if config_key in self.app.unsaved_layout_changes:
                    final_geo_str_to_use = self.app.unsaved_layout_changes[config_key]
                elif geo_from_config:
                    final_geo_str_to_use = geo_from_config
                else:
                    final_geo_str_to_use = default_geo_str
                
                rect = QRect()
                valid_geo_loaded = False
                if final_geo_str_to_use and len(final_geo_str_to_use.split(',')) == 4 : 
                    try:
                        x, y, w, h = map(int, final_geo_str_to_use.split(','))
                        
                        # Use sizeHint which considers font size for minimum dimensions
                        min_w_hint = widget_to_set.sizeHint().width()
                        min_h_hint = widget_to_set.sizeHint().height()

                        w = max(w, min_w_hint if min_w_hint > 0 else min_panel_width)
                        h = max(h, min_h_hint if min_h_hint > 0 else min_panel_height)
                        
                        # Clamp geometry within the parent widget's bounds
                        parent_for_positioning = widget_to_set.parentWidget()
                        if parent_for_positioning:
                            parent_w = parent_for_positioning.width()
                            parent_h = parent_for_positioning.height()
                            if parent_w > 0:
                                w = min(w, parent_w) 
                                x = min(max(0, x), parent_w - w)
                            if parent_h > 0:
                                h = min(h, parent_h)
                                y = min(max(0, y), parent_h - h)

                        if w > 10 and h > 10: 
                            rect = QRect(x, y, w, h)
                            valid_geo_loaded = True
                    except (ValueError, TypeError): pass 
                
                if not valid_geo_loaded: 
                    print(f"UI_Manager: ERROR - Could not parse/validate geometry '{final_geo_str_to_use}' for {name}. Using default: {default_geo_str}")
                    x_def, y_def, w_def, h_def = map(int, default_geo_str.split(',')) 
                    rect = QRect(x_def, y_def, w_def, h_def)
                
                print(f"UI_Manager: FINAL Setting geometry for {name} to {rect.x()},{rect.y()},{rect.width()}x{rect.height()}")
                widget_to_set.setGeometry(rect)
                widget_to_set.show()
        
        # Mark that the initial geometry load has happened
        if not getattr(self.app, '_panel_geometries_applied_this_session', False):
            if not (pw < 200 or ph < 200): 
                self.app._panel_geometries_applied_this_session = True 
                print("UI_Manager: Marked initial panel geometries as applied for this session.")