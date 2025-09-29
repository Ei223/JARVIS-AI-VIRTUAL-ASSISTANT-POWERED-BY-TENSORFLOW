import sys
import os
import pygame
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtCore import QTimer, QPropertyAnimation
from PyQt6.QtGui import QColor

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.jarvis_core import JarvisCore
from core.voice_engine import VoiceEngine
from gui.main_interface import MainInterface
from gui.main_window import JarvisWindow

def main():
    app = QApplication(sys.argv)
    
    # Initialize core components
    core = JarvisCore()
    voice_engine = VoiceEngine()
    
    # Create main window and interface
    window = JarvisWindow()
    interface = MainInterface(core, voice_engine)
    window.setCentralWidget(interface)
    
    # Show window
    window.showMaximized()
    
    # Start the application
    sys.exit(app.exec())
    print("Initializing face recognition system...")
    auth = FaceAuthenticator()
    
    # Verify user's face
    print("Please look at the camera for face verification...")
    is_authorized, user_name = auth.verify_face_realtime()
    
    if not is_authorized:
        print("Access denied. User not authorized. Please register first.")
        sys.exit(1)
        
    print(f"Access granted! Welcome {user_name}!")
    
    # Initialize GUI first
    window = JarvisWindow()
    window.show()
    
    try:
        # Initialize core components
        print("Initializing core components...")
        jarvis = JarvisCore()
        voice = VoiceEngine()
        from core.nlp_engine import NLPEngine
        nlp = NLPEngine()
    except Exception as e:
        print(f"Error initializing components: {str(e)}")
        # Continue showing GUI even if components fail to load
    
    # Start the application event loop
    return app.exec()
    print("\nअब आप हिंदी में कुछ भी पूछ सकते हैं (type 'exit' to quit):")
    while True:
        user_input = input("आप: ")
        if user_input.strip().lower() == "exit":
            print("JARVIS: ठीक है, अलविदा!")
            break
        result = nlp.generate_conversational_response(user_input)
        print(f"JARVIS: {result}")
        # Uncomment below to use TTS as well:
        # voice.speak(result, language='hi-IN')

    # (Optional) You can still launch the GUI and other features after/before chat loop if desired
    # ...existing code for object detection and GUI...
    # return app.exec()


if __name__ == '__main__':
    sys.exit(main())

# The following methods were previously present at the module level and are likely intended for a class (such as JarvisWindow).
# They have been commented out for review and should be integrated into the appropriate class if needed.
# def setup_window_effects(self): ...
# def play_startup_sound(self): ...
# def show_main_interface(self): ...
# def switch_to_main(self): ...
