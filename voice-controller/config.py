"""
Voice Controller - Configuration & Command Mappings
Sari settings aur commands yahan hain. Apni marzi se change kar sakte ho.
"""

import json
import os

# --- General Settings ---
LANGUAGE = "en-US"          # "en-US" for English, "ur-PK" for Urdu
WAKE_WORD = "hello"         # Bot tab active hoga jab ye bolo (set None to disable)
MOUSE_STEP = 30             # Mouse kitne pixels move kare ek baar mein
MOUSE_FAST_STEP = 100       # Tez mouse movement (jab "fast" bolo)
LISTEN_TIMEOUT = 5          # Kitne seconds tak sune (seconds)
PHRASE_TIMEOUT = 10         # Ek phrase kitni der tak sun sakta hai
SPEECH_RATE = 170           # Bot kitni tezi se bole (words per minute)
SPEECH_VOLUME = 0.9         # Bot ki awaz kitni loud ho (0.0 to 1.0)
ENERGY_THRESHOLD = 300      # Microphone sensitivity (lower = more sensitive)
CONTINUOUS_LISTEN = True    # Continuously listen for commands

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMANDS_FILE = os.path.join(BASE_DIR, "commands.json")
LOG_FILE = os.path.join(BASE_DIR, "voice_controller.log")

# --- Built-in Command Mappings ---
# Ye sab default commands hain - tum commands.json se apne custom commands add kar sakte ho

MOUSE_COMMANDS = {
    "mouse up": "move_up",
    "mouse down": "move_down",
    "mouse left": "move_left",
    "mouse right": "move_right",
    "click": "left_click",
    "left click": "left_click",
    "right click": "right_click",
    "double click": "double_click",
    "scroll up": "scroll_up",
    "scroll down": "scroll_down",
    "drag": "start_drag",
    "drop": "stop_drag",
    "move fast up": "fast_move_up",
    "move fast down": "fast_move_down",
    "move fast left": "fast_move_left",
    "move fast right": "fast_move_right",
    "center mouse": "center_mouse",
}

KEYBOARD_COMMANDS = {
    "press enter": "enter",
    "press escape": "escape",
    "press tab": "tab",
    "press space": "space",
    "press backspace": "backspace",
    "press delete": "delete",
    "press up": "up",
    "press down": "down",
    "press left arrow": "left",
    "press right arrow": "right",
    "press home": "home",
    "press end": "end",
    "page up": "pageup",
    "page down": "pagedown",
    "press f5": "f5",
    "press f11": "f11",
}

SHORTCUT_COMMANDS = {
    "copy": ("ctrl", "c"),
    "paste": ("ctrl", "v"),
    "cut": ("ctrl", "x"),
    "undo": ("ctrl", "z"),
    "redo": ("ctrl", "y"),
    "select all": ("ctrl", "a"),
    "save": ("ctrl", "s"),
    "save as": ("ctrl", "shift", "s"),
    "new file": ("ctrl", "n"),
    "open file": ("ctrl", "o"),
    "print": ("ctrl", "p"),
    "find": ("ctrl", "f"),
    "replace": ("ctrl", "h"),
    "new tab": ("ctrl", "t"),
    "close tab": ("ctrl", "w"),
    "close window": ("alt", "f4"),
    "switch window": ("alt", "tab"),
    "minimize": ("win", "down"),
    "maximize": ("win", "up"),
    "show desktop": ("win", "d"),
    "lock screen": ("win", "l"),
    "screenshot": ("win", "shift", "s"),
    "task manager": ("ctrl", "shift", "escape"),
    "zoom in": ("ctrl", "plus"),
    "zoom out": ("ctrl", "minus"),
}

MEDIA_COMMANDS = {
    "play": "play_pause",
    "pause": "play_pause",
    "stop": "stop",
    "next track": "next_track",
    "previous track": "prev_track",
    "volume up": "volume_up",
    "volume down": "volume_down",
    "mute": "mute",
}

SYSTEM_COMMANDS = {
    "stop listening": "pause_listening",
    "start listening": "resume_listening",
    "exit": "exit_app",
    "quit": "exit_app",
    "goodbye": "exit_app",
    "help": "show_help",
    "what can you do": "show_help",
    "status": "show_status",
}

# --- Application shortcuts for "open [app]" ---
APP_ALIASES = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "browser": "start chrome",
    "chrome": "start chrome",
    "firefox": "start firefox",
    "edge": "start msedge",
    "file manager": "explorer.exe",
    "explorer": "explorer.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "cmd.exe",
    "word": "start winword",
    "excel": "start excel",
    "powerpoint": "start powerpnt",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "settings": "start ms-settings:",
    "snipping tool": "snippingtool.exe",
    "media player": "start wmplayer",
    "vlc": "start vlc",
}


def load_custom_commands():
    """commands.json se custom commands load karo."""
    if os.path.exists(COMMANDS_FILE):
        try:
            with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"[WARNING] commands.json load error: {e}")
    return {}


def get_all_commands():
    """Sab commands ek dictionary mein merge kar ke do."""
    all_cmds = {}
    all_cmds.update({k: ("mouse", v) for k, v in MOUSE_COMMANDS.items()})
    all_cmds.update({k: ("keyboard", v) for k, v in KEYBOARD_COMMANDS.items()})
    all_cmds.update({k: ("shortcut", v) for k, v in SHORTCUT_COMMANDS.items()})
    all_cmds.update({k: ("media", v) for k, v in MEDIA_COMMANDS.items()})
    all_cmds.update({k: ("system", v) for k, v in SYSTEM_COMMANDS.items()})

    custom = load_custom_commands()
    if "commands" in custom:
        for cmd_name, cmd_action in custom["commands"].items():
            all_cmds[cmd_name.lower()] = ("custom", cmd_action)

    return all_cmds
