"""
Voice Controller - Application Launcher
Awaz se apps open aur close karo.
"""

import subprocess
import os

from config import APP_ALIASES


class AppLauncher:
    """Open and close applications by voice command."""

    def __init__(self):
        print("[AppLauncher] Ready.")

    def open_app(self, app_name):
        """
        App open karo by name.
        Pehle APP_ALIASES mein dhundho, phir directly try karo.
        """
        app_name_lower = app_name.lower().strip()

        command = APP_ALIASES.get(app_name_lower)

        if command:
            return self._run_command(command, app_name_lower)

        for alias, cmd in APP_ALIASES.items():
            if alias in app_name_lower or app_name_lower in alias:
                return self._run_command(cmd, alias)

        return self._run_command(f"start {app_name}", app_name)

    def _run_command(self, command, display_name):
        """Command execute karo to open an app."""
        try:
            if command.startswith("start "):
                subprocess.Popen(
                    command, shell=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            print(f"[AppLauncher] Opening: {display_name}")
            return True
        except FileNotFoundError:
            print(f"[AppLauncher] App not found: {display_name}")
            return False
        except Exception as e:
            print(f"[AppLauncher] Error opening {display_name}: {e}")
            return False

    def close_window(self):
        """Current window close karo (Alt+F4)."""
        try:
            import pyautogui
            pyautogui.hotkey("alt", "f4")
            print("[AppLauncher] Closing current window.")
            return True
        except Exception as e:
            print(f"[AppLauncher] Close error: {e}")
            return False

    def minimize_window(self):
        """Current window minimize karo."""
        try:
            import pyautogui
            pyautogui.hotkey("win", "down")
            return True
        except Exception as e:
            print(f"[AppLauncher] Minimize error: {e}")
            return False

    def maximize_window(self):
        """Current window maximize karo."""
        try:
            import pyautogui
            pyautogui.hotkey("win", "up")
            return True
        except Exception as e:
            print(f"[AppLauncher] Maximize error: {e}")
            return False

    def switch_window(self):
        """Alt+Tab se window switch karo."""
        try:
            import pyautogui
            pyautogui.hotkey("alt", "tab")
            return True
        except Exception as e:
            print(f"[AppLauncher] Switch error: {e}")
            return False

    def open_folder(self, path):
        """Folder open karo in file explorer."""
        try:
            if os.path.exists(path):
                os.startfile(path)
                print(f"[AppLauncher] Opening folder: {path}")
                return True
            else:
                print(f"[AppLauncher] Folder not found: {path}")
                return False
        except Exception as e:
            print(f"[AppLauncher] Folder error: {e}")
            return False

    def open_website(self, url):
        """Browser mein website open karo."""
        try:
            import webbrowser
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)
            print(f"[AppLauncher] Opening: {url}")
            return True
        except Exception as e:
            print(f"[AppLauncher] Browser error: {e}")
            return False
