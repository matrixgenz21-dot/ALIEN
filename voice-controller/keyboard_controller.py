"""
Voice Controller - Keyboard Control Module
Awaz se keyboard use karo - type karo, keys dabao, shortcuts use karo.
"""

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

from config import SHORTCUT_COMMANDS


class KeyboardController:
    """Keyboard typing, key presses, and shortcuts."""

    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            print("[KeyboardController] pyautogui not installed!")
            print("                     Install with: pip install pyautogui")

    def _check(self):
        if not PYAUTOGUI_AVAILABLE:
            print("[KeyboardController] pyautogui not available.")
            return False
        return True

    def type_text(self, text):
        """Text type karo keyboard se — insaan ki tarha slowly."""
        if not self._check():
            return
        for char in text:
            if char.isascii() and char.isprintable():
                pyautogui.press(char)
            else:
                import pyperclip
                pyperclip.copy(char)
                pyautogui.hotkey("ctrl", "v")
            import time
            time.sleep(0.05)

    def type_unicode(self, text):
        """Unicode text type karo (Urdu etc. ke liye)."""
        if not self._check():
            return
        import pyperclip
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")

    def press_key(self, key):
        """Ek key press karo."""
        if not self._check():
            return
        key_map = {
            "enter": "enter",
            "escape": "escape",
            "esc": "escape",
            "tab": "tab",
            "space": "space",
            "backspace": "backspace",
            "delete": "delete",
            "up": "up",
            "down": "down",
            "left": "left",
            "right": "right",
            "home": "home",
            "end": "end",
            "pageup": "pageup",
            "pagedown": "pagedown",
            "f1": "f1",
            "f2": "f2",
            "f3": "f3",
            "f4": "f4",
            "f5": "f5",
            "f6": "f6",
            "f7": "f7",
            "f8": "f8",
            "f9": "f9",
            "f10": "f10",
            "f11": "f11",
            "f12": "f12",
        }
        mapped = key_map.get(key.lower(), key.lower())
        try:
            pyautogui.press(mapped)
        except Exception as e:
            print(f"[KeyboardController] Key press error: {e}")

    def hotkey(self, *keys):
        """Shortcut keys dabao (e.g., ctrl+c)."""
        if not self._check():
            return
        key_map = {
            "ctrl": "ctrl",
            "alt": "alt",
            "shift": "shift",
            "win": "win",
            "plus": "+",
            "minus": "-",
        }
        mapped_keys = [key_map.get(k.lower(), k.lower()) for k in keys]
        try:
            pyautogui.hotkey(*mapped_keys)
        except Exception as e:
            print(f"[KeyboardController] Hotkey error ({'+'.join(mapped_keys)}): {e}")

    def execute_shortcut(self, shortcut_name):
        """Named shortcut execute karo from config."""
        keys = SHORTCUT_COMMANDS.get(shortcut_name)
        if keys:
            self.hotkey(*keys)
            return True
        return False

    def execute(self, action):
        """Action string se key press karo."""
        self.press_key(action)
        return True
