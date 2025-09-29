import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
import json
import asyncio
import re
import logging
from utils.config import load_config
from .nlp_engine import NLPEngine

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.voice_queue = queue.Queue()
        self.is_listening = False
        self.config = load_config()
        self.language = 'hi-IN'  # Set Hindi as default language
        self.nlp_engine = NLPEngine()  # Initialize NLP engine
        self.setup_voice()
        
    def setup_voice(self):
        """Configure text-to-speech with Hindi support"""
        voices = self.engine.getProperty('voices')
        
        # Try to find an Indian voice first
        indian_voice = None
        male_voice = None
        
        for voice in voices:
            if "hindi" in voice.name.lower() or "indian" in voice.name.lower():
                indian_voice = voice.id
                break
            elif "male" in voice.name.lower():
                male_voice = voice.id
        
        # Set the appropriate voice
        if indian_voice:
            self.engine.setProperty('voice', indian_voice)
            print("Using Indian voice for speech")
        elif male_voice:
            self.engine.setProperty('voice', male_voice)
            print("Using male voice for speech (Indian voice not found)")
        else:
            print("Warning: No suitable voice found, using default voice")
        
        # Configure voice properties
        self.engine.setProperty('rate', 160)  # Slightly slower for Hindi
        self.engine.setProperty('volume', 0.9)
        
        # Store available voices for language switching
        self.available_voices = {
            'hi-IN': indian_voice,
            'en-US': male_voice
        }
    
    def get_command(self):
        """Get the next command from the queue if available"""
        try:
            return self.voice_queue.get_nowait()
        except queue.Empty:
            return None
            
    def start_listening(self):
        self.is_listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop_listening(self):
        self.is_listening = False

    def _listen_loop(self):
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Ready! Say 'Jarvis' followed by your command.")
            
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    try:
                        # Use Hindi language for recognition
                        command = self.recognizer.recognize_google(audio, language=self.language)
                        print(f"Recognized: {command}")
                        
                        # Check if command starts with "jarvis" (case insensitive)
                        if "jarvis" in command.lower() or "जार्विस" in command.lower():
                            # Remove "jarvis" from command
                            actual_command = command.lower().replace("jarvis", "").replace("जार्विस", "").strip()
                            
                            # Process command through NLP engine
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            processed_command = loop.run_until_complete(self.nlp_engine.process_command(actual_command))
                            
                            # Generate response
                            response = loop.run_until_complete(self.nlp_engine.generate_response(processed_command))
                            
                            # Speak response
                            self.speak(response)
                            
                            # Put processed command in queue for action handling
                            self.voice_queue.put(processed_command)
                            
                    except sr.UnknownValueError:
                        print("Could not understand audio")
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
                        
                except sr.WaitTimeoutError:
                    continue


    def speak(self, text: str, language: str = 'hi-IN'):
        """
        Speak the given text in the specified language with improved Hindi support
        
        Args:
            text: Text to speak
            language: Language code ('hi-IN' for Hindi, 'en-US' for English)
        """
        try:
            # Save current properties
            current_voice = self.engine.getProperty('voice')
            current_rate = self.engine.getProperty('rate')
            
            # Detect if text contains Hindi characters
            contains_hindi = bool(re.search(r'[\u0900-\u097F]', text))
            
            # Adjust voice and rate based on content
            if contains_hindi or language == 'hi-IN':
                if self.available_voices.get('hi-IN'):
                    self.engine.setProperty('voice', self.available_voices['hi-IN'])
                    self.engine.setProperty('rate', 160)  # Slower for Hindi
            else:
                if self.available_voices.get('en-US'):
                    self.engine.setProperty('voice', self.available_voices['en-US'])
                    self.engine.setProperty('rate', 180)  # Normal speed for English
            
            # Break text into smaller chunks for better pronunciation
            sentences = re.split('[।.|!|?]', text)
            for sentence in sentences:
                if sentence.strip():
                    self.engine.say(sentence.strip())
                    self.engine.runAndWait()
                    time.sleep(0.1)  # Small pause between sentences
            
            # Restore original properties
            self.engine.setProperty('voice', current_voice)
            self.engine.setProperty('rate', current_rate)
            
        except Exception as e:
            logging.error(f"Error in speech: {str(e)}")
            # Fallback to print if speech fails
            print(f"JARVIS would say: {text}")

    def get_analysis(self):
        # Return current voice analysis data
        return {
            "Status": "Active" if self.is_listening else "Inactive",
            "Input Queue": self.voice_queue.qsize(),
            "Last Process Time": time.strftime("%H:%M:%S")
        }