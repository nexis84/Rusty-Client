"""
RustyBot Launcher - Checks for updates and starts the main application
"""
import sys
import os
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
import threading

# Try to import auto_updater
try:
    from auto_updater import AutoUpdater
    UPDATER_AVAILABLE = True
except ImportError:
    UPDATER_AVAILABLE = False
    print("Warning: auto_updater module not found. Update checking disabled.")


class UpdateDialog:
    """Simple dialog to show update availability and progress"""
    
    def __init__(self, current_version, new_version, release_notes):
        self.result = False
        self.root = tk.Tk()
        self.root.title("RustyBot Update Available")
        self.root.geometry("500x350")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.root.winfo_screenheight() // 2) - (350 // 2)
        self.root.geometry(f"500x350+{x}+{y}")
        
        # Header
        header_frame = tk.Frame(self.root, bg="#2b2b2b", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎉 Update Available!", 
                              font=("Arial", 16, "bold"), 
                              bg="#2b2b2b", fg="white")
        title_label.pack(pady=15)
        
        # Content
        content_frame = tk.Frame(self.root, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        version_text = f"Version {new_version} is now available!\n(You have version {current_version})"
        version_label = tk.Label(content_frame, text=version_text,
                                font=("Arial", 11), bg="white", fg="#333")
        version_label.pack(pady=(0, 10))
        
        # Release notes
        notes_label = tk.Label(content_frame, text="What's New:",
                              font=("Arial", 10, "bold"), bg="white", fg="#333")
        notes_label.pack(anchor="w")
        
        notes_frame = tk.Frame(content_frame, bg="white")
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 15))
        
        notes_text = tk.Text(notes_frame, wrap=tk.WORD, height=8,
                            font=("Arial", 9), bg="#f5f5f5", relief=tk.FLAT, padx=10, pady=10)
        notes_text.insert("1.0", release_notes or "No release notes available.")
        notes_text.config(state=tk.DISABLED)
        notes_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg="white")
        button_frame.pack(fill=tk.X)
        
        update_btn = tk.Button(button_frame, text="Download & Install", 
                              command=self.accept, bg="#4CAF50", fg="white",
                              font=("Arial", 10, "bold"), relief=tk.FLAT,
                              padx=20, pady=8, cursor="hand2")
        update_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        skip_btn = tk.Button(button_frame, text="Skip This Version",
                           command=self.decline, bg="#757575", fg="white",
                           font=("Arial", 10), relief=tk.FLAT,
                           padx=20, pady=8, cursor="hand2")
        skip_btn.pack(side=tk.LEFT)
        
        self.root.protocol("WM_DELETE_WINDOW", self.decline)
        
    def accept(self):
        self.result = True
        self.root.destroy()
        
    def decline(self):
        self.result = False
        self.root.destroy()
        
    def show(self):
        self.root.mainloop()
        return self.result


class DownloadProgressDialog:
    """Dialog to show download and installation progress"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Updating RustyBot")
        self.root.geometry("400x150")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (150 // 2)
        self.root.geometry(f"400x150+{x}+{y}")
        
        # Content
        content_frame = tk.Frame(self.root, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.status_label = tk.Label(content_frame, text="Downloading update...",
                                     font=("Arial", 11), bg="white", fg="#333")
        self.status_label.pack(pady=(10, 10))
        
        self.progress_bar = ttk.Progressbar(content_frame, mode='determinate', length=350)
        self.progress_bar.pack(pady=(0, 10))
        
        self.percent_label = tk.Label(content_frame, text="0%",
                                      font=("Arial", 9), bg="white", fg="#666")
        self.percent_label.pack()
        
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close
        
    def update_progress(self, percent):
        self.progress_bar['value'] = percent
        self.percent_label.config(text=f"{percent}%")
        self.root.update()
        
    def update_status(self, status):
        self.status_label.config(text=status)
        self.root.update()
        
    def close(self):
        self.root.destroy()


def check_for_updates():
    """Check for updates and prompt user"""
    if not UPDATER_AVAILABLE:
        return False
    
    try:
        updater = AutoUpdater()
        has_update, latest_version, release_notes = updater.check_for_updates()
        
        if has_update:
            # Show update dialog
            dialog = UpdateDialog(updater.current_version, latest_version, release_notes)
            user_wants_update = dialog.show()
            
            if user_wants_update:
                # Show progress dialog
                progress = DownloadProgressDialog()
                
                # Download update
                success, result = updater.download_update(progress_callback=progress.update_progress)
                
                if success:
                    progress.update_status("Installing update...")
                    progress.update_progress(100)
                    
                    # Apply update (this will exit the launcher)
                    success, message = updater.apply_update(result)
                    
                    if not success:
                        progress.close()
                        messagebox.showerror("Update Failed", f"Failed to install update:\n{message}")
                        return False
                    
                    # If we reach here, update failed to exit properly
                    progress.close()
                    return True
                else:
                    progress.close()
                    messagebox.showerror("Download Failed", f"Failed to download update:\n{result}")
                    return False
        
        return False
        
    except Exception as e:
        print(f"Update check error: {e}")
        return False


def main():
    """Launcher main function - checks for updates then starts RustyBot"""
    try:
        # Get the directory where this launcher is located
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = Path(sys.executable).parent
        else:
            # Running as script
            app_dir = Path(__file__).parent
        
        # Path to the main RustyBot executable
        # First try dist/ directory (where PyInstaller puts executables)
        rustybot_exe = app_dir / "dist" / "RustyBot.exe"
        
        # If not found in dist/, try same directory as launcher
        if not rustybot_exe.exists():
            rustybot_exe = app_dir / "RustyBot.exe"
        
        if not rustybot_exe.exists():
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"RustyBot.exe not found at:\n{rustybot_exe}")
            return 1
        
        # Check for updates (non-blocking, quick check)
        print("Checking for updates...")
        update_applied = check_for_updates()
        
        # If update was applied, the updater will restart the app
        # So we should not reach this point. If we do, it means no update or user declined
        if not update_applied:
            # Launch RustyBot
            print("Starting RustyBot...")
            subprocess.Popen([str(rustybot_exe)], cwd=str(app_dir))
        
        return 0
        
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Error launching RustyBot:\n{e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
