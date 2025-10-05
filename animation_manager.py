import sys
import os

# Helper for PyInstaller asset path
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return str(Path(sys._MEIPASS) / relative_path)
    return str(Path(__file__).parent.resolve() / relative_path)
# animation_manager.py

import json
import traceback
from pathlib import Path

# --- PyQt6 Imports ---
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, QUrl, Qt
from PyQt6.QtGui import QPalette, QColor # Added QPalette, QColor
from PyQt6.QtWidgets import QLabel, QApplication, QStackedWidget 
# --- PyQt6 WebEngine Imports ---
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
    from PyQt6.QtWebChannel import QWebChannel
    webengine_available = True
except ImportError:
    webengine_available = False
    class QWebEngineView: pass 
    class QWebEnginePage: pass 
    class QWebChannel: pass   

# Asset files are now in the assets/ folder
ANIMATION_HTML_FILE = "assets/animation.html"
ANIMATION_JS_FILE = "assets/script.js"
ANIMATION_CSS_FILE = "assets/style.css"
ANIMATION_QWEBCHANNEL_FILE = "assets/qwebchannel.js"
NETWORK_JS_FILE = "assets/network_animation.js"
BG_LISTS_JS_FILE = "assets/background_lists.js"

class BackendBridge(QObject):
    jsReady = pyqtSignal()
    visualAnimationComplete = pyqtSignal(str)
    requestSound = pyqtSignal(str)
    prizeRevealComplete = pyqtSignal(str, str) # <<< NEW

    @pyqtSlot()
    def js_ready(self):
        print("ANIM_BRIDGE: Received js_ready signal from JavaScript.")
        self.jsReady.emit()

    @pyqtSlot(str)
    def jsVisualsComplete(self, winnerName):
        print(f"ANIM_BRIDGE: Received jsVisualsComplete for: {winnerName}")
        self.visualAnimationComplete.emit(winnerName)

    @pyqtSlot(str)
    def jsRequestSound(self, soundKeyMessage):
        if isinstance(soundKeyMessage, str) and soundKeyMessage:
            self.requestSound.emit(soundKeyMessage)
        else:
            print(f"ANIM_BRIDGE: Received invalid sound request: {soundKeyMessage}")

    @pyqtSlot(str, str) # <<< NEW
    def jsPrizeRevealComplete(self, prizeName, donatorName):
        print(f"ANIM_BRIDGE: Received jsPrizeRevealComplete for prize '{prizeName}'")
        self.prizeRevealComplete.emit(prizeName, donatorName)

    @pyqtSlot(str)
    def jsDebugMessage(self, message):
        print(f"JS_DEBUG: {message}")  # This will show JavaScript debug messages in Python console


class AnimationManager(QObject):
    js_ready_signal = pyqtSignal()
    visuals_complete_signal = pyqtSignal(str)
    sound_request_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    prize_reveal_complete_signal = pyqtSignal(str, str) # <<< NEW

    def __init__(self, parent=None): 
        super().__init__(parent)
        self._view = None
        self._channel = None
        self._bridge = None
        self._is_ready = False
        self._page_load_finished_successfully = False
        self.main_app_ref = parent 

        if not webengine_available:
            print("ANIM_MANAGER: WebEngine not available. Creating placeholder.")
            self._view = QLabel("Winner Animation Disabled\n(PyQtWebEngine not installed)")
            self._view.setStyleSheet("background-color: #111; border: 1px solid #555; color: #d4351e; padding: 10px;")
            self._view.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return

        try:
            print("ANIM_MANAGER: Initializing WebEngine components...")
            self._view = QWebEngineView()
            
            # Attributes to help prevent white flash
            self._view.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
            self._view.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
            
            # Set palette for the view itself
            palette = self._view.palette()
            palette.setColor(QPalette.ColorRole.Window, QColor("#05080a")) # Match body background
            self._view.setPalette(palette)
            self._view.setAutoFillBackground(True) # Important with palette change

            # Set page background to transparent so HTML body background shows through
            self._view.page().setBackgroundColor(Qt.GlobalColor.transparent)
            # Fallback stylesheet for the view if HTML transparency doesn't work as expected
            self._view.setStyleSheet("background-color: #05080a;") 


            settings = self._view.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, False)
            settings.setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, False)

            self._channel = QWebChannel(self._view.page())
            self._bridge = BackendBridge(self)
            self._channel.registerObject("backend", self._bridge)
            self._view.page().setWebChannel(self._channel)

            self._view.loadFinished.connect(self._on_page_load_finished)
            self._view.loadStarted.connect(lambda: print("ANIM_MANAGER: Page load started..."))
            if hasattr(self._view.page(), 'loadFailed'):
                 self._view.page().loadFailed.connect(self._on_page_load_failed)

            self._bridge.jsReady.connect(self._on_js_ready)
            self._bridge.visualAnimationComplete.connect(self._on_visuals_complete)
            self._bridge.requestSound.connect(self._on_sound_request)
            self._bridge.prizeRevealComplete.connect(self._on_prize_reveal_complete) # <<< NEW
            print("ANIM_MANAGER: WebEngine components initialized.")

        except Exception as e:
            print(f"ANIM_MANAGER: CRITICAL ERROR during WebEngine init: {e}")
            traceback.print_exc()
            self._view = QLabel(f"WebEngine Init Error:\n{e}")
            self._view.setStyleSheet("background-color: #111; border: 1px solid #555; color: red; padding: 10px;")
            self._view.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)
            self._view.setWordWrap(True)

    @pyqtSlot(bool)
    def _on_page_load_finished(self, success):
        self._page_load_finished_successfully = success
        if success:
            print("ANIM_MANAGER: Page load finished successfully.")
            # Notify main app if available, but only log to status bar if debug mode is enabled
            if hasattr(self, 'main_app_ref') and self.main_app_ref and hasattr(self.main_app_ref, 'log_status'):
                if getattr(self.main_app_ref, 'config', {}).get('debug_mode_enabled', False):
                    self.main_app_ref.log_status("Animation page loaded successfully.")
        else:
            print("ANIM_MANAGER: Page load finished with success=False. Check for JS errors or if loadFailed signal provided more info.")
            page_url = self._view.url().toString()
            error_msg = f"Failed to load animation page: {page_url}. Content might be missing or malformed."
            if hasattr(self, 'main_app_ref') and self.main_app_ref and hasattr(self.main_app_ref, 'log_status'):
                self.main_app_ref.log_status(f"ERROR: {error_msg}")
            if not hasattr(self._view.page(), 'loadFailed'): 
                self.error_signal.emit(error_msg)

    @pyqtSlot(int)
    def _on_page_load_failed(self, error_code):
        error_string = self._view.page().loadErrorString(error_code) if hasattr(self._view.page(), 'loadErrorString') else f"Unknown error code {error_code}"
        page_url = self._view.url().toString()
        error_msg = f"Animation Load Error: {error_string} for {page_url}"
        print(f"ANIM_MANAGER: Page load FAILED. URL: {page_url}, Error: {error_string} (Code: {error_code})")
        
        # Notify main app if available
        if hasattr(self, 'main_app_ref') and self.main_app_ref and hasattr(self.main_app_ref, 'log_status'):
            self.main_app_ref.log_status(f"ERROR: {error_msg}")
            
        self.error_signal.emit(error_msg)
        self._is_ready = False
        self._page_load_finished_successfully = False


    def get_view_widget(self):
        return self._view

    def load(self):
        if not webengine_available or not isinstance(self._view, QWebEngineView):
            print("ANIM_MANAGER: Cannot load page, WebEngine not available or view is invalid.")
            return False

        print("ANIM_MANAGER: load() called. Attempting to load actual animation.html.") 
        self._is_ready = False
        self._page_load_finished_successfully = False

        # Handle both development and PyInstaller packaged environments
        import sys
        import os
        
        # Use resource_path for all asset files
        html_path = Path(resource_path(ANIMATION_HTML_FILE))
        qwebchannel_path = Path(resource_path(ANIMATION_QWEBCHANNEL_FILE))
        js_path = Path(resource_path(ANIMATION_JS_FILE))
        css_path = Path(resource_path(ANIMATION_CSS_FILE))
        network_js_path = Path(resource_path(NETWORK_JS_FILE))
        bg_lists_js_path = Path(resource_path(BG_LISTS_JS_FILE))

        required_files = [
            (html_path, ANIMATION_HTML_FILE),
            (qwebchannel_path, ANIMATION_QWEBCHANNEL_FILE),
            (js_path, ANIMATION_JS_FILE),
            (css_path, ANIMATION_CSS_FILE),
            (network_js_path, NETWORK_JS_FILE),
            (bg_lists_js_path, BG_LISTS_JS_FILE),
        ]
        missing_files = [name for path, name in required_files if not path.is_file()]
        if missing_files:
            error_msg = f"Animation support files not found: {', '.join(missing_files)}"
            print(f"ERROR (ANIM_MANAGER): {error_msg}")
            print(f"ANIM_MANAGER: Searched in directory: {html_path.parent}")
            self.error_signal.emit(error_msg)
            error_html = f"<body style='background:#05080a;color:#d4351e; font-family: sans-serif; margin:0; padding:20px;'><h1>Error: Files Missing</h1><p>{error_msg}</p><p>Searched in: {html_path.parent}</p></body>"
            base_url = QUrl.fromLocalFile(str(html_path.parent) + "/")
            self._view.setHtml(error_html, base_url)
            return False

        # Load a minimal dark page first. The setUrl call will then replace this content.
        base_url = QUrl.fromLocalFile(str(html_path.parent.resolve()) + "/")
        self._view.setHtml("<body style='margin:0; background-color:#05080a;'></body>", base_url)
        QApplication.processEvents() # Give Qt a chance to render this minimal page

        file_url = QUrl.fromLocalFile(str(html_path.resolve()))
        print(f"ANIM_MANAGER: Loading animation page: {file_url.toString()}")
        self._view.setUrl(file_url)
        return True

    def start_reveal(self, winner_name, animation_type, options):
        print(f"ANIM_MANAGER: Attempting start_reveal. JS Ready: {self._is_ready}, Page Loaded Successfully: {self._page_load_finished_successfully}")
        if not self._is_ready:
            print("ANIM_MANAGER WARN: Cannot start reveal, JS not ready yet (self._is_ready is False).")
            if not self._page_load_finished_successfully:
                 print("ANIM_MANAGER WARN: Page load also not marked as successful. Possible load error or JS init failure.")
            self.error_signal.emit("Animation JS not ready. Cannot start reveal.")
            return
        if not self._page_load_finished_successfully:
            print("ANIM_MANAGER WARN: Cannot start reveal, page load was not successful.")
            self.error_signal.emit("Animation page did not load successfully. Cannot start reveal.")
            return

        if not isinstance(self._view, QWebEngineView):
             print("ANIM_MANAGER WARN: Cannot start reveal, view is not a QWebEngineView.")
             return

        print(f"ANIM_MANAGER: Requesting JS startAnimation for '{winner_name}', type '{animation_type}'")
        try:
            js_safe_name = json.dumps(winner_name)
            js_safe_type = json.dumps(animation_type)
            js_safe_options = json.dumps(options or {})
            js_code = f"startAnimation({js_safe_name}, {js_safe_type}, {js_safe_options});"
            self._view.page().runJavaScript(js_code)
            print("ANIM_MANAGER: JS startAnimation call executed.")
        except Exception as e:
            error_msg = f"Failed to execute startAnimation script: {e}"
            print(f"ANIM_MANAGER ERROR: {error_msg}")
            self.error_signal.emit(error_msg)
            traceback.print_exc()

    def start_prize_reveal(self, prize_name, donator_name): # <<< NEW
        print(f"ANIM_MANAGER: Attempting start_prize_reveal for '{prize_name}'. JS Ready: {self._is_ready}")
        if not self._is_ready:
            self.error_signal.emit("Animation JS not ready. Cannot start prize reveal.")
            return
        if not isinstance(self._view, QWebEngineView):
            return

        print(f"ANIM_MANAGER: Requesting JS startPrizeRevealAnimation for '{prize_name}'")
        try:
            js_safe_prize = json.dumps(prize_name)
            js_safe_donator = json.dumps(donator_name or "")
            js_code = f"startPrizeRevealAnimation({js_safe_prize}, {js_safe_donator});"
            self._view.page().runJavaScript(js_code)
            print("ANIM_MANAGER: JS startPrizeRevealAnimation call executed.")
        except Exception as e:
            error_msg = f"Failed to execute startPrizeRevealAnimation script: {e}"
            print(f"ANIM_MANAGER ERROR: {error_msg}")
            self.error_signal.emit(error_msg)
            traceback.print_exc()


    def cancel_animation(self):
        print(f"ANIM_MANAGER: Attempting cancel_animation. JS Ready: {self._is_ready}")
        if not self._is_ready:
             print("ANIM_MANAGER WARN: Cannot cancel animation, JS not ready yet.")
             return

        if not isinstance(self._view, QWebEngineView):
             print("ANIM_MANAGER WARN: Cannot cancel animation, view is not a QWebEngineView.")
             return

        print("ANIM_MANAGER: Requesting JS cancel animation sequence...");
        js_code = "if (typeof cancelAnimationAndCountdown === 'function') { cancelAnimationAndCountdown(); console.log('JS cancel function called.'); } else { console.warn('JS function cancelAnimationAndCountdown not found.'); }";
        try:
             self._view.page().runJavaScript(js_code)
        except Exception as e:
             error_msg = f"Failed to execute cancelAnimationAndCountdown script: {e}"
             print(f"ANIM_MANAGER ERROR: {error_msg}")
             self.error_signal.emit(error_msg)
             traceback.print_exc()

    def update_participants(self, participants):
        if not self._is_ready:
            return
        if not isinstance(self._view, QWebEngineView):
             return
        try:
            js_arg = json.dumps(participants);
            js_code = f"if(typeof updateParticipantsJS === 'function') {{ updateParticipantsJS({js_arg}); }} else {{ console.warn('JS function updateParticipantsJS not found'); }}";
            self._view.page().runJavaScript(js_code)
        except Exception as e:
            error_msg = f"Failed to send participant list to JS: {e}"
            print(f"ANIM_MANAGER ERROR: {error_msg}");
            self.error_signal.emit(error_msg)
            traceback.print_exc()

    def update_winner_esi_details_js(self, winner_data: dict):
        print(f"ANIM_MANAGER: update_winner_esi_details_js called. Portrait base64 present: {bool(winner_data.get('portrait_base64'))}, Type: {winner_data.get('portrait_content_type')}")
        if not self._is_ready or not isinstance(self._view, QWebEngineView):
            print("ANIM_MANAGER WARN: JS not ready or view invalid for ESI update (update_winner_esi_details_js).")
            return

        original_widget_on_stack = None
        main_stack_widget = None

        if self.main_app_ref and hasattr(self.main_app_ref, 'main_stack') and isinstance(self.main_app_ref.main_stack, QStackedWidget):
            main_stack_widget = self.main_app_ref.main_stack
            if main_stack_widget.currentWidget() != self._view:
                original_widget_on_stack = main_stack_widget.currentWidget()
                print("ANIM_MANAGER_ESI_UPDATE: Temporarily ensuring animation panel is current for ESI update.")
                main_stack_widget.setCurrentWidget(self._view)
                QApplication.processEvents() 

        try:
            js_safe_data = json.dumps(winner_data)
            js_code = f"if(typeof handleESIDataUpdate === 'function') {{ handleESIDataUpdate({js_safe_data}); console.log('JS handleESIDataUpdate was called from Python.'); }} else {{ console.warn('JS function handleESIDataUpdate not found'); }}"
            
            def restore_original_widget_if_needed(result=None):
                print(f"ANIM_MANAGER_ESI_UPDATE: JS handleESIDataUpdate call presumed executed. JS result: {result}")
                if original_widget_on_stack and main_stack_widget and main_stack_widget.currentWidget() == self._view:
                    print("ANIM_MANAGER_ESI_UPDATE: Restoring original panel after JS ESI update call.")
                    main_stack_widget.setCurrentWidget(original_widget_on_stack)
                    QApplication.processEvents()
                else:
                    print("ANIM_MANAGER_ESI_UPDATE: Original panel restoration not needed or stack changed.")

            self._view.page().runJavaScript(js_code, restore_original_widget_if_needed)
            print("ANIM_MANAGER: JS handleESIDataUpdate call initiated.")

        except Exception as e:
            error_msg = f"Failed to execute ESI update script (handleESIDataUpdate): {e}"
            print(f"ANIM_MANAGER ERROR: {error_msg}")
            self.error_signal.emit(error_msg)
            traceback.print_exc()
            if original_widget_on_stack and main_stack_widget and main_stack_widget.currentWidget() == self._view:
                print("ANIM_MANAGER_ESI_UPDATE: Restoring original panel due to Python exception during JS call.")
                main_stack_widget.setCurrentWidget(original_widget_on_stack)
                QApplication.processEvents()


    def stop(self):
        print("ANIM_MANAGER: Stopping...")
        if webengine_available and isinstance(self._view, QWebEngineView):
            try:
                base_url = QUrl.fromLocalFile(str(Path(__file__).parent.resolve()) + "/")
                self._view.setHtml("<body style='margin:0; background-color:#05080a;'></body>", base_url)
                self._view.stop() 
            except Exception as e:
                 print(f"ANIM_MANAGER: Error during WebEngine cleanup: {e}")
        self._is_ready = False
        self._page_load_finished_successfully = False

    @pyqtSlot()
    def _on_js_ready(self):
        print("ANIM_MANAGER: JS Ready signal received from BackendBridge.")
        if not self._page_load_finished_successfully:
            print("ANIM_MANAGER WARN: JS Ready signal received, BUT page load was not marked as successful. This might indicate an issue.")
        else:
            print("ANIM_MANAGER: JS Ready received AND page load was successful.")
        self._is_ready = True
        self.js_ready_signal.emit()
        print("ANIM_MANAGER: _is_ready set to True. Emitted js_ready_signal.")


    @pyqtSlot(str)
    def _on_visuals_complete(self, winner_name):
        print(f"ANIM_MANAGER: Visuals Complete signal received for '{winner_name}'.")
        self.visuals_complete_signal.emit(winner_name)
        
    @pyqtSlot(str, str) # <<< NEW
    def _on_prize_reveal_complete(self, prize_name, donator_name):
        print(f"ANIM_MANAGER: Prize Reveal Complete signal received for '{prize_name}'.")
        self.prize_reveal_complete_signal.emit(prize_name, donator_name)

    @pyqtSlot(str)
    def _on_sound_request(self, sound_message):
        self.sound_request_signal.emit(sound_message)