#!/usr/bin/env python3
"""
Voice interface for Sarek AI Assistant
"""

import re
from typing import Optional
from rich.console import Console

try:
    import speech_recognition as sr
    import pyttsx3

    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

console = Console()


class VoiceInterface:
    """Voice recognition and text-to-speech interface"""

    def __init__(self):
        self.available = VOICE_AVAILABLE
        self.recognizer = None
        self.tts = None

        if self.available:
            try:
                self.recognizer = sr.Recognizer()
                self.tts = pyttsx3.init()
                self._configure_tts()
            except Exception:
                self.available = False

    def _configure_tts(self) -> None:
        """Configure text-to-speech settings"""
        if not self.available or not self.tts:
            return

        try:
            voices = self.tts.getProperty('voices')
            if voices:
                self.tts.setProperty('voice', voices[0].id)

            self.tts.setProperty('rate', 180)
            self.tts.setProperty('volume', 0.8)
        except Exception:
            pass

    def listen(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Listen for voice commands"""
        if not self.available:
            console.print("❌ Voice recognition not available")
            console.print("Install with: pip install SpeechRecognition pyttsx3")
            return None

        try:
            with sr.Microphone() as source:
                console.print("🎤 [bold cyan]Listening... (speak now)[/bold cyan]")

                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

            console.print("🤖 [dim]Processing speech...[/dim]")

            text = self.recognizer.recognize_google(audio)
            console.print(f"📝 [bold green]You said:[/bold green] {text}")
            return text

        except sr.WaitTimeoutError:
            console.print("⏰ Listening timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            console.print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            console.print(f"❌ Speech recognition service error: {e}")
            return None
        except Exception as e:
            console.print(f"❌ Voice recognition error: {e}")
            return None

    def speak(self, text: str) -> None:
        """Speak the response with text-to-speech"""
        if not self.available or not self.tts:
            return

        try:
            clean_text = self._clean_text_for_speech(text)

            if not clean_text.strip():
                return

            console.print("🔊 [dim]Speaking...[/dim]")

            self.tts.say(clean_text)
            self.tts.runAndWait()

        except Exception as e:
            console.print(f"❌ Text-to-speech error: {e}")

    def _clean_text_for_speech(self, text: str) -> str:
        """Clean text to make it more suitable for speech synthesis"""

        clean_text = re.sub(r'\[.*?\]', '', text)

        clean_text = re.sub(r'[🖖🤖📝💬🔍⚠️❌✅🔴🟡🟢📊🏆🎤🔊]', '', clean_text)

        clean_text = re.sub(r'```.*?```', '[code block]', clean_text, flags=re.DOTALL)

        clean_text = clean_text.replace('**', '').replace('*', '')
        clean_text = clean_text.replace('`', '')

        replacements = {
            'CLI': 'command line interface',
            'API': 'A P I',
            'URL': 'U R L',
            'HTTP': 'H T T P',
            'JSON': 'J S O N',
            'XML': 'X M L',
            'SQL': 'S Q L',
            'CSS': 'C S S',
            'HTML': 'H T M L',
            'JS': 'JavaScript',
            'TS': 'TypeScript'
        }

        for abbrev, replacement in replacements.items():
            clean_text = clean_text.replace(abbrev, replacement)

        clean_text = ' '.join(clean_text.split())

        return clean_text

    def set_voice_properties(self, rate: int = None, volume: float = None) -> None:
        """Set voice properties for TTS"""
        if not self.available or not self.tts:
            return

        try:
            if rate is not None:
                self.tts.setProperty('rate', max(50, min(300, rate)))

            if volume is not None:
                self.tts.setProperty('volume', max(0.0, min(1.0, volume)))

        except Exception:
            pass

    def list_available_voices(self) -> list:
        """Get list of available TTS voices"""
        if not self.available or not self.tts:
            return []

        try:
            voices = self.tts.getProperty('voices')
            if voices:
                return [
                    {
                        'id': voice.id,
                        'name': getattr(voice, 'name', 'Unknown'),
                        'languages': getattr(voice, 'languages', [])
                    }
                    for voice in voices
                ]
        except Exception:
            pass

        return []

    def set_voice(self, voice_id: str) -> bool:
        """Set the TTS voice by ID"""
        if not self.available or not self.tts:
            return False

        try:
            voices = self.tts.getProperty('voices')
            if voices:
                for voice in voices:
                    if voice.id == voice_id:
                        self.tts.setProperty('voice', voice_id)
                        return True
        except Exception:
            pass

        return False

    def test_audio_devices(self) -> dict:
        """Test and list available audio input devices"""
        if not self.available:
            return {'error': 'Voice interface not available'}

        try:
            device_info = {}

            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                device_info[index] = name

            return {
                'devices': device_info,
                'default_device': 'System default microphone'
            }

        except Exception as e:
            return {'error': f'Could not list audio devices: {e}'}

    def is_microphone_available(self) -> bool:
        """Check if microphone is available and working"""
        if not self.available:
            return False

        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                return True
        except Exception:
            return False