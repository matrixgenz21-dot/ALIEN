"""
Voice Controller - Media Playback Controls
Awaz se media control karo - play, pause, volume, next/previous track.
"""

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False


class MediaController:
    """Media keys through keyboard simulation."""

    def __init__(self):
        if not PYAUTOGUI_AVAILABLE:
            print("[MediaController] pyautogui not installed!")

    def _check(self):
        if not PYAUTOGUI_AVAILABLE:
            return False
        return True

    def play_pause(self):
        if not self._check():
            return
        pyautogui.press("playpause")

    def stop(self):
        if not self._check():
            return
        pyautogui.press("stop")

    def next_track(self):
        if not self._check():
            return
        pyautogui.press("nexttrack")

    def prev_track(self):
        if not self._check():
            return
        pyautogui.press("prevtrack")

    def volume_up(self):
        if not self._check():
            return
        pyautogui.press("volumeup")
        pyautogui.press("volumeup")
        pyautogui.press("volumeup")

    def volume_down(self):
        if not self._check():
            return
        pyautogui.press("volumedown")
        pyautogui.press("volumedown")
        pyautogui.press("volumedown")

    def mute(self):
        if not self._check():
            return
        pyautogui.press("volumemute")

    def execute(self, action):
        """Action string se media command execute karo."""
        action_map = {
            "play_pause": self.play_pause,
            "stop": self.stop,
            "next_track": self.next_track,
            "prev_track": self.prev_track,
            "volume_up": self.volume_up,
            "volume_down": self.volume_down,
            "mute": self.mute,
        }
        fn = action_map.get(action)
        if fn:
            fn()
            return True
        return False
