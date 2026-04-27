"""
Voice Controller - Command Parser
Voice text ko samajh ke sahi action pe map karo.
"""

import re

from config import (
    get_all_commands,
    MOUSE_COMMANDS,
    KEYBOARD_COMMANDS,
    SHORTCUT_COMMANDS,
    MEDIA_COMMANDS,
    SYSTEM_COMMANDS,
    WAKE_WORD,
)


class CommandParser:
    """Parse recognized speech into actionable commands."""

    def __init__(self):
        self._commands = get_all_commands()
        self._wake_active = WAKE_WORD is None

    def reload_commands(self):
        """Reload command mappings (e.g., after editing commands.json)."""
        self._commands = get_all_commands()
        print("[CommandParser] Commands reloaded.")

    def parse(self, text):
        """
        Text se command parse karo.

        Returns: dict with keys:
            - "type": command category (mouse/keyboard/shortcut/media/system/type/open/website/unknown)
            - "action": the action to execute
            - "args": optional arguments (e.g., text to type, app name)
            - "raw": original text
        """
        if not text:
            return None

        text = text.lower().strip()

        if WAKE_WORD and not self._wake_active:
            if WAKE_WORD.lower() in text:
                self._wake_active = True
                return {
                    "type": "system",
                    "action": "wake",
                    "args": None,
                    "raw": text,
                }
            return None

        if WAKE_WORD and text.startswith(WAKE_WORD.lower()):
            text = text[len(WAKE_WORD):].strip()

        if text in ("go to sleep", "sleep mode"):
            self._wake_active = False
            return {
                "type": "system",
                "action": "sleep_mode",
                "args": None,
                "raw": text,
            }

        # 1) Exact match against known commands first (system, shortcuts, etc.)
        for cmd_text, (cmd_type, cmd_action) in self._commands.items():
            if cmd_text == text:
                return {
                    "type": cmd_type,
                    "action": cmd_action,
                    "args": None,
                    "raw": text,
                }

        # 2) Special pattern-based commands (order matters)
        result = self._check_type_command(text)
        if result:
            return result

        result = self._check_website_command(text)
        if result:
            return result

        result = self._check_open_command(text)
        if result:
            return result

        result = self._check_move_to_command(text)
        if result:
            return result

        result = self._check_repeat_command(text)
        if result:
            return result

        # 3) Partial/prefix match against known commands
        for cmd_text, (cmd_type, cmd_action) in self._commands.items():
            if text.startswith(cmd_text):
                return {
                    "type": cmd_type,
                    "action": cmd_action,
                    "args": None,
                    "raw": text,
                }

        for cmd_text, (cmd_type, cmd_action) in self._commands.items():
            if cmd_text in text:
                return {
                    "type": cmd_type,
                    "action": cmd_action,
                    "args": None,
                    "raw": text,
                }

        return {
            "type": "unknown",
            "action": None,
            "args": text,
            "raw": text,
        }

    def _check_type_command(self, text):
        """'type [something]' command check karo."""
        patterns = [
            r"^type\s+(.+)$",
            r"^write\s+(.+)$",
            r"^likh\s+(.+)$",
            r"^likho\s+(.+)$",
        ]
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                return {
                    "type": "type",
                    "action": "type_text",
                    "args": match.group(1),
                    "raw": text,
                }
        return None

    def _check_open_command(self, text):
        """'open [app]' command check karo."""
        patterns = [
            r"^open\s+(.+)$",
            r"^launch\s+(.+)$",
            r"^start\s+(.+)$",
            r"^run\s+(.+)$",
            r"^kholo\s+(.+)$",
        ]
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                return {
                    "type": "open",
                    "action": "open_app",
                    "args": match.group(1),
                    "raw": text,
                }
        return None

    def _check_website_command(self, text):
        """'go to [url]' command check karo."""
        patterns = [
            r"^go to\s+(.+)$",
            r"^open website\s+(.+)$",
            r"^browse\s+(.+)$",
            r"^visit\s+(.+)$",
        ]
        for pattern in patterns:
            match = re.match(pattern, text)
            if match:
                target = match.group(1)
                if "." in target or "www" in target or "http" in target:
                    return {
                        "type": "website",
                        "action": "open_website",
                        "args": target,
                        "raw": text,
                    }
        return None

    def _check_move_to_command(self, text):
        """'move mouse to [x] [y]' command check karo."""
        match = re.match(r"move (?:mouse )?to (\d+)\s+(\d+)", text)
        if match:
            return {
                "type": "mouse",
                "action": "move_to",
                "args": (int(match.group(1)), int(match.group(2))),
                "raw": text,
            }
        return None

    def _check_repeat_command(self, text):
        """'[command] [N] times' pattern check karo."""
        match = re.match(r"(.+?)\s+(\d+)\s+times?$", text)
        if match:
            inner_text = match.group(1)
            count = min(int(match.group(2)), 50)
            inner_cmd = self.parse(inner_text)
            if inner_cmd and inner_cmd["type"] != "unknown":
                return {
                    "type": "repeat",
                    "action": inner_cmd,
                    "args": count,
                    "raw": text,
                }
        return None

    def get_help_text(self):
        """Sab available commands ka help text do."""
        lines = []
        lines.append("=== VOICE CONTROLLER - AVAILABLE COMMANDS ===")
        lines.append("")

        lines.append("--- Mouse Commands ---")
        for cmd in sorted(MOUSE_COMMANDS.keys()):
            lines.append(f"  '{cmd}'")

        lines.append("")
        lines.append("--- Keyboard Commands ---")
        for cmd in sorted(KEYBOARD_COMMANDS.keys()):
            lines.append(f"  '{cmd}'")

        lines.append("")
        lines.append("--- Shortcuts ---")
        for cmd, keys in sorted(SHORTCUT_COMMANDS.items()):
            lines.append(f"  '{cmd}' -> {'+'.join(keys)}")

        lines.append("")
        lines.append("--- Media Commands ---")
        for cmd in sorted(MEDIA_COMMANDS.keys()):
            lines.append(f"  '{cmd}'")

        lines.append("")
        lines.append("--- System Commands ---")
        for cmd in sorted(SYSTEM_COMMANDS.keys()):
            lines.append(f"  '{cmd}'")

        lines.append("")
        lines.append("--- Special Commands ---")
        lines.append("  'type [text]'     - Type any text")
        lines.append("  'open [app]'      - Open an application")
        lines.append("  'go to [url]'     - Open a website")
        lines.append("  '[cmd] [N] times' - Repeat any command N times")

        if WAKE_WORD:
            lines.append(f"")
            lines.append(f"  Wake word: '{WAKE_WORD}'")
            lines.append(f"  'go to sleep' - Pause until wake word")

        return "\n".join(lines)
