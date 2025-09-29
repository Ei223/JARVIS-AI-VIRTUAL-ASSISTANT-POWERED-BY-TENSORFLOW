from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient
from .startup_screen import StartupScreen
from .main_interface import MainInterface
import pygame

class JarvisWindow(QMainWindow):
    def __init__(self, jarvis_core):
        super().__init__()
        self.jarvis = jarvis_core
        self.setup_window()
        self.initialize_audio()
        self.show_startup_screen()
        
    def setup_window(self):
        """Set up the main window properties"""
        self.setWindowTitle("J.A.R.V.I.S")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
    def initialize_audio(self):
        """Initialize audio system for sound effects"""
        pygame.mixer.init()
        self.load_sound_effects()
        
    def load_sound_effects(self):
        """Load sound effects"""
        try:
            self.sounds = {
                'startup': pygame.mixer.Sound('assets/sounds/startup.wav'),
                'transition': pygame.mixer.Sound('assets/sounds/transition.wav'),
                'notification': pygame.mixer.Sound('assets/sounds/notification.wav')
            }
        except:
            print("Warning: Could not load sound effects")
            self.sounds = {}
            
    def show_startup_screen(self):
        """Show the startup animation screen"""
        self.startup_screen = StartupScreen()
        self.layout.addWidget(self.startup_screen)
        
        # Play startup sound
        if 'startup' in self.sounds:
            self.sounds['startup'].play()
            
        # Set timer to switch to main interface
        QTimer.singleShot(5000, self.transition_to_main)
        
    def transition_to_main(self):
        """Transition from startup to main interface"""
        # Create fade out animation
        fade_out = QPropertyAnimation(self.startup_screen, b"windowOpacity")
        fade_out.setDuration(1000)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.finished.connect(self.show_main_interface)
        fade_out.start()
        
        # Play transition sound
        if 'transition' in self.sounds:
            self.sounds['transition'].play()
            
    def show_main_interface(self):
        """Show the main JARVIS interface"""
        # Remove startup screen
        self.startup_screen.deleteLater()
        
        # Create main interface
        self.main_interface = MainInterface(self.jarvis)
        self.main_interface.setWindowOpacity(0.0)
        self.layout.addWidget(self.main_interface)
        
        # Create fade in animation
        fade_in = QPropertyAnimation(self.main_interface, b"windowOpacity")
        fade_in.setDuration(1000)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.start()
        
        # Start JARVIS systems
        self.jarvis.start()
        
    def paintEvent(self, event):
        """Custom paint event for window effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create background gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 0, 0, 200))
        gradient.setColorAt(1, QColor(0, 0, 0, 230))
        
        painter.fillRect(self.rect(), gradient)
        
        # Draw border glow
        glow_color = QColor(0, 255, 255, 30)
        pen = QPen(glow_color)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect())