# -*- coding: utf-8 -*-
# Sound Manager for EVE Giveaway Tool

import os
from pathlib import Path
import traceback

try:
    import pygame
    pygame_available = True
except ImportError:
    pygame_available = False
    pygame = None

# --- Sound File Configuration ---
# (sound_key: (filename, default_volume_multiplier, category))
SOUND_FILES = {
    "animation_start": ("Hacking in progress.mp3", 0.7, "hacking_bg"), 
    # "reel_loop": ("Reel_Loop.wav", 0.6, "hacking_bg"), # <<< MODIFIED: Removed
    "winner": ("Winner_Selected.wav", 0.8, "ai_voice"),          
    "verified": ("Verified.wav", 0.9, "ai_voice"),              
    "fail": ("Fail.wav", 0.8, "warning"),                      
    "notification": ("Notification.mp3", 0.7, "general"),      
    "countdown": ("Countdown.wav", 1.0, "countdown"),          
    "timer_high": ("Timer_Shield.mp3", 1.0, "warning"),         
    "timer_mid": ("Timer_Armor.mp3", 1.0, "warning"),          
    "timer_low": ("Timer_Hull.mp3", 1.0, "warning"),           
    "wheel_tick": ("wheel_tick.wav", 0.6, "general"), 
    "conduit_stable": ("Conduit_Stable.wav", 0.8, "ai_voice"), # Added key from script.js options
}

CATEGORY_TO_CONFIG_VOLUME_KEY = {
    "ai_voice": "ai_voice_volume",
    "warning": "warning_sounds_volume",
    "hacking_bg": "hacking_background_volume",
    "countdown": "countdown_volume",
    "general": "master_volume" 
}


class SoundManager:
    def __init__(self, config, base_path="sounds"):
        self.config = config
        self.sounds = {}
        self.playing_channels = {} 
        self.base_path = Path(base_path)
        self.is_initialized = False

        if not pygame_available:
            print("SOUND_DEBUG: Pygame not available. SoundManager will be disabled.")
            return

        try:
            pygame.mixer.init()
            num_channels_to_try = [32, 24, 16, 8]
            for num_c in num_channels_to_try:
                try:
                    pygame.mixer.set_num_channels(num_c)
                    print(f"SOUND_DEBUG: Pygame Mixer initialized with {pygame.mixer.get_num_channels()} channels.")
                    self.is_initialized = True
                    break
                except pygame.error as e:
                    print(f"SOUND_DEBUG: Failed to set {num_c} channels: {e}")
            if not self.is_initialized:
                 print("SOUND_DEBUG: Pygame Mixer could not be initialized. Sound disabled.")
                 pygame.mixer.quit()
                 return
            self._load_sounds()
        except pygame.error as e:
            print(f"SOUND_DEBUG: Pygame mixer initialization error: {e}")
            traceback.print_exc()
            self.is_initialized = False
        except Exception as e:
            print(f"SOUND_DEBUG: Unexpected error during SoundManager init: {e}")
            traceback.print_exc()
            self.is_initialized = False

    def _load_sounds(self):
        if not self.is_initialized: return
        print("SOUND_DEBUG: Loading sounds...")
        for key, (filename, _, _) in SOUND_FILES.items():
            path = self.base_path / filename
            if path.is_file():
                try:
                    self.sounds[key] = pygame.mixer.Sound(str(path))
                    print(f"SOUND_DEBUG: Loaded sound '{key}' from '{path}'")
                except pygame.error as e:
                    print(f"SOUND_DEBUG: Error loading sound '{key}' from '{path}': {e}")
                    self.sounds[key] = None
            else:
                print(f"SOUND_DEBUG: Sound file not found for '{key}': '{path}'")
                self.sounds[key] = None
        print("SOUND_DEBUG: Sound loading complete.")

    def _calculate_volume(self, sound_key):
        if sound_key not in SOUND_FILES:
            return self.config.get("master_volume", 0.75)

        _, default_vol_multiplier, category = SOUND_FILES[sound_key]
        master_volume = self.config.get("master_volume", 0.75)
        category_volume_key = CATEGORY_TO_CONFIG_VOLUME_KEY.get(category, "master_volume")
        category_volume_level = self.config.get(category_volume_key, 1.0)

        if category_volume_key == "master_volume":
             effective_volume = master_volume * default_vol_multiplier
        else:
             effective_volume = master_volume * category_volume_level * default_vol_multiplier
        final_volume = max(0.0, min(1.0, effective_volume))

        if sound_key == "countdown":
            print(f"SOUND_DEBUG (countdown volume calc): Key='{sound_key}', DefMultiplier={default_vol_multiplier:.2f}, Category='{category}'")
            print(f"SOUND_DEBUG (countdown volume calc): MasterVol={master_volume:.2f}, CatVolKey='{category_volume_key}', CatVolLevel={category_volume_level:.2f}")
            print(f"SOUND_DEBUG (countdown volume calc): EffectiveVol(pre-clamp)={effective_volume:.2f}, FinalVol={final_volume:.2f}")
        return final_volume

    def play(self, key, loops=0, maxtime=0, fade_ms=0):
        if not self.is_initialized or key not in self.sounds or self.sounds[key] is None:
            if not self.is_initialized: print(f"Warning: Sound system not initialized. Cannot play '{key}'.")
            elif key not in self.sounds : print(f"Warning: Sound key '{key}' not found in sound_files config.")
            elif self.sounds[key] is None: print(f"Warning: Sound '{key}' was not loaded (file missing or error). Cannot play.")
            return None

        sound_obj = self.sounds[key]
        volume = self._calculate_volume(key)
        sound_obj.set_volume(volume)

        if key == "countdown":
            print(f"SOUND_DEBUG: Attempting to play 'countdown'. Volume set to {volume:.2f}, loops={loops}")

        try:
            if key in self.playing_channels and self.playing_channels[key].get_sound() == sound_obj:
                if self.playing_channels[key].get_busy():
                    print(f"SOUND_DEBUG: Sound '{key}' is already playing on channel {self.playing_channels[key]}. Stopping before replay.")
                    self.playing_channels[key].stop()

            channel = pygame.mixer.find_channel(True) 
            if channel:
                if key == "countdown":
                    print(f"SOUND_DEBUG: Playing '{key}' on channel {channel} with volume {volume:.2f}, loops={loops}")
                self.playing_channels[key] = channel
                channel.play(sound_obj, loops=loops, maxtime=maxtime, fade_ms=fade_ms)
                return channel
            else:
                print(f"SOUND_DEBUG: No available channels to play '{key}'.")
                return None
        except pygame.error as e:
            print(f"SOUND_DEBUG: Pygame error playing sound '{key}': {e}")
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"SOUND_DEBUG: Unexpected error playing sound '{key}': {e}")
            traceback.print_exc()
            return None

    def stop(self, key):
        if not self.is_initialized or key not in self.sounds or self.sounds[key] is None:
            return

        sound_obj = self.sounds[key]
        if key == "countdown":
            print(f"SOUND_DEBUG: Stop requested for 'countdown'.")

        if key in self.playing_channels:
            channel = self.playing_channels[key]
            if channel.get_sound() == sound_obj and channel.get_busy():
                channel.stop()
                if key == "countdown": print(f"SOUND_DEBUG: Stopped '{key}' via tracked channel {channel}.")
                return 

        stopped_fallback = False
        for i in range(pygame.mixer.get_num_channels()):
            channel = pygame.mixer.Channel(i)
            if channel.get_sound() == sound_obj and channel.get_busy():
                channel.stop()
                if key == "countdown": print(f"SOUND_DEBUG: Stopped '{key}' via fallback channel iteration on channel {i}.")
                stopped_fallback = True
                break

        if key == "countdown" and not stopped_fallback and key not in self.playing_channels:
             print(f"SOUND_DEBUG: '{key}' stop called, but not found playing on tracked or iterated channels.")
        
        if key in self.playing_channels:
            del self.playing_channels[key]

    def stop_all(self):
        if not self.is_initialized: return
        print("SOUND_DEBUG: Stopping all sounds.")
        pygame.mixer.stop()
        self.playing_channels.clear() 

    def set_master_volume(self, volume):
        if not self.is_initialized: return
        self.config['master_volume'] = max(0.0, min(1.0, volume))
        print(f"SOUND_DEBUG: Master volume in config set to {self.config['master_volume']:.2f}")
        self.apply_volumes_to_playing_sounds()

    def apply_volumes(self, new_config):
        if not self.is_initialized: return
        self.config = new_config
        print("SOUND_DEBUG: SoundManager config updated. Re-applying volumes.")
        self.apply_volumes_to_playing_sounds()

    def apply_volumes_to_playing_sounds(self):
        if not self.is_initialized: return
        for sound_key, channel in list(self.playing_channels.items()):
            if channel.get_busy():
                if self.sounds.get(sound_key):
                    new_volume = self._calculate_volume(sound_key)
                    self.sounds[sound_key].set_volume(new_volume)
                    channel.set_volume(new_volume)
                    if sound_key == "countdown": 
                        print(f"SOUND_DEBUG: Re-applied volume to playing 'countdown' on channel {channel}: {new_volume:.2f}")
                else:
                    print(f"SOUND_DEBUG: Warning - Sound key '{sound_key}' in playing_channels but not loaded.")
            else:
                del self.playing_channels[sound_key]


    def get_sound_path(self, key):
        if key in SOUND_FILES:
            return self.base_path / SOUND_FILES[key][0]
        return None

    def quit(self):
        if pygame_available and self.is_initialized:
            print("SOUND_DEBUG: Quitting Pygame mixer.")
            pygame.mixer.quit()
            self.is_initialized = False