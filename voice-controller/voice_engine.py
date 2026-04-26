"""
Voice Controller - Speech Recognition Engine
Tumhari awaz sun ke text mein convert karta hai.
"""

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

from config import LANGUAGE, LISTEN_TIMEOUT, PHRASE_TIMEOUT, ENERGY_THRESHOLD


class VoiceEngine:
    """Microphone se awaz sun ke text mein badle."""

    def __init__(self):
        self._recognizer = None
        self._microphone = None
        self.is_listening = True

        if not SR_AVAILABLE:
            print("[VoiceEngine] speech_recognition not installed!")
            print("              Install with: pip install SpeechRecognition")
            return

        try:
            self._recognizer = sr.Recognizer()
            self._recognizer.energy_threshold = ENERGY_THRESHOLD
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.8

            self._microphone = sr.Microphone()

            with self._microphone as source:
                print("[VoiceEngine] Adjusting for ambient noise... (2 sec)")
                self._recognizer.adjust_for_ambient_noise(source, duration=2)

            print("[VoiceEngine] Microphone ready. Listening...")
        except Exception as e:
            print(f"[VoiceEngine] Microphone init failed: {e}")
            print("              Make sure a microphone is connected.")
            self._recognizer = None

    def listen(self):
        """
        Ek baar suno aur text return karo.
        Returns: recognized text (lowercase) or None if nothing heard.
        """
        if not self._recognizer or not self._microphone:
            return None

        if not self.is_listening:
            return None

        try:
            with self._microphone as source:
                audio = self._recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIMEOUT,
                )

            text = self._recognizer.recognize_google(
                audio, language=LANGUAGE
            )
            text = text.lower().strip()
            print(f"[You said]: {text}")
            return text

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[VoiceEngine] Google API error: {e}")
            print("              Check your internet connection.")
            return None
        except Exception as e:
            print(f"[VoiceEngine] Error: {e}")
            return None

    def listen_in_background(self, callback):
        """
        Background mein continuously suno.
        callback(text) har recognized phrase ke liye call hoga.
        """
        if not self._recognizer or not self._microphone:
            print("[VoiceEngine] Cannot start background listening.")
            return None

        def _callback(recognizer, audio):
            if not self.is_listening:
                return
            try:
                text = recognizer.recognize_google(audio, language=LANGUAGE)
                text = text.lower().strip()
                print(f"[You said]: {text}")
                callback(text)
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"[VoiceEngine] API error: {e}")
            except Exception as e:
                print(f"[VoiceEngine] Error: {e}")

        stop_fn = self._recognizer.listen_in_background(
            self._microphone, _callback, phrase_time_limit=PHRASE_TIMEOUT
        )
        print("[VoiceEngine] Background listening started.")
        return stop_fn

    def pause(self):
        """Sunna band karo."""
        self.is_listening = False
        print("[VoiceEngine] Listening paused.")

    def resume(self):
        """Dubara sunna shuru karo."""
        self.is_listening = True
        print("[VoiceEngine] Listening resumed.")

    def calibrate(self):
        """Microphone ko dubara calibrate karo."""
        if self._recognizer and self._microphone:
            try:
                with self._microphone as source:
                    print("[VoiceEngine] Recalibrating... (2 sec)")
                    self._recognizer.adjust_for_ambient_noise(source, duration=2)
                print("[VoiceEngine] Calibration done.")
            except Exception as e:
                print(f"[VoiceEngine] Calibration error: {e}")
