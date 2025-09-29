from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGraphicsDropShadowEffect, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient
try:
    from .holographic_display import HologramEffect
    from .face_auth_interface import FaceAuthInterface
except ImportError as e:
    print(f"Warning: Could not import GUI components: {e}")
    HologramEffect = None
    FaceAuthInterface = None
import time
import random

class MainInterface(QWidget):
    authentication_complete = pyqtSignal(bool)  # Signal for auth result

    def __init__(self, core, voice_engine):
        super().__init__()
        self.core = core
        self.voice_engine = voice_engine
        self.authenticated = False
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Create stacked widget for different screens
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # Create and add the face authentication interface
        try:
            self.face_auth = FaceAuthInterface()
            self.face_auth.auth_successful.connect(self.on_auth_success)
            self.face_auth.auth_failed.connect(self.on_auth_failed)
        except Exception as e:
            print(f"Warning: Face authentication initialization error: {str(e)}")
            self.face_auth = QWidget()  # Placeholder if face auth fails
        
        # Create main content widget
        self.main_content = QWidget()
        
        # Add both to stack
        self.stack.addWidget(self.face_auth)
        self.stack.addWidget(self.main_content)
        
        # Set up main layout
        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)
        
        # Add background glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 255, 255, 160))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)
        
        self.setup_ui()
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_interface)
        self.timer.start(16)  # 60 FPS
        
        # Setup floating animation
        self.setup_floating_animation()

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: black;
            }
            QLabel {
                color: #00FFFF;
                font-family: 'Consolas';
                font-size: 24px;
                background-color: transparent;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Status display with holographic effect
        status_container = QWidget()
        status_container.setStyleSheet("background: rgba(0, 30, 60, 30); border-radius: 10px;")
        status_layout = QVBoxLayout(status_container)
        
        self.status_label = QLabel("J.A.R.V.I.S ONLINE")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        # Add glow effect to status
        status_glow = QGraphicsDropShadowEffect()
        status_glow.setBlurRadius(10)
        status_glow.setColor(QColor(0, 255, 255, 160))
        status_glow.setOffset(0, 0)
        self.status_label.setGraphicsEffect(status_glow)
        
        layout.addWidget(status_container)
        
        # Create holographic display areas
        self.create_holographic_displays()
        
    def setup_floating_animation(self):
        # Create floating animation for displays
        for display in self.displays:
            anim = QPropertyAnimation(display, b"pos")
            anim.setDuration(random.randint(2000, 3000))
            anim.setEasingCurve(QEasingCurve.Type.InOutSine)
            
            start_pos = display.pos()
            anim.setStartValue(start_pos)
            anim.setEndValue(start_pos.translated(0, 10))
            
            # Make it loop back and forth
            anim.finished.connect(lambda: self.reverse_animation(anim))
            anim.start()

    def create_holographic_displays(self):
        # Create areas for different holographic displays
        self.displays = []
        
        # System monitoring display
        self.system_display = HolographicDisplay("SYSTEM STATUS")
        self.displays.append(self.system_display)
        
        # Voice analysis display
        self.voice_display = HolographicDisplay("VOICE ANALYSIS")
        self.displays.append(self.voice_display)
        
        # Data processing display
        self.data_display = HolographicDisplay("DATA PROCESSING")
        self.displays.append(self.data_display)
        
        # Neural network display
        self.neural_display = HolographicDisplay("NEURAL NETWORK")
        self.displays.append(self.neural_display)
        
        # Add displays to layout with spacing
        display_layout = QHBoxLayout()
        display_layout.setSpacing(20)
        display_layout.setContentsMargins(20, 20, 20, 20)
        
        for display in self.displays:
            # Add glow effect
            glow = QGraphicsDropShadowEffect()
            glow.setBlurRadius(20)
            glow.setColor(QColor(0, 255, 255, 100))
            glow.setOffset(0, 0)
            display.setGraphicsEffect(glow)
            
            display_layout.addWidget(display)
            
        self.layout().addLayout(display_layout)
        
    def reverse_animation(self, animation):
        # Reverse the animation direction
        start = animation.startValue()
        end = animation.endValue()
        animation.setStartValue(end)
        animation.setEndValue(start)
        animation.start()

    def update_interface(self):
        # Update displays with new data
        self.update_system_status()
        self.update_voice_analysis()
        self.update_data_processing()
        self.update()

    def update_system_status(self):
        # Update system monitoring information
        system_info = self.core.get_system_info()
        self.system_display.update_data(system_info)

    def update_voice_analysis(self):
        # Update voice analysis display
        voice_data = self.voice_engine.get_analysis()
        self.voice_display.update_data(voice_data)

    def update_data_processing(self):
        # Update data processing display
        processing_data = self.core.get_processing_status()
        self.data_display.update_data(processing_data)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background effects
        self.draw_background_effects(painter)

    def draw_background_effects(self, painter):
        # Draw holographic grid
        pen = QPen(QColor(0, 255, 255, 30))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Draw grid lines
        spacing = 50
        for x in range(0, self.width(), spacing):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), spacing):
            painter.drawLine(0, y, self.width(), y)

    def on_auth_success(self):
        """Handle successful authentication"""
        self.authenticated = True
        self.authentication_complete.emit(True)
        
        # Create transition animation
        fade = QPropertyAnimation(self.face_auth, "windowOpacity")
        fade.setDuration(1000)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.finished.connect(lambda: self.stack.setCurrentWidget(self.main_content))
        fade.start()
        
        # Update status
        self.status_label.setText("ACCESS GRANTED - JARVIS ACTIVATED")
        self.status_label.setStyleSheet("color: #00FF00; font-size: 24px;")
        
    def on_auth_failed(self):
        """Handle failed authentication"""
        self.authenticated = False
        self.authentication_complete.emit(False)
        
        # Update status
        self.status_label.setText("ACCESS DENIED - AUTHENTICATION FAILED")
        self.status_label.setStyleSheet("color: #FF0000; font-size: 24px;")

class HolographicDisplay(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.data = {}
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumSize(300, 400)
        self.setStyleSheet("""
            background-color: rgba(0, 30, 60, 50);
            border: 1px solid #00FFFF;
            border-radius: 10px;
        """)

    def update_data(self, data):
        self.data = data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw title
        painter.setPen(QColor("#00FFFF"))
        font = QFont("Consolas", 14)
        painter.setFont(font)
        painter.drawText(10, 30, self.title)
        
        # Draw data
        y = 60
        font = QFont("Consolas", 10)
        painter.setFont(font)
        for key, value in self.data.items():
            painter.drawText(20, y, f"{key}: {value}")
            y += 25