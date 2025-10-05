
# Place DEFAULT_CONFIG after animation type constants are defined


# --- Define Animation Types ---
ANIM_TYPE_HACKING = "Hacking"
# ANIM_TYPE_LIST = "Vertical List" # Ensured removed
ANIM_TYPE_TRIGLAVIAN = "Triglavian Translation"
ANIM_TYPE_NODE_PATH = "Node Path Reveal"
ANIM_TYPE_TRIG_CONDUIT = "Triglavian Conduit"
ANIM_TYPE_TRIG_CODE_REVEAL = "Triglavian Code Reveal"
ANIM_TYPE_RANDOM_TECH = "Random"

DEFAULT_CONFIG = {
    "animation_type": ANIM_TYPE_TRIGLAVIAN,
}
# config_manager.py
import os
import json
import traceback
import re 
from pathlib import Path
from dotenv import load_dotenv
import sys 
try:
    from PyQt6.QtCore import QStandardPaths 
    qt_available = True
except ImportError:
    qt_available = False
    print("WARNING (config_manager): PyQt6 not found. Config saving might fall back to local directory.")


CONFIG_FILE = "config.json"
APP_NAME = "RustyBotGiveaway"
ORG_NAME = "RustyBit"

# --- Define Animation Types ---
ANIM_TYPE_HACKING = "Hacking"
# ANIM_TYPE_LIST = "Vertical List" # Ensured removed
ANIM_TYPE_TRIGLAVIAN = "Triglavian Translation"
ANIM_TYPE_NODE_PATH = "Node Path Reveal"
ANIM_TYPE_TRIG_CONDUIT = "Triglavian Conduit"
ANIM_TYPE_TRIG_CODE_REVEAL = "Triglavian Code Reveal"
ANIM_TYPE_RANDOM_TECH = "Random"

VALID_ANIMATION_TYPES = [
    ANIM_TYPE_HACKING,
    ANIM_TYPE_TRIGLAVIAN,
    ANIM_TYPE_NODE_PATH,
    ANIM_TYPE_TRIG_CONDUIT,
    ANIM_TYPE_TRIG_CODE_REVEAL,
    ANIM_TYPE_RANDOM_TECH
]

TRIG_SPEED_FAST = "Fast"
TRIG_SPEED_NORMAL = "Normal"
TRIG_SPEED_SLOW = "Slow"
VALID_TRIG_SPEEDS = [TRIG_SPEED_FAST, TRIG_SPEED_NORMAL, TRIG_SPEED_SLOW]

NODE_PATH_SPEED_NORMAL = "Normal"
NODE_PATH_SPEED_SLOW = "Slow"
NODE_PATH_SPEED_VERY_SLOW = "Very Slow"
VALID_NODE_PATH_SPEEDS = [NODE_PATH_SPEED_NORMAL, NODE_PATH_SPEED_SLOW, NODE_PATH_SPEED_VERY_SLOW]

TRIG_CONDUIT_SPEED_FAST = "Fast"
TRIG_CONDUIT_SPEED_NORMAL = "Normal"
TRIG_CONDUIT_SPEED_SLOW = "Slow"
VALID_TRIG_CONDUIT_SPEEDS = [TRIG_CONDUIT_SPEED_FAST, TRIG_CONDUIT_SPEED_NORMAL, TRIG_CONDUIT_SPEED_SLOW]

TRIG_CODE_REVEAL_SPEED_FAST = "Fast"
TRIG_CODE_REVEAL_SPEED_NORMAL = "Normal"
TRIG_CODE_REVEAL_SPEED_SLOW = "Slow"
VALID_TRIG_CODE_REVEAL_SPEEDS = [TRIG_CODE_REVEAL_SPEED_FAST, TRIG_CODE_REVEAL_SPEED_NORMAL, TRIG_CODE_REVEAL_SPEED_SLOW]

TRIG_CODE_ALPHANUMERIC_GLYPHS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCČDEFGHILMNOPRSŠTUVZŽƕƆƗƖƜƞƚƶENTYΛƆЯƧИ"

# --- Prize Selection Modes ---
PRIZE_MODE_STREAMER = "Streamer Choice"
PRIZE_MODE_POLL = "Twitch Chat Poll"
VALID_PRIZE_MODES = [PRIZE_MODE_STREAMER, PRIZE_MODE_POLL]

# --- Max Common Prizes ---
#MAX_COMMON_PRIZES = 5 # Commented out line

DEFAULT_CONFIG = {
    "confirmation_timeout": 90,
    "eve_response_timeout": 300,
    "entry_condition_type": "Predefined Command",
    "join_command": "!play",
    "custom_join_command": "!win",
    "window_geometry": None, # <<< Forcing to None for maximized startup
    "enable_test_entries": False,
    "multi_draw_enabled": False,
    "target_channel": None,
    "font_size_multiplier": 1.0,
    "customisable_ui_enabled": True,
    "ui_locked": True,
    "main_action_buttons_geometry": None,
    "top_controls_geometry": None,
    "entrants_panel_geometry": None,
    "main_stack_geometry": None,
    "master_volume": 0.75,
    "ai_voice_volume": 0.7,
    "warning_sounds_volume": 0.6,
    "hacking_background_volume": 0.2,
    "countdown_volume": 0.6,
    "animation_type": ANIM_TYPE_HACKING,
    "animation_box_speed": "Normal",
    "animation_list_duration": "Normal", # Kept for compatibility, though list anim is removed
    "animation_trig_speed": TRIG_SPEED_NORMAL,
    "animation_node_path_speed": NODE_PATH_SPEED_NORMAL,
    "animation_trig_conduit_speed": TRIG_CONDUIT_SPEED_NORMAL,
    "animation_trig_code_length": 8,
    "animation_trig_code_reveal_speed": TRIG_CODE_REVEAL_SPEED_NORMAL,
    "animation_trig_code_char_set": TRIG_CODE_ALPHANUMERIC_GLYPHS,
    "animation_trig_code_finalist_count": 10,
    "google_analytics_enabled": True,
    "ga_measurement_id": "G-NMCBJZKMC6",
    "ga_api_secret": "-NCziwRDSgCzm-S2TMOlFw",
    "ga_client_id": None,
    "remote_logging_enabled": False,
    "remote_logging_url": "",
    "remote_logging_api_key": "",
    "prize_options": [],
    "common_prizes_list": [],
    "poll_duration": 30,
    "prize_selection_mode": PRIZE_MODE_POLL,
    "debug_mode_enabled": False,
    # Customisable chat messages (use Python format placeholders: {winner}, {prize}, {timeout})
    "chat_msg_winner_confirmation_needed": "🎉 Congrats @{winner}! 🎉 You won: {prize}! Type anything (or !ign) in chat within {timeout}s to confirm!",
    "chat_msg_auto_lookup_attempt": "@{winner} confirmed! Congratulations! Attempting automatic EVE2Twitch lookup for your EVE IGN — please wait.",
    "chat_msg_auto_lookup_failed": "@{winner} confirmed! We could not validate your EVE IGN automatically. Please register with the IGN bot or type '!ign <your in-game name>' in chat to provide your IGN.",
    "chat_msg_awaiting_ign": "@{winner} confirmed! Congratulations! Awaiting Capsuleers name, Please type !ign in chat",
    # Message when ESI validation succeeds. Placeholders: {winner}, {ign}
    "chat_msg_ign_found": "@{winner} — IGN verified: {ign}. Congratulations on winning!",
    # How long (seconds) to wait for automatic EVE2Twitch lookup before prompting for !ign
    "eve2twitch_lookup_timeout": 10,
    # Short watchdog timeout (seconds) used when fetching ESI data after auto-lookup
    "esi_short_timeout": 5,
}
ENTRY_TYPE_PREDEFINED = "Predefined Command"
ENTRY_TYPE_ANYTHING = "Type Anything"
ENTRY_TYPE_CUSTOM = "Custom Command"
VALID_ENTRY_TYPES = [ENTRY_TYPE_PREDEFINED, ENTRY_TYPE_ANYTHING, ENTRY_TYPE_CUSTOM]
PREDEFINED_COMMANDS = ["!play", "!draw", "!hype"]


def _get_config_path():
    """Determines the appropriate path for the config file using QStandardPaths."""
    if qt_available:
        data_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not data_dir_str:
            data_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation)
            if data_dir_str:
                 data_dir = Path(data_dir_str) / ORG_NAME / APP_NAME
            else:
                 data_dir = None
        else:
            data_dir = Path(data_dir_str)

        if data_dir:
             try:
                 data_dir.mkdir(parents=True, exist_ok=True)
                 config_path = data_dir / CONFIG_FILE
                 print(f"DEBUG (config_manager): Using config path: {config_path}")
                 return config_path
             except Exception as e:
                 print(f"ERROR (config_manager): Failed to create/access standard config directory {data_dir}: {e}")
        else:
             print("ERROR (config_manager): Could not find writable AppDataLocation or GenericDataLocation.")

    print("WARNING (config_manager): Falling back to saving config next to script/executable.")
    try:
        if getattr(sys, 'frozen', False):
            exe_dir = Path(sys.executable).parent
            parent_dir = exe_dir.parent
            
            # Check parent directory first (for organized structure: root/config.json and root/app/RustyBot.exe)
            parent_config = parent_dir / CONFIG_FILE
            if parent_config.exists():
                print(f"DEBUG (config_manager): Found config in parent directory: {parent_config}")
                return parent_config
            
            # Try parent directory even if it doesn't exist yet (for new installs)
            # This assumes app is in a subfolder like 'app'
            if exe_dir.name.lower() == 'app':
                fallback_path = parent_config
                print(f"DEBUG (config_manager): Using parent config path (app folder detected): {fallback_path}")
                return fallback_path
            
            # Fall back to exe directory
            fallback_path = exe_dir / CONFIG_FILE
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller compatibility - also check _MEIPASS
                meipass_config = Path(sys._MEIPASS) / CONFIG_FILE
                if meipass_config.exists():
                    return meipass_config
        else:
            fallback_path = Path(__file__).parent.resolve() / CONFIG_FILE
        
        print(f"DEBUG (config_manager): Using fallback config path: {fallback_path}")
        return fallback_path
    except Exception as e:
        print(f"ERROR (config_manager): Cannot determine fallback config path: {e}")
        return Path.cwd() / CONFIG_FILE

def _validate_volume(val, default):
    try:
        v = float(val)
        return max(0.0, min(1.0, v))
    except (ValueError, TypeError):
        return float(default)

def _validate_font_multiplier(val, default=1.0, min_val=0.7, max_val=2.5):
    try:
        v = float(val)
        return max(min_val, min(max_val, v))
    except (ValueError, TypeError):
        return float(default)

def _validate_geometry_string(geo_str):
    if not isinstance(geo_str, str):
        return False
    return bool(re.fullmatch(r"^\d+,\d+,\d+,\d+$", geo_str))

def save_config(config_data):
    """Saves the configuration dictionary to the JSON file."""
    config_path = _get_config_path()
    print(f"DEBUG: Attempting to save config to {config_path}")
    try:
        config_to_save = config_data.copy()

        # Always force UI to be enabled and window_geometry to be None on save
        # This prevents saving a non-maximized window state, improving layout stability on startup.
        config_to_save["customisable_ui_enabled"] = True
        config_to_save["window_geometry"] = None

        # Filter out any keys that are not in the default config to prevent saving obsolete keys
        config_to_save_filtered = {
            k: config_to_save[k] for k in DEFAULT_CONFIG.keys() if k in config_to_save
        }

        # Check for keys that are allowed to be None
        keys_to_check_if_none_allowed = ["window_geometry",
                                       "main_action_buttons_geometry",
                                       "top_controls_geometry",
                                       "entrants_panel_geometry", "main_stack_geometry",
                                       "target_channel", "ga_client_id"]

        for key in keys_to_check_if_none_allowed:
            if key in config_to_save and config_to_save[key] is None and key in DEFAULT_CONFIG and DEFAULT_CONFIG[key] is None:
                config_to_save_filtered[key] = None
            elif key in config_to_save_filtered and config_to_save_filtered.get(key) is None and DEFAULT_CONFIG.get(key) is not None:
                 config_to_save_filtered.pop(key, None)

        print(f"DEBUG: Saving filtered config: {json.dumps(config_to_save_filtered, indent=2)}")
        with open(config_path, 'w') as f:
            json.dump(config_to_save_filtered, f, indent=4)
        print(f"Saved config successfully to {config_path}")
        return True
    except TypeError as e:
         print(f"ERROR saving config: Data type issue. Filtered data: {config_to_save_filtered}")
         print(f"Error details: {e}")
         traceback.print_exc()
         return False
    except Exception as e:
        print(f"ERROR saving config to {config_path}: {e}")
        traceback.print_exc()
        return False

def load_config():
    config_path = _get_config_path()
    config = DEFAULT_CONFIG.copy()
    config_changed = False
    original_config_before_validation = {}

    ALL_DEFINED_ANIMATION_TYPES = [ # All types ever defined for validation, even if removed from VALID_ANIMATION_TYPES
        ANIM_TYPE_HACKING,
        "Vertical List", # Keep "Vertical List" here for loading old configs
        ANIM_TYPE_TRIGLAVIAN, ANIM_TYPE_NODE_PATH, ANIM_TYPE_TRIG_CONDUIT,
        ANIM_TYPE_TRIG_CODE_REVEAL, ANIM_TYPE_RANDOM_TECH
    ]

    try:
        if config_path.exists() and config_path.is_file():
            print(f"Loading config from {config_path}")
            with open(config_path, 'r') as f:
                loaded_data = json.load(f)

            # --- Migration for old/obsolete keys ---
            if "adjust_layout_mode" in loaded_data and "customisable_ui_enabled" not in loaded_data:
                print("Info: Found old 'adjust_layout_mode' key, it will be ignored/removed.")
                loaded_data.pop("adjust_layout_mode")
                config_changed = True

            if "animation_wheel_duration" in loaded_data:
                print("Info: Found obsolete 'animation_wheel_duration' key. It will be removed.")
                loaded_data.pop("animation_wheel_duration", None)
                config_changed = True
            
            if "animation_list_scroll_duration" in loaded_data and "animation_list_duration" not in loaded_data:
                loaded_data["animation_list_duration"] = loaded_data.pop("animation_list_scroll_duration")
                print("Info: Migrated 'animation_list_scroll_duration' to 'animation_list_duration'.")
                config_changed = True

            if "streamer_choice_enabled" in loaded_data or "twitch_choice_enabled" in loaded_data:
                if "prize_selection_mode" not in loaded_data:
                    if loaded_data.get("streamer_choice_enabled", False):
                        loaded_data["prize_selection_mode"] = PRIZE_MODE_STREAMER
                    else:
                        loaded_data["prize_selection_mode"] = PRIZE_MODE_POLL
                    print(f"Info: Migrated old prize choice keys to 'prize_selection_mode': {loaded_data['prize_selection_mode']}")
                loaded_data.pop("streamer_choice_enabled", None)
                loaded_data.pop("twitch_choice_enabled", None)
                config_changed = True
            
            # --- Load data into config, preferring loaded over default ---
            for key in DEFAULT_CONFIG.keys():
                if key == "customisable_ui_enabled":
                    if key not in loaded_data or loaded_data[key] is not True:
                        config_changed = True
                    config[key] = True # Always force to True
                    continue
                
                if key == "window_geometry": # Always force to None on load for stable startup
                    if loaded_data.get(key) is not None: 
                        print("INFO (config_manager load): Forcing 'window_geometry' to None for maximized startup.")
                        config_changed = True
                    config[key] = None
                    continue

                if key in loaded_data:
                    if loaded_data[key] is not None:
                         config[key] = loaded_data[key]
                    else: # Key exists in loaded_data but is None
                        if DEFAULT_CONFIG[key] is not None: # If default is not None, use default
                            print(f"Info: Key '{key}' was null in {config_path.name}, using default '{DEFAULT_CONFIG[key]}'.")
                            config[key] = DEFAULT_CONFIG[key]
                            config_changed = True
                        else: # Default is also None, so keep None
                            config[key] = None
                else: # Key not in loaded_data at all
                    print(f"Info: Key '{key}' not found in {config_path.name}, using default '{DEFAULT_CONFIG[key]}'.")
                    config[key] = DEFAULT_CONFIG[key]
                    config_changed = True
        else:
            print(f"Info: Config file not found at {config_path}. Using all defaults.")
            config = DEFAULT_CONFIG.copy()
            config["window_geometry"] = None # Ensure it's None for new configs
            config_changed = True

        original_config_before_validation = config.copy()

        # --- VALIDATIONS & SANITIZATION ---
        config["customisable_ui_enabled"] = True 
        if not original_config_before_validation.get("customisable_ui_enabled", True):
            config_changed = True
        
        config["window_geometry"] = None # Re-confirm it's None
        if original_config_before_validation.get("window_geometry") is not None:
            config_changed = True

        # --- Integer Validations ---
        ct = config.get("confirmation_timeout", DEFAULT_CONFIG["confirmation_timeout"])
        try: config["confirmation_timeout"] = int(ct)
        except (ValueError, TypeError): config["confirmation_timeout"] = DEFAULT_CONFIG["confirmation_timeout"]
        if config["confirmation_timeout"] <= 0: config["confirmation_timeout"] = DEFAULT_CONFIG["confirmation_timeout"]

        et = config.get("eve_response_timeout", DEFAULT_CONFIG["eve_response_timeout"])
        try: config["eve_response_timeout"] = int(et)
        except (ValueError, TypeError): config["eve_response_timeout"] = DEFAULT_CONFIG["eve_response_timeout"]
        if config["eve_response_timeout"] <= 0: config["eve_response_timeout"] = DEFAULT_CONFIG["eve_response_timeout"]

        # --- String / Enum Validations ---
        ect = config.get("entry_condition_type", DEFAULT_CONFIG["entry_condition_type"])
        config["entry_condition_type"] = str(ect) if ect in VALID_ENTRY_TYPES else DEFAULT_CONFIG["entry_condition_type"]

        jc = config.get("join_command", DEFAULT_CONFIG["join_command"])
        config["join_command"] = str(jc).lower() if jc else DEFAULT_CONFIG["join_command"]
        if config["join_command"] not in PREDEFINED_COMMANDS:
             print(f"Warning: Loaded predefined join_command '{config['join_command']}' is not in the valid list {PREDEFINED_COMMANDS}. Resetting to default '{DEFAULT_CONFIG['join_command']}'.")
             config["join_command"] = DEFAULT_CONFIG["join_command"]

        cjc = config.get("custom_join_command", DEFAULT_CONFIG["custom_join_command"])
        config["custom_join_command"] = str(cjc) if cjc else DEFAULT_CONFIG["custom_join_command"]
        
        loaded_channel = config.get("target_channel")
        if loaded_channel is not None:
            config["target_channel"] = str(loaded_channel).strip()
            if not config["target_channel"]: config["target_channel"] = None
        else: config["target_channel"] = None

        # --- Float Validations ---
        fsm = config.get("font_size_multiplier", DEFAULT_CONFIG["font_size_multiplier"])
        config["font_size_multiplier"] = _validate_font_multiplier(fsm, DEFAULT_CONFIG["font_size_multiplier"])
        config["master_volume"] = _validate_volume(config.get("master_volume"), DEFAULT_CONFIG["master_volume"])
        config["ai_voice_volume"] = _validate_volume(config.get("ai_voice_volume"), DEFAULT_CONFIG["ai_voice_volume"])
        config["warning_sounds_volume"] = _validate_volume(config.get("warning_sounds_volume"), DEFAULT_CONFIG["warning_sounds_volume"])
        config["hacking_background_volume"] = _validate_volume(config.get("hacking_background_volume"), DEFAULT_CONFIG["hacking_background_volume"])
        config["countdown_volume"] = _validate_volume(config.get("countdown_volume"), DEFAULT_CONFIG["countdown_volume"])
        
        # --- Boolean Validations ---
        config["enable_test_entries"] = bool(config.get("enable_test_entries", DEFAULT_CONFIG["enable_test_entries"]))
        config["multi_draw_enabled"] = bool(config.get("multi_draw_enabled", DEFAULT_CONFIG["multi_draw_enabled"]))
        config["ui_locked"] = bool(config.get("ui_locked", DEFAULT_CONFIG["ui_locked"]))

        # --- Geometry Validations ---
        geom_keys = [ "main_action_buttons_geometry", "top_controls_geometry", "entrants_panel_geometry", "main_stack_geometry"]
        for key in geom_keys:
            geom_val = config.get(key)
            if geom_val is not None and not _validate_geometry_string(geom_val):
                print(f"Warning: Invalid geometry string for '{key}': '{geom_val}'. Resetting to default.")
                config[key] = DEFAULT_CONFIG[key]
                config_changed = True
        
        # --- Animation Settings Validations ---
        loaded_anim_type = config.get("animation_type", DEFAULT_CONFIG["animation_type"])
        if loaded_anim_type not in VALID_ANIMATION_TYPES:
             print(f"Warning: Animation type '{loaded_anim_type}' is no longer selectable. Resetting to default '{DEFAULT_CONFIG['animation_type']}'.")
             config["animation_type"] = DEFAULT_CONFIG["animation_type"]
             config_changed = True
        
        # Validate all speed settings
        speed_validations = {
            "animation_trig_speed": VALID_TRIG_SPEEDS,
            "animation_node_path_speed": VALID_NODE_PATH_SPEEDS,
            "animation_trig_conduit_speed": VALID_TRIG_CONDUIT_SPEEDS,
            "animation_trig_code_reveal_speed": VALID_TRIG_CODE_REVEAL_SPEEDS,
        }
        for key, valid_values in speed_validations.items():
            loaded_speed = config.get(key, DEFAULT_CONFIG[key])
            if loaded_speed not in valid_values:
                print(f"Warning: Invalid speed for '{key}': '{loaded_speed}'. Resetting to default.")
                config[key] = DEFAULT_CONFIG[key]
                config_changed = True

        # --- Trig Code Validations ---
        tcl = config.get("animation_trig_code_length", DEFAULT_CONFIG["animation_trig_code_length"])
        try: config["animation_trig_code_length"] = int(tcl)
        except (ValueError, TypeError): config["animation_trig_code_length"] = DEFAULT_CONFIG["animation_trig_code_length"]
        if not (5 <= config["animation_trig_code_length"] <= 12):
            print(f"Warning: Invalid Triglavian code length '{config['animation_trig_code_length']}' found (must be 5-12). Resetting to default.")
            config["animation_trig_code_length"] = DEFAULT_CONFIG["animation_trig_code_length"]; config_changed = True

        char_set = config.get("animation_trig_code_char_set", DEFAULT_CONFIG["animation_trig_code_char_set"])
        if not isinstance(char_set, str) or not char_set:
            print(f"Warning: Invalid Triglavian code char set '{char_set}'. Resetting to default.");
            config["animation_trig_code_char_set"] = DEFAULT_CONFIG["animation_trig_code_char_set"]; config_changed = True
        
        tcfc = config.get("animation_trig_code_finalist_count", DEFAULT_CONFIG["animation_trig_code_finalist_count"])
        try: config["animation_trig_code_finalist_count"] = int(tcfc)
        except (ValueError, TypeError): config["animation_trig_code_finalist_count"] = DEFAULT_CONFIG["animation_trig_code_finalist_count"]
        if not (2 <= config["animation_trig_code_finalist_count"] <= 20):
            print(f"Warning: Invalid Triglavian code finalist count '{config['animation_trig_code_finalist_count']}' (must be 2-20). Resetting to default.")
            config["animation_trig_code_finalist_count"] = DEFAULT_CONFIG["animation_trig_code_finalist_count"]; config_changed = True
        
        # --- Prize/Poll Validations ---
        loaded_prize_options = config.get("prize_options", DEFAULT_CONFIG["prize_options"])
        if isinstance(loaded_prize_options, list):
            config["prize_options"] = [str(item) for item in loaded_prize_options if isinstance(item, str)]
        else:
            config["prize_options"] = DEFAULT_CONFIG["prize_options"]; config_changed = True

        loaded_common_prizes = config.get("common_prizes_list", DEFAULT_CONFIG["common_prizes_list"])
        if isinstance(loaded_common_prizes, list):
            config["common_prizes_list"] = [str(item) for item in loaded_common_prizes if isinstance(item, str)]
        else:
            config["common_prizes_list"] = DEFAULT_CONFIG["common_prizes_list"]; config_changed = True
        
        pt = config.get("poll_duration", DEFAULT_CONFIG["poll_duration"])
        try: config["poll_duration"] = int(pt)
        except (ValueError, TypeError): config["poll_duration"] = DEFAULT_CONFIG["poll_duration"]; config_changed = True
        if config["poll_duration"] <= 0: config["poll_duration"] = DEFAULT_CONFIG["poll_duration"]; config_changed = True

        loaded_prize_mode = config.get("prize_selection_mode", DEFAULT_CONFIG["prize_selection_mode"])
        if loaded_prize_mode not in VALID_PRIZE_MODES:
            print(f"Warning: Invalid prize_selection_mode '{loaded_prize_mode}'. Resetting to default '{DEFAULT_CONFIG['prize_selection_mode']}'.")
            config["prize_selection_mode"] = DEFAULT_CONFIG["prize_selection_mode"]; config_changed = True

        # --- Final check for changes and save if needed ---
        if config != original_config_before_validation:
             if config_path.exists(): 
                 print("Info: Configuration values were adjusted during loading/validation."); 
                 config_changed = True

        # Final check: window_geometry must be None post-load.
        if config.get("window_geometry") is not None:
            print("INFO (config_manager load): Forcing 'window_geometry' to None again after validations.")
            config["window_geometry"] = None
            config_changed = True 
        
        if config_changed:
            print("Info: Saving configuration file with defaults/validated/forced values.")
            save_config(config)

        return config

    except json.JSONDecodeError as e:
        print(f"ERROR decoding {config_path}: {e}. Using defaults and attempting to overwrite.")
        traceback.print_exc()
        config = DEFAULT_CONFIG.copy()
        config["customisable_ui_enabled"] = True
        config["window_geometry"] = None # Ensure it's None even on decode error
        save_config(config)
        return config
    except Exception as e:
        print(f"ERROR loading {config_path}: {e}. Using defaults.")
        traceback.print_exc()
        temp_default = DEFAULT_CONFIG.copy()
        temp_default["customisable_ui_enabled"] = True
        temp_default["window_geometry"] = None # Ensure it's None on other load errors
        return temp_default