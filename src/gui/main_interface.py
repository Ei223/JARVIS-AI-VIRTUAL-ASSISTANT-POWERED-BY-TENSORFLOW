from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QPainterPath
import math
import random
from .holographic_widget import HolographicWidget

class MainInterface(QWidget):
    def __init__(self, jarvis_core):
        super().__init__()
        self.jarvis = jarvis_core
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface"""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add status display
        self.create_status_display(layout)
        
        # Add main content area
        self.create_main_content(layout)
        
        # Start update timer
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(1000)  # Update every second
        
    def create_status_display(self, parent_layout):
        """Create the top status display"""
        status_widget = HolographicWidget("SYSTEM STATUS")
        status_widget.setFixedHeight(100)
        
        # Status layout
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(20, 10, 20, 10)
        
        # Add status items
        self.time_label = QLabel("00:00:00")
        self.time_label.setStyleSheet("color: #00FFFF; font-size: 24px;")
        status_layout.addWidget(self.time_label)
        
        self.status_label = QLabel("All Systems Online")
        self.status_label.setStyleSheet("color: #00FFFF; font-size: 24px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        parent_layout.addWidget(status_widget)
        
    def create_main_content(self, parent_layout):
        """Create the main content area with holographic displays"""
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # System monitoring display
        self.system_monitor = HolographicWidget("SYSTEM MONITOR")
        content_layout.addWidget(self.system_monitor)
        
        # Voice interaction display
        self.voice_display = HolographicWidget("VOICE INTERFACE")
        content_layout.addWidget(self.voice_display)
        
        # Neural network display
        self.neural_display = HolographicWidget("NEURAL NETWORK")
        content_layout.addWidget(self.neural_display)
        
        # Add to main layout
        parent_layout.addLayout(content_layout)
        
    def update_displays(self):
        """Update all display information"""
        # Update time
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)
        
        # Update system monitor
        system_info = self.jarvis.get_system_status()
        self.system_monitor.set_data({
            "CPU Usage": f"{system_info['cpu']}%",
            "Memory": f"{system_info['memory']}%",
            "Disk": f"{system_info['disk']}%"
        })
        
        # Other updates can be added here
        
    def paintEvent(self, event):
        """Custom paint event for background effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background grid
        self.draw_background_grid(painter)
        
    def draw_background_grid(self, painter):
        """Draw a holographic grid in the background"""
        pen = QPen(QColor(0, 255, 255, 20))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Draw horizontal lines
        spacing = 50
        for y in range(0, self.height(), spacing):
            painter.drawLine(0, y, self.width(), y)
            
        # Draw vertical lines
        for x in range(0, self.width(), spacing):
            painter.drawLine(x, 0, x, self.height())