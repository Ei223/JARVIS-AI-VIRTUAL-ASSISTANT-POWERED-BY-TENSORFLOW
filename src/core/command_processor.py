import re
import json
import wikipedia
import webbrowser
import psutil
import datetime
import requests
from bs4 import BeautifulSoup

class CommandProcessor:
    def __init__(self):
        self.commands = {
            'search': self.web_search,
            'time': self.get_time,
            'date': self.get_date,
            'system': self.system_status,
            'weather': self.get_weather,
            'open': self.open_application,
            'close': self.close_application,
            'wiki': self.wikipedia_search
        }
        
    def process_command(self, command_text):
        """Process natural language commands without using OpenAI"""
        command_text = command_text.lower().strip()
        
        # Time queries
        if any(phrase in command_text for phrase in ['what time', 'current time']):
            return self.get_time()
            
        # Date queries
        if any(phrase in command_text for phrase in ['what date', 'what day', 'current date']):
            return self.get_date()
            
        # System status
        if any(phrase in command_text for phrase in ['system status', 'cpu usage', 'memory usage']):
            return self.system_status()
            
        # Weather queries
        if 'weather' in command_text:
            location = self.extract_location(command_text)
            return self.get_weather(location)
            
        # Web searches
        if any(phrase in command_text for phrase in ['search for', 'look up', 'search']):
            query = command_text.split('search for')[-1].strip()
            if not query:
                query = command_text.split('search')[-1].strip()
            return self.web_search(query)
            
        # Wikipedia searches
        if any(phrase in command_text for phrase in ['tell me about', 'what is', 'who is']):
            query = command_text.split('about')[-1].strip()
            return self.wikipedia_search(query)
            
        # Application control
        if 'open' in command_text:
            app = command_text.split('open')[-1].strip()
            return self.open_application(app)
            
        if 'close' in command_text:
            app = command_text.split('close')[-1].strip()
            return self.close_application(app)
            
        return "I'm sorry, I didn't understand that command. Could you please rephrase it?"
        
    def get_time(self):
        """Get current time"""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}"
        
    def get_date(self):
        """Get current date"""
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        return f"Today is {current_date}"
        
    def system_status(self):
        """Get system resource usage"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        return f"System Status:\nCPU Usage: {cpu}%\nMemory Usage: {memory}%\nDisk Usage: {disk}%"
        
    def get_weather(self, location="local"):
        """Get weather information using free API"""
        try:
            # Using wttr.in - a free weather service
            url = f"https://wttr.in/{location}?format=%C+%t"
            response = requests.get(url)
            if response.status_code == 200:
                return f"Weather in {location}: {response.text}"
            return "Sorry, I couldn't fetch the weather information"
        except:
            return "Sorry, I couldn't fetch the weather information"
            
    def wikipedia_search(self, query):
        """Search Wikipedia"""
        try:
            result = wikipedia.summary(query, sentences=2)
            return result
        except:
            return f"Sorry, I couldn't find information about {query}"
            
    def web_search(self, query):
        """Perform a web search"""
        search_url = f"https://www.google.com/search?q={query}"
        webbrowser.open(search_url)
        return f"I've opened a web search for: {query}"
        
    def open_application(self, app_name):
        """Simple application control"""
        try:
            import subprocess
            common_apps = {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'chrome': 'chrome.exe',
                'firefox': 'firefox.exe',
                'explorer': 'explorer.exe'
            }
            
            app = common_apps.get(app_name.lower(), app_name.lower())
            subprocess.Popen(app)
            return f"Opening {app_name}"
        except:
            return f"Sorry, I couldn't open {app_name}"
            
    def close_application(self, app_name):
        """Close a running application"""
        try:
            import subprocess
            subprocess.run(['taskkill', '/IM', f'{app_name}.exe', '/F'])
            return f"Closed {app_name}"
        except:
            return f"Sorry, I couldn't close {app_name}"
            
    def extract_location(self, text):
        """Extract location from weather query"""
        # Remove common weather-related words
        words = text.replace('weather', '').replace('in', '').replace('at', '').strip()
        if words:
            return words
        return "local"  # Default to local weather