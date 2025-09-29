from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QPainterPath
import math
import random

class HolographicWidget(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.data = {}
        self.rotation = 0
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        """Initialize the widget UI"""
        self.setMinimumSize(300, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Add glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 255, 255, 160))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)
        
    def setup_animations(self):
        """Setup widget animations"""
        # Rotation animation
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.update_rotation)
        self.rotation_timer.start(50)
        
        # Scan line animation
        self.scan_line_pos = 0
        self.scan_line_direction = 1
        
        # Floating animation
        self.float_animation = QPropertyAnimation(self, b"pos")
        self.float_animation.setDuration(3000)
        self.float_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.float_animation.finished.connect(self.reverse_float_animation)
        self.start_float_animation()
        
    def start_float_animation(self):
        """Start the floating animation"""
        start_pos = self.pos()
        self.float_animation.setStartValue(start_pos)
        self.float_animation.setEndValue(start_pos + QPointF(0, 10))
        self.float_animation.start()
        
    def reverse_float_animation(self):
        """Reverse the floating animation"""
        start_pos = self.float_animation.endValue()
        end_pos = self.float_animation.startValue()
        self.float_animation.setStartValue(start_pos)
        self.float_animation.setEndValue(end_pos)
        self.float_animation.start()
        
    def update_rotation(self):
        """Update the rotation angle"""
        self.rotation = (self.rotation + 1) % 360
        self.update()
        
    def set_data(self, data):
        """Update the widget's data"""
        self.data = data
        self.update()
        
    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        self.draw_background(painter)
        
        # Draw rotating elements
        self.draw_rotating_elements(painter)
        
        # Draw content
        self.draw_content(painter)
        
        # Draw scan line
        self.draw_scan_line(painter)
        
        # Draw border
        self.draw_border(painter)
        
    def draw_background(self, painter):
        """Draw the widget background"""
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 30, 60, 50))
        gradient.setColorAt(1, QColor(0, 20, 40, 50))
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        painter.fillPath(path, gradient)
        
    def draw_rotating_elements(self, painter):
        """Draw rotating decorative elements"""
        center = self.rect().center()
        radius = min(self.width(), self.height()) * 0.3
        
        painter.save()
        painter.translate(center.x(), center.y())
        painter.rotate(self.rotation)
        
        # Draw circular elements
        pen = QPen(QColor(0, 255, 255, 30))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(0, 0), radius, radius)
        
        # Draw radial lines
        for i in range(8):
            angle = i * 45
            x = radius * math.cos(math.radians(angle))
            y = radius * math.sin(math.radians(angle))
            painter.drawLine(0, 0, x, y)
            
        painter.restore()
        
    def draw_content(self, painter):
        """Draw the widget content"""
        # Draw title
        painter.setPen(QColor("#00FFFF"))
        font = QFont("Consolas", 14)
        painter.setFont(font)
        painter.drawText(20, 30, self.title)
        
        # Draw data
        y = 70
        font = QFont("Consolas", 10)
        painter.setFont(font)
        
        for key, value in self.data.items():
            # Create glowing text effect
            glow = QPainterPath()
            glow.addText(20, y, font, f"{key}: {value}")
            
            # Draw glow
            glow_color = QColor(0, 255, 255, 30)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow_color)
            painter.drawPath(glow)
            
            # Draw text
            painter.setPen(QColor("#00FFFF"))
            painter.drawText(20, y, f"{key}: {value}")
            
            y += 25
            
    def draw_scan_line(self, painter):
        """Draw animated scan line effect"""
        # Update scan line position
        self.scan_line_pos += 2 * self.scan_line_direction
        if self.scan_line_pos >= self.height():
            self.scan_line_direction = -1
        elif self.scan_line_pos <= 0:
            self.scan_line_direction = 1
            
        # Draw scan line
        gradient = QLinearGradient(0, self.scan_line_pos - 5, 0, self.scan_line_pos + 5)
        gradient.setColorAt(0, QColor(0, 255, 255, 0))
        gradient.setColorAt(0.5, QColor(0, 255, 255, 30))
        gradient.setColorAt(1, QColor(0, 255, 255, 0))
        
        painter.fillRect(0, self.scan_line_pos - 5, self.width(), 10, gradient)
        
    def draw_border(self, painter):
        """Draw widget border with glow effect"""
        pen = QPen(QColor(0, 255, 255, 100))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRoundedRect(1, 1, self.width()-2, self.height()-2, 10, 10)