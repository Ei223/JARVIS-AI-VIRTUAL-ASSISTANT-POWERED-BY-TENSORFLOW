import cv2
import numpy as np
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import face_recognition
import random
from gui.holographic_display import HologramEffect

class FaceAuthInterface(QWidget):
    auth_successful = pyqtSignal()  # Signal emitted when authentication is successful
    auth_failed = pyqtSignal()      # Signal emitted when authentication fails

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_face_recognition()
        self.scan_progress = 0
        self.authenticated = False
        self.scan_complete = False

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(0, 20, 40, 180);
                border: 2px solid #00fff2;
                border-radius: 10px;
            }
        """)

        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Video feed display with holographic effect
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.video_label)

        # Status display
        self.status_label = QLabel("INITIATING BIOMETRIC SCAN...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00fff2;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
                background: none;
                border: none;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Initialize holographic effect
        self.holo_effect = HologramEffect()
        
        # Setup timers
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_frame)
        self.video_timer.start(33)  # ~30 FPS

        self.scan_timer = QTimer()
        self.scan_timer.timeout.connect(self.update_scan_progress)
        self.scan_timer.start(50)

    def setup_face_recognition(self):
        self.cap = cv2.VideoCapture(0)
        # Load known face encodings
        self.known_face_encodings = []
        try:
            known_image = face_recognition.load_image_file("known_faces/user.jpg")
            self.known_face_encodings = face_recognition.face_encodings(known_image)[0]
        except Exception as e:
            print(f"Error loading known face: {e}")

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert frame to RGB for face_recognition
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find faces in frame
            face_locations = face_recognition.face_locations(rgb_frame)
            
            # Add futuristic overlay
            self.add_futuristic_overlay(rgb_frame, face_locations)
            
            # Convert to QImage and display
            h, w, ch = rgb_frame.shape
            qt_image = QImage(rgb_frame.data, w, h, w * ch, QImage.Format.Format_RGB888)
            
            # Apply holographic effect
            holo_image = self.holo_effect.apply(qt_image)
            self.video_label.setPixmap(QPixmap.fromImage(holo_image).scaled(
                self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio))

            # Process face recognition if face detected
            if face_locations and not self.scan_complete:
                self.process_face_recognition(rgb_frame, face_locations)

    def add_futuristic_overlay(self, frame, face_locations):
        overlay = frame.copy()
        for (top, right, bottom, left) in face_locations:
            # Draw scanning grid
            grid_color = (0, 255, 242)
            grid_spacing = 20
            for x in range(left, right, grid_spacing):
                cv2.line(overlay, (x, top), (x, bottom), grid_color, 1)
            for y in range(top, bottom, grid_spacing):
                cv2.line(overlay, (left, y), (right, y), grid_color, 1)

            # Draw main rectangle
            cv2.rectangle(overlay, (left-2, top-2), (right+2, bottom+2), (0, 255, 242), 2)
            
            # Add scan line animation
            scan_y = int(top + (bottom - top) * (self.scan_progress / 100))
            cv2.line(overlay, (left-10, scan_y), (right+10, scan_y), (0, 255, 242), 2)
            
            # Add random "data points"
            for _ in range(5):
                x = random.randint(left, right)
                y = random.randint(top, bottom)
                cv2.circle(overlay, (x, y), 2, (0, 255, 242), -1)
                
            # Add biometric data text
            cv2.putText(overlay, f"SCAN: {self.scan_progress}%", 
                      (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 242), 1)

        # Blend the overlay with the original frame
        alpha = 0.7
        frame[:] = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    def process_face_recognition(self, frame, face_locations):
        # Get face encodings for detected faces
        face_encodings = face_recognition.face_encodings(frame, face_locations)
        
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces([self.known_face_encodings], face_encoding)
            
            if True in matches:
                self.authenticated = True
                self.status_label.setText("IDENTITY CONFIRMED - ACCESS GRANTED")
                self.status_label.setStyleSheet("color: #00ff00; font-size: 18px; font-weight: bold;")
                self.scan_complete = True
                self.auth_successful.emit()
            else:
                self.status_label.setText("ACCESS DENIED - IDENTITY MISMATCH")
                self.status_label.setStyleSheet("color: #ff0000; font-size: 18px; font-weight: bold;")
                self.auth_failed.emit()

    def update_scan_progress(self):
        if not self.scan_complete:
            self.scan_progress = (self.scan_progress + 2) % 100
            if self.scan_progress == 0:
                self.status_label.setText("ANALYZING BIOMETRIC PATTERNS...")

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)