"""
Voice Controller - Text-to-Speech Feedback
Bot tumhe baat kar ke batata hai kya ho raha hai.
"""

import threading

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

from config import SPEECH_RATE, SPEECH_VOLUME


class Speaker:
    """Text-to-speech engine for voice feedback."""

    def __init__(self):
        self._engine = None
        self._lock = threading.Lock()
        self.enabled = True

        if TTS_AVAILABLE:
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", SPEECH_RATE)
                self._engine.setProperty("volume", SPEECH_VOLUME)

                voices = self._engine.getProperty("voices")
                if voices:
                    self._engine.setProperty("voice", voices[0].id)

                print("[Speaker] Text-to-speech ready.")
            except Exception as e:
                print(f"[Speaker] TTS init failed: {e}")
                self._engine = None
        else:
            print("[Speaker] pyttsx3 not installed. Voice feedback disabled.")
            print("          Install with: pip install pyttsx3")

    def say(self, text):
        """Bolo kuch - thread-safe."""
        if not self.enabled or self._engine is None:
            print(f"[Bot]: {text}")
            return

        def _speak():
            with self._lock:
                try:
                    self._engine.say(text)
                    self._engine.runAndWait()
                except Exception as e:
                    print(f"[Speaker] Error: {e}")

        print(f"[Bot]: {text}")
        thread = threading.Thread(target=_speak, daemon=True)
        thread.start()

    def say_sync(self, text):
        """Synchronous speech - wait until done."""
        if not self.enabled or self._engine is None:
            print(f"[Bot]: {text}")
            return

        with self._lock:
            try:
                print(f"[Bot]: {text}")
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                print(f"[Speaker] Error: {e}")

    def toggle(self):
        """Voice feedback on/off toggle."""
        self.enabled = not self.enabled
        state = "ON" if self.enabled else "OFF"
        print(f"[Speaker] Voice feedback: {state}")

    def cleanup(self):
        """Engine cleanup."""
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
