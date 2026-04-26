"""
Voice Controller - Mouse Control Module
Awaz se mouse ko control karo - move, click, scroll, drag.
"""

try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

from config import MOUSE_STEP, MOUSE_FAST_STEP


class MouseController:
    """Mouse movement, clicks, scrolling aur dragging."""

    def __init__(self):
        self._dragging = False
        if not PYAUTOGUI_AVAILABLE:
            print("[MouseController] pyautogui not installed!")
            print("                  Install with: pip install pyautogui")

    def _check(self):
        if not PYAUTOGUI_AVAILABLE:
            print("[MouseController] pyautogui not available.")
            return False
        return True

    def get_position(self):
        """Current mouse position return karo."""
        if not self._check():
            return (0, 0)
        return pyautogui.position()

    def get_screen_size(self):
        """Screen size return karo."""
        if not self._check():
            return (1920, 1080)
        return pyautogui.size()

    # --- Movement ---
    def move_up(self, step=None):
        if not self._check():
            return
        pyautogui.moveRel(0, -(step or MOUSE_STEP), duration=0.1)

    def move_down(self, step=None):
        if not self._check():
            return
        pyautogui.moveRel(0, step or MOUSE_STEP, duration=0.1)

    def move_left(self, step=None):
        if not self._check():
            return
        pyautogui.moveRel(-(step or MOUSE_STEP), 0, duration=0.1)

    def move_right(self, step=None):
        if not self._check():
            return
        pyautogui.moveRel(step or MOUSE_STEP, 0, duration=0.1)

    def fast_move_up(self):
        self.move_up(MOUSE_FAST_STEP)

    def fast_move_down(self):
        self.move_down(MOUSE_FAST_STEP)

    def fast_move_left(self):
        self.move_left(MOUSE_FAST_STEP)

    def fast_move_right(self):
        self.move_right(MOUSE_FAST_STEP)

    def center_mouse(self):
        """Mouse ko screen ke center mein le jao."""
        if not self._check():
            return
        w, h = pyautogui.size()
        pyautogui.moveTo(w // 2, h // 2, duration=0.3)

    def move_to(self, x, y):
        """Mouse ko specific position pe le jao."""
        if not self._check():
            return
        pyautogui.moveTo(x, y, duration=0.2)

    # --- Clicks ---
    def left_click(self):
        if not self._check():
            return
        pyautogui.click()

    def right_click(self):
        if not self._check():
            return
        pyautogui.rightClick()

    def double_click(self):
        if not self._check():
            return
        pyautogui.doubleClick()

    def triple_click(self):
        if not self._check():
            return
        pyautogui.tripleClick()

    # --- Scroll ---
    def scroll_up(self, amount=3):
        if not self._check():
            return
        pyautogui.scroll(amount)

    def scroll_down(self, amount=3):
        if not self._check():
            return
        pyautogui.scroll(-amount)

    # --- Drag ---
    def start_drag(self):
        """Drag start karo (mouse button hold)."""
        if not self._check():
            return
        pyautogui.mouseDown()
        self._dragging = True
        print("[MouseController] Drag started. Say 'drop' to release.")

    def stop_drag(self):
        """Drag end karo (mouse button release)."""
        if not self._check():
            return
        pyautogui.mouseUp()
        self._dragging = False
        print("[MouseController] Drag ended.")

    @property
    def is_dragging(self):
        return self._dragging

    def execute(self, action):
        """Action string se corresponding method call karo."""
        action_map = {
            "move_up": self.move_up,
            "move_down": self.move_down,
            "move_left": self.move_left,
            "move_right": self.move_right,
            "left_click": self.left_click,
            "right_click": self.right_click,
            "double_click": self.double_click,
            "scroll_up": self.scroll_up,
            "scroll_down": self.scroll_down,
            "start_drag": self.start_drag,
            "stop_drag": self.stop_drag,
            "fast_move_up": self.fast_move_up,
            "fast_move_down": self.fast_move_down,
            "fast_move_left": self.fast_move_left,
            "fast_move_right": self.fast_move_right,
            "center_mouse": self.center_mouse,
        }
        fn = action_map.get(action)
        if fn:
            fn()
            return True
        return False
