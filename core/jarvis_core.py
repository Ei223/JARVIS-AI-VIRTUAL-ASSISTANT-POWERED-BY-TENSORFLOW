import psutil
import GPUtil
import platform
import datetime
import requests
import wikipedia
import webbrowser
import os
import face_recognition
import cv2
from utils.config import load_config

class JarvisCore:
    def __init__(self):
        self.config = load_config()
        self.initialize_systems()
        
    def initialize_systems(self):
        """Initialize all subsystems"""
        self.last_system_check = datetime.datetime.now()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def get_system_info(self):
        """Get current system status"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        try:
            gpus = GPUtil.getGPUs()
            gpu_info = f"{gpus[0].name}: {gpus[0].load*100}%" if gpus else "No GPU found"
        except:
            gpu_info = "GPU info unavailable"
            
        return {
            "CPU Usage": f"{cpu_percent}%",
            "Memory": f"{memory.percent}%",
            "GPU": gpu_info,
            "Temperature": self.get_temperature()
        }
        
    def get_temperature(self):
        """Get system temperature if available"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # Get the first temperature reading
                first_temp = next(iter(temps.values()))[0]
                return f"{first_temp.current}°C"
        except:
            pass
        return "N/A"
        
    def get_processing_status(self):
        """Get current processing status"""
        return {
            "Active Tasks": len(psutil.Process().threads()),
            "Last Check": self.last_system_check.strftime("%H:%M:%S"),
            "System Load": f"{psutil.getloadavg()[0]:.2f}"
        }
        
    def process_command(self, command):
        """Process voice commands"""
        command = command.lower()
        
        # System commands
        if "system status" in command:
            return self.get_system_info()
            
        # Web searches
        elif "search" in command:
            query = command.replace("search", "").strip()
            return self.web_search(query)
            
        # Wikipedia lookups
        elif "tell me about" in command:
            query = command.replace("tell me about", "").strip()
            return self.wikipedia_search(query)
            
        # Face recognition
        elif "recognize face" in command:
            return self.recognize_face()
            
        return "Command not recognized"
        
    def web_search(self, query):
        """Perform a web search"""
        try:
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Searching for {query}"
        except:
            return "Failed to perform web search"
            
    def wikipedia_search(self, query):
        """Search Wikipedia"""
        try:
            result = wikipedia.summary(query, sentences=2)
            return result
        except:
            return "Could not find information on Wikipedia"
            
    def recognize_face(self):
        """Perform facial recognition"""
        try:
            # Initialize camera
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            
            if not ret:
                return "Camera access failed"
                
            # Find faces
            face_locations = face_recognition.face_locations(frame)
            if face_locations:
                return f"Found {len(face_locations)} face(s)"
            else:
                return "No faces detected"
                
        except Exception as e:
            return f"Face recognition error: {str(e)}"
        finally:
            if 'cap' in locals():
                cap.release()