# logging_utils.py
import os
import time
import traceback
import uuid
import json
from pathlib import Path
from datetime import datetime

import requests # Needs to be installed if not already: pip install requests
from PyQt6.QtCore import QStandardPaths, QTimer # QTimer for deferred GA sending

# --- Constants needed for logging ---
# These could also be passed as arguments or imported from a central constants file
APP_NAME_LOG = "RustyBotGiveaway" # Using a distinct name to avoid conflict if Main.py also defines it
APP_VERSION_LOG = "1.2.4" # Ensure this matches the version in Main.py or is managed centrally
ACTIVITY_LOG_FILE = "activity_log.txt"

# --- Google Analytics Client ID Management ---
_ga_client_id_cache = None
_ga_config_ref = None # Reference to the main app's config dictionary

def init_ga_config_ref(config_dict):
    """
    Call this once from Main.py to provide a reference to the main config
    for GA client ID persistence.
    """
    global _ga_config_ref
    _ga_config_ref = config_dict

def _ensure_ga_client_id():
    """Ensures a client ID exists in config, generating one if not."""
    global _ga_client_id_cache, _ga_config_ref
    if _ga_client_id_cache:
        return _ga_client_id_cache

    if _ga_config_ref:
        client_id_from_config = _ga_config_ref.get("ga_client_id")
        if client_id_from_config:
            _ga_client_id_cache = client_id_from_config
            return _ga_client_id_cache

    # Generate new if not found or config ref not set yet (should be set by app start)
    new_client_id = str(uuid.uuid4())
    _ga_client_id_cache = new_client_id
    print(f"LOGGING_UTILS (GA): Generated new client_id: {new_client_id}")
    
    if _ga_config_ref:
        _ga_config_ref["ga_client_id"] = new_client_id
        # Defer saving of config to the main application's logic
        # (e.g., when options are saved or app closes)
        print(f"LOGGING_UTILS (GA): Client ID set in provided config reference. Main app should save.")
    else:
        print("LOGGING_UTILS (GA) WARN: Config reference not set. New Client ID not persisted in config immediately.")
    return new_client_id


# --- Local Activity Logging ---
def log_activity(event_type: str, details: str = ""):
    try:
        data_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if not data_dir_str:
            data_dir_str = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.GenericDataLocation)
            if not data_dir_str: # Should ideally use ORG_NAME/APP_NAME here if available
                print("ERROR (Local Activity Log): Could not find writable application data directory.")
                return
        # If ORG_NAME and APP_NAME are needed, they should be passed or imported
        app_data_dir = Path(data_dir_str) / "RustyBit" / "RustyBotGiveaway" 
        app_data_dir.mkdir(parents=True, exist_ok=True)
        log_path = app_data_dir / ACTIVITY_LOG_FILE
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_entry = f"{timestamp}\t{event_type}"
        if details: 
            log_entry += f"\t{details}"
        log_entry += "\n"
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        target_path_str = str(log_path) if 'log_path' in locals() else ACTIVITY_LOG_FILE
        print(f"ERROR (Local Activity Log): Could not write to {target_path_str}: {e}")

# --- Remote Logging ---
def send_remote_log(config: dict, event_type: str, data: dict = None):
    if not config.get("remote_logging_enabled", False):
        return
    url = config.get("remote_logging_url")
    api_key = config.get("remote_logging_api_key") 
    if not url:
        return
    
    payload = {
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "app_name": APP_NAME_LOG,
        "app_version": APP_VERSION_LOG,
        "data": data or {},
    }
    headers = {"Content-Type": "application/json"}
    if api_key: headers["X-API-Key"] = api_key 
    
    def send_request_thread_func(): # Renamed to avoid conflict
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code >= 300:
                print(f"WARN (Remote Log): Failed to send log to {url}. Status: {response.status_code}, Response: {response.text[:200]}")
        except requests.exceptions.Timeout: print(f"ERROR (Remote Log): Timeout sending log to {url}.")
        except requests.exceptions.RequestException as e: print(f"ERROR (Remote Log): Network error sending log to {url}: {e}")
        except Exception as e: print(f"ERROR (Remote Log): Unexpected error sending log: {e}"); traceback.print_exc()

    # For remote logging, direct threading might be okay, or use QTimer for a slight delay
    # if running directly from a signal handler could block UI.
    # Using QTimer.singleShot(0, ...) to run it in the next event loop iteration.
    QTimer.singleShot(0, send_request_thread_func)


# --- Google Analytics Event Sending ---
_ga_warning_shown_internal = False # Internal flag for this module

def send_ga_event(config: dict, event_name: str, event_params: dict = None, status_logger_func=None):
    global _ga_warning_shown_internal
    if not config.get("google_analytics_enabled", False):
        return

    measurement_id = config.get("ga_measurement_id")
    api_secret = config.get("ga_api_secret")
    
    if not measurement_id or not api_secret:
        if not _ga_warning_shown_internal:
            print("LOGGING_UTILS (GA) WARN: Measurement ID or API Secret not configured. GA tracking disabled.")
            if status_logger_func: status_logger_func("GA WARN: Analytics not configured in Options.")
            _ga_warning_shown_internal = True
        return
    
    if _ga_warning_shown_internal and measurement_id and api_secret:
        _ga_warning_shown_internal = False

    client_id = _ensure_ga_client_id() # Uses the shared config reference
    if not client_id:
        print("LOGGING_UTILS (GA) ERROR: Could not get or generate client_id.")
        return

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={measurement_id}&api_secret={api_secret}"
    
    default_params = {
        "event_category": "GiveawayApp", 
        "app_version": APP_VERSION_LOG,
    }
    if event_params:
        default_params.update(event_params)

    payload = {
        "client_id": client_id,
        "non_personalized_ads": False, 
        "events": [{
            "name": event_name,
            "params": default_params
        }]
    }

    def send_request_thread_func(): # Renamed
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code == 204:
                print(f"LOGGING_UTILS (GA): Event '{event_name}' sent successfully. Params: {default_params}")
            else:
                print(f"LOGGING_UTILS (GA) ERROR: Failed to send event '{event_name}'. Status: {response.status_code}, Response: {response.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"LOGGING_UTILS (GA) ERROR: Network error sending event '{event_name}': {e}")
        except Exception as e:
            print(f"LOGGING_UTILS (GA) ERROR: Unexpected error sending event '{event_name}': {e}")

    # Use QTimer.singleShot for GA as well to avoid blocking if called from UI thread
    QTimer.singleShot(0, send_request_thread_func)