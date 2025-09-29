import speech_recognition as sr
import pyttsx3
import threading
import queue
from src.utils.config import load_config
import face_recognition
import cv2
import numpy as np
import openai
import json
import os
from datetime import datetime

class Jarvis:
    def __init__(self, config):
        self.config = config
        self.initialize_components()
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.running = False
        self.setup_openai()
        
    def initialize_components(self):
        """Initialize all JARVIS components"""
        self.setup_voice()
        self.setup_face_recognition()
        self.setup_event_handlers()
        
    def setup_voice(self):
        """Initialize voice recognition and synthesis"""
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.configure_voice()
        
    def configure_voice(self):
        """Configure voice properties"""
        voices = self.engine.getProperty('voices')
        # Select a male voice for JARVIS
        for voice in voices:
            if "male" in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
                
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
        
    def setup_face_recognition(self):
        """Initialize facial recognition system"""
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Load known faces if available
        self.known_faces = []
        self.known_names = []
        self.load_known_faces()
        
    def setup_openai(self):
        """Configure OpenAI for natural language processing"""
        if 'OPENAI_API_KEY' in self.config:
            openai.api_key = self.config['OPENAI_API_KEY']
            
    def setup_event_handlers(self):
        """Set up event handlers for various JARVIS functions"""
        self.event_handlers = {
            'face_detected': self.handle_face_detection,
            'voice_command': self.handle_voice_command,
            'system_alert': self.handle_system_alert
        }
        
    def start(self):
        """Start JARVIS systems"""
        self.running = True
        threading.Thread(target=self.voice_recognition_loop, daemon=True).start()
        threading.Thread(target=self.command_processing_loop, daemon=True).start()
        
    def stop(self):
        """Stop JARVIS systems"""
        self.running = False
        
    def voice_recognition_loop(self):
        """Main loop for voice recognition"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=1)
                    text = self.recognizer.recognize_google(audio)
                    self.command_queue.put(('voice_command', text))
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except Exception as e:
                    print(f"Error in voice recognition: {str(e)}")
                    
    def command_processing_loop(self):
        """Main loop for processing commands"""
        while self.running:
            try:
                event_type, data = self.command_queue.get(timeout=1)
                if event_type in self.event_handlers:
                    self.event_handlers[event_type](data)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing command: {str(e)}")
                
    def speak(self, text):
        """Convert text to speech"""
        def _speak():
            self.engine.say(text)
            self.engine.runAndWait()
            
        threading.Thread(target=_speak, daemon=True).start()
        
    def handle_voice_command(self, command):
        """Process voice commands using NLP"""
        try:
            # Use OpenAI for natural language understanding
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are JARVIS, an advanced AI assistant."},
                    {"role": "user", "content": command}
                ]
            )
            
            # Extract and process the response
            ai_response = response.choices[0].message.content
            self.speak(ai_response)
            
            # Execute any associated actions
            self.execute_command(command, ai_response)
            
        except Exception as e:
            print(f"Error processing command: {str(e)}")
            self.speak("I apologize, but I encountered an error processing that command.")
            
    def execute_command(self, command, ai_response):
        """Execute specific actions based on commands"""
        command = command.lower()
        
        if "face recognition" in command:
            self.start_face_recognition()
        elif "system status" in command:
            self.get_system_status()
        elif "search" in command:
            query = command.replace("search", "").strip()
            self.web_search(query)
            
    def handle_face_detection(self, face_data):
        """Handle detected faces"""
        face_image = face_data['image']
        face_locations = face_recognition.face_locations(face_image)
        face_encodings = face_recognition.face_encodings(face_image, face_locations)
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_faces, face_encoding)
            if True in matches:
                name = self.known_names[matches.index(True)]
                self.speak(f"Welcome back, {name}")
            else:
                self.speak("Unknown person detected")
                
    def handle_system_alert(self, alert_data):
        """Handle system alerts and notifications"""
        alert_type = alert_data['type']
        message = alert_data['message']
        
        if alert_type == 'warning':
            self.speak(f"Warning: {message}")
        elif alert_type == 'critical':
            self.speak(f"Critical alert: {message}")
            
    def load_known_faces(self):
        """Load known faces from the faces directory"""
        faces_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'faces')
        if os.path.exists(faces_dir):
            for filename in os.listdir(faces_dir):
                if filename.endswith((".jpg", ".png")):
                    image_path = os.path.join(faces_dir, filename)
                    name = os.path.splitext(filename)[0]
                    
                    face_image = face_recognition.load_image_file(image_path)
                    face_encoding = face_recognition.face_encodings(face_image)[0]
                    
                    self.known_faces.append(face_encoding)
                    self.known_names.append(name)
                    
    def get_system_status(self):
        """Get current system status"""
        import psutil
        
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status_message = f"""
        Current system status:
        CPU Usage: {cpu_percent}%
        Memory Usage: {memory.percent}%
        Disk Usage: {disk.percent}%
        """
        
        self.speak(status_message)
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent
        }
        
    def web_search(self, query):
        """Perform a web search"""
        import wikipedia
        
        try:
            # Try Wikipedia first
            result = wikipedia.summary(query, sentences=2)
            self.speak(f"Here's what I found: {result}")
        except:
            self.speak("I'm sorry, I couldn't find any relevant information.")