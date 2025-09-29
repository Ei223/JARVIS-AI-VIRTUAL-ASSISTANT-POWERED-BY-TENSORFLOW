from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QLinearGradient, QPainterPath
import math
import random

class HologramEffect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Hologram animation parameters
        self.scan_line_pos = 0
        self.flicker_intensity = 1.0
        self.glitch_offset = 0
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_effect)
        self.timer.start(16)
        
        # Glitch effect timer
        self.glitch_timer = QTimer(self)
        self.glitch_timer.timeout.connect(self.trigger_glitch)
        self.glitch_timer.start(random.randint(1000, 3000))

    def update_effect(self):
        # Update scan line
        self.scan_line_pos = (self.scan_line_pos + 2) % self.height()
        
        # Update flicker
        self.flicker_intensity = random.uniform(0.8, 1.0)
        
        self.update()

    def trigger_glitch(self):
        # Random glitch effect
        self.glitch_offset = random.randint(-5, 5)
        QTimer.singleShot(100, self.clear_glitch)
        self.glitch_timer.setInterval(random.randint(1000, 3000))

    def clear_glitch(self):
        self.glitch_offset = 0
        self.update()

    def paintEvent(self, event):
        if not self.parent():
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw parent widget to texture
        parent = self.parent()
        
        # Apply holographic effects
        self.draw_scan_line(painter)
        self.draw_edge_glow(painter)
        self.draw_interference(painter)
        
        if self.glitch_offset:
            self.draw_glitch(painter)

    def draw_scan_line(self, painter):
        gradient = QLinearGradient(0, self.scan_line_pos - 5, 0, self.scan_line_pos + 5)
        gradient.setColorAt(0, QColor(0, 255, 255, 0))
        gradient.setColorAt(0.5, QColor(0, 255, 255, 30))
        gradient.setColorAt(1, QColor(0, 255, 255, 0))
        
        painter.fillRect(0, self.scan_line_pos - 5, self.width(), 10, gradient)

    def draw_edge_glow(self, painter):
        glow = QPainterPath()
        glow.addRect(0, 0, self.width(), self.height())
        
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(0, 255, 255, 30))
        gradient.setColorAt(0.5, QColor(0, 255, 255, 0))
        gradient.setColorAt(1, QColor(0, 255, 255, 30))
        
        painter.strokePath(glow, QPen(gradient, 2))

    def draw_interference(self, painter):
        for _ in range(5):
            y = random.randint(0, self.height())
            opacity = random.randint(5, 15)
            painter.fillRect(0, y, self.width(), 1, QColor(0, 255, 255, opacity))

    def draw_glitch(self, painter):
        height = 10
        y = random.randint(0, self.height() - height)
        painter.save()
        painter.translate(self.glitch_offset, 0)
        painter.setOpacity(0.8)
        painter.drawPixmap(0, y, self.width(), height, self.grab(self.rect()))
        painter.restore()

class HolographicDisplay(QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.data = {}
        self.rotation = 0
        self.setup_ui()
        
        # Add hologram effect
        self.holo_effect = HologramEffect(self)
        
        # Rotation animation
        self.rotation_timer = QTimer(self)
        self.rotation_timer.timeout.connect(self.update_rotation)
        self.rotation_timer.start(50)

    def setup_ui(self):
        self.setMinimumSize(300, 400)
        self.setStyleSheet("""
            background-color: rgba(0, 30, 60, 50);
            border: 1px solid #00FFFF;
            border-radius: 10px;
        """)
        
        # Add drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 255, 255, 160))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def update_rotation(self):
        self.rotation = (self.rotation + 1) % 360
        self.update()

    def update_data(self, data):
        self.data = data
        self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'holo_effect'):
            self.holo_effect.setGeometry(self.rect())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 30, 60, 50))
        gradient.setColorAt(1, QColor(0, 20, 40, 50))
        painter.fillRect(self.rect(), gradient)
        
        # Draw title with glow
        painter.setPen(QColor("#00FFFF"))
        font = QFont("Consolas", 14)
        painter.setFont(font)
        
        # Draw rotating elements
        self.draw_rotating_elements(painter)
        
        # Draw data with dynamic effects
        self.draw_data(painter)

    def draw_rotating_elements(self, painter):
        center = self.rect().center()
        radius = min(self.width(), self.height()) * 0.4
        
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

    def draw_data(self, painter):
        y = 60
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