import sys
import os
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
import speech_recognition as sr
import pyttsx3
import json
import cv2

def test_components():
    print("Testing JARVIS components...")
    
    # Test GUI
    print("\n1. Testing GUI components:")
    try:
        app = QApplication(sys.argv)
        window = QMainWindow()
        print("✓ PyQt6 GUI framework is working")
    except Exception as e:
        print(f"✗ GUI Error: {str(e)}")

    # Test Voice Recognition
    print("\n2. Testing Voice Recognition:")
    try:
        recognizer = sr.Recognizer()
        print("✓ Speech Recognition is working")
    except Exception as e:
        print(f"✗ Voice Recognition Error: {str(e)}")

    # Test Voice Synthesis
    print("\n3. Testing Voice Synthesis:")
    try:
        engine = pyttsx3.init()
        print("✓ Voice Synthesis is working")
    except Exception as e:
        print(f"✗ Voice Synthesis Error: {str(e)}")

    # Test Configuration
    print("\n4. Testing Configuration:")
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        print("✓ Configuration file is accessible")
    except Exception as e:
        print(f"✗ Configuration Error: {str(e)}")

    # Test Camera
    print("\n5. Testing Camera:")
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            print("✓ Camera is accessible")
        else:
            print("✗ Camera test failed")
    except Exception as e:
        print(f"✗ Camera Error: {str(e)}")

if __name__ == "__main__":
    test_components()