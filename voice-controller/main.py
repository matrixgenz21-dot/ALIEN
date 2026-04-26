"""
Voice Controller Bot - Main Entry Point
=========================================
Ye bot tumhari awaz sun ke tumhare computer ka keyboard, mouse,
media playback, aur apps control karta hai.

Run karo:  python main.py
"""

import sys
import time
import logging

from config import CONTINUOUS_LISTEN, WAKE_WORD, LOG_FILE, USE_AI
from speaker import Speaker
from voice_engine import VoiceEngine
from command_parser import CommandParser
from ai_brain import AIBrain
from mouse_controller import MouseController
from keyboard_controller import KeyboardController
from media_controller import MediaController
from app_launcher import AppLauncher

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("VoiceController")


class VoiceController:
    """Main controller - sab modules ko connect karta hai."""

    def __init__(self):
        print("=" * 55)
        print("   VOICE CONTROLLER BOT")
        print("   Apni awaz se computer control karo!")
        print("=" * 55)
        print()

        self.speaker = Speaker()
        self.voice = VoiceEngine()
        self.parser = CommandParser()
        self.ai = AIBrain()
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.media = MediaController()
        self.apps = AppLauncher()

        self.running = True
        self.paused = False
        self.use_ai = USE_AI and self.ai.enabled

        if self.use_ai:
            print("\n[Mode] AI Mode ON - Kuch bhi bolo, AI samjhe ga!")
        else:
            print("\n[Mode] Fixed Commands Mode - Sirf specific commands chalein ge.")

    def handle_command(self, parsed):
        """Parsed command ko execute karo."""
        if parsed is None:
            return

        cmd_type = parsed["type"]
        action = parsed["action"]
        args = parsed.get("args")
        raw = parsed.get("raw", "")

        logger.info(f"Command: {raw} -> type={cmd_type}, action={action}")

        if cmd_type == "mouse":
            if action == "move_to" and args:
                self.mouse.move_to(args[0], args[1])
                self.speaker.say(f"Mouse moved to {args[0]}, {args[1]}")
            elif self.mouse.execute(action):
                self.speaker.say(f"Done: {raw}")
            else:
                self.speaker.say(f"Unknown mouse action: {action}")

        elif cmd_type == "keyboard":
            self.keyboard.execute(action)
            self.speaker.say(f"Pressed {action}")

        elif cmd_type == "shortcut":
            keys = action
            self.keyboard.hotkey(*keys)
            self.speaker.say(f"Done: {raw}")

        elif cmd_type == "media":
            if self.media.execute(action):
                self.speaker.say(f"Media: {raw}")
            else:
                self.speaker.say(f"Unknown media action")

        elif cmd_type == "type":
            if args:
                self.keyboard.type_text(args)
                self.speaker.say(f"Typed: {args}")

        elif cmd_type == "open":
            if args:
                if self.apps.open_app(args):
                    self.speaker.say(f"Opening {args}")
                else:
                    self.speaker.say(f"Could not open {args}")

        elif cmd_type == "website":
            if args:
                self.apps.open_website(args)
                self.speaker.say(f"Opening website")

        elif cmd_type == "repeat":
            count = args
            inner_cmd = action
            self.speaker.say(f"Repeating {count} times")
            for i in range(count):
                self.handle_command(inner_cmd)
                time.sleep(0.15)

        elif cmd_type == "system":
            self._handle_system(action)

        elif cmd_type == "custom":
            self.speaker.say(f"Custom: {raw}")
            logger.info(f"Custom command: {action}")

        elif cmd_type == "unknown":
            if self.use_ai:
                self._handle_ai(raw)
            else:
                self.speaker.say("Command samajh nahi aaya. 'help' bolo for commands.")
                logger.warning(f"Unknown command: {raw}")

    def _handle_ai(self, text):
        """AI Brain se natural language samajh ke multi-step execute karo."""
        result = self.ai.understand(text)
        if not result:
            self.speaker.say("AI se baat nahi ho payi. Internet check karo.")
            return

        steps = result.get("steps", [])
        if not steps:
            self.speaker.say("Samajh nahi aaya, dubara bolo.")
            return

        logger.info(f"AI: {text} -> {len(steps)} steps")

        total = len(steps)
        if total > 1:
            self.speaker.say(f"Ok, {total} steps mein kar raha hoon...")
            time.sleep(0.5)

        for i, step in enumerate(steps):
            if not self.running:
                break
            self._execute_step(step, i + 1, total)
            if i < total - 1:
                time.sleep(0.3)

        if total > 1:
            print(f"[AIBrain] All {total} steps done.")

    def _execute_step(self, step, num, total):
        """Ek step execute karo."""
        step_type = step.get("step", step.get("action", ""))

        if step_type == "mouse":
            cmd = step.get("command", "")
            self.mouse.execute(cmd)
            print(f"  [{num}/{total}] Mouse: {cmd}")

        elif step_type == "keyboard":
            cmd = step.get("command", "")
            self.keyboard.press_key(cmd)
            print(f"  [{num}/{total}] Key: {cmd}")

        elif step_type == "type":
            text = step.get("text", "")
            if text:
                self.keyboard.type_text(text)
                print(f"  [{num}/{total}] Typed: {text}")

        elif step_type == "shortcut":
            keys = step.get("keys", [])
            if keys:
                self.keyboard.hotkey(*keys)
                print(f"  [{num}/{total}] Shortcut: {'+'.join(keys)}")

        elif step_type == "media":
            cmd = step.get("command", "")
            self.media.execute(cmd)
            print(f"  [{num}/{total}] Media: {cmd}")

        elif step_type == "open":
            app = step.get("app", "")
            if app:
                self.apps.open_app(app)
                print(f"  [{num}/{total}] Opening: {app}")

        elif step_type == "website":
            url = step.get("url", "")
            if url:
                self.apps.open_website(url)
                print(f"  [{num}/{total}] Website: {url}")

        elif step_type == "wait":
            seconds = min(step.get("seconds", 1), 10)
            print(f"  [{num}/{total}] Waiting {seconds}s...")
            time.sleep(seconds)

        elif step_type == "speak":
            text = step.get("text", "")
            if text:
                self.speaker.say_sync(text)
                print(f"  [{num}/{total}] Said: {text}")

        elif step_type == "system":
            cmd = step.get("command", "")
            self._handle_system(cmd)
            print(f"  [{num}/{total}] System: {cmd}")

        elif step_type == "chat":
            reply = step.get("reply", "")
            if reply:
                self.speaker.say(reply)
                print(f"  [{num}/{total}] Chat: {reply}")

    def _handle_system(self, action):
        """System commands handle karo."""
        if action == "pause_listening":
            self.paused = True
            self.speaker.say_sync("Listening paused. Say 'start listening' to resume.")

        elif action == "resume_listening":
            self.voice.resume()
            self.paused = False
            self.speaker.say("Listening resumed!")

        elif action == "exit_app":
            self.speaker.say_sync("Goodbye! Voice Controller band ho raha hai.")
            self.running = False

        elif action == "show_help":
            help_text = self.parser.get_help_text()
            print(help_text)
            self.speaker.say("Help screen pe commands dikha di hain.")

        elif action == "show_status":
            pos = self.mouse.get_position()
            screen = self.mouse.get_screen_size()
            status = (
                f"Status: Mouse at {pos[0]}, {pos[1]}. "
                f"Screen size {screen[0]} by {screen[1]}. "
                f"Listening: {'Yes' if not self.paused else 'Paused'}."
            )
            print(status)
            self.speaker.say(status)

        elif action == "wake":
            self.speaker.say("Hello! Main sun raha hoon. Bolo kya karna hai?")

        elif action == "sleep_mode":
            self.speaker.say_sync(
                f"Going to sleep. Say '{WAKE_WORD}' to wake me up."
            )

    def run(self):
        """Main loop - continuously listen and execute commands."""
        if WAKE_WORD:
            self.speaker.say_sync(
                f"Voice Controller ready! Say '{WAKE_WORD}' to start."
            )
        else:
            self.speaker.say_sync(
                "Voice Controller ready! Bolo kya karna hai?"
            )

        print()
        print("Listening... (Say 'help' for commands, 'exit' to quit)")
        print("-" * 55)

        while self.running:
            try:
                text = self.voice.listen()

                if text and self.paused:
                    if text.strip().lower() == "start listening":
                        self._handle_system("resume_listening")
                    continue

                if text:
                    if self.use_ai:
                        self._handle_ai(text)
                    else:
                        parsed = self.parser.parse(text)
                        self.handle_command(parsed)

                if not CONTINUOUS_LISTEN and text:
                    time.sleep(0.5)

            except KeyboardInterrupt:
                print("\n[Ctrl+C] Shutting down...")
                self.running = False
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                print(f"[Error]: {e}")
                time.sleep(1)

        self._cleanup()

    def _cleanup(self):
        """Sab kuch band karo nicely."""
        print("\nCleaning up...")
        self.speaker.cleanup()
        print("Voice Controller stopped. Khuda Hafiz!")


def main():
    """Entry point."""
    print()
    print("Checking dependencies...")

    missing = []
    try:
        import speech_recognition
    except ImportError:
        missing.append("SpeechRecognition")

    try:
        import pyautogui
    except ImportError:
        missing.append("pyautogui")

    try:
        import pyttsx3
    except ImportError:
        missing.append("pyttsx3")

    if missing:
        print()
        print("=" * 55)
        print("  MISSING LIBRARIES!")
        print("  Ye packages install karo pehle:")
        print()
        print(f"  pip install {' '.join(missing)}")
        print()
        print("  Ya run karo: setup.bat")
        print("=" * 55)
        print()

        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != "y":
            sys.exit(1)

    controller = VoiceController()
    controller.run()


if __name__ == "__main__":
    main()
