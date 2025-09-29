from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
import os

class StartupScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle('JARVIS')
        self.setStyleSheet("background-color: black;")
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create JARVIS logo
        self.logo_label = QLabel(self)
        logo_path = os.path.join("assets", "jarvis_logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio))
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create loading text
        self.loading_label = QLabel("INITIALIZING SYSTEMS...", self)
        self.loading_label.setStyleSheet("color: #00FFFF; font-size: 24px;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create system status labels
        self.status_labels = []
        systems = [
            "CORE SYSTEMS",
            "NEURAL INTERFACE",
            "VOICE RECOGNITION",
            "FACE RECOGNITION",
            "ENVIRONMENT SENSORS"
        ]
        
        for system in systems:
            label = QLabel(f"[    ] {system}", self)
            label.setStyleSheet("color: #00FFFF; font-size: 16px;")
            self.status_labels.append(label)
        
        # Position elements
        self.resize(800, 600)
        self.logo_label.setGeometry(200, 50, 400, 400)
        self.loading_label.setGeometry(200, 460, 400, 30)
        
        for i, label in enumerate(self.status_labels):
            label.setGeometry(250, 500 + i*25, 300, 20)
        
        # Start initialization sequence
        self.current_system = 0
        self.init_timer = QTimer()
        self.init_timer.timeout.connect(self.initialize_next_system)
        self.init_timer.start(1000)
        
    def initialize_next_system(self):
        if self.current_system < len(self.status_labels):
            text = self.status_labels[self.current_system].text()
            self.status_labels[self.current_system].setText(text.replace("[    ]", "[DONE]"))
            self.current_system += 1
        else:
            self.init_timer.stop()
            # Emit signal that initialization is complete
            self.initialization_complete()
            
    def initialization_complete(self):
        # This method will be called when all systems are initialized
        print("All systems initialized")
        # You can emit a signal here to switch to the main interface