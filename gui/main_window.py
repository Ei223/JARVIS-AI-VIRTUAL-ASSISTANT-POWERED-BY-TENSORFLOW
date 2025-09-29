from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient
import os

class JarvisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # Set window properties
        self.setWindowTitle('J.A.R.V.I.S')
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(0, 0, 0, 230);
            }
        """)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Setup animation timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update)
        self.anim_timer.start(16)  # ~60 FPS
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create background gradient
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 30, 60, 200))
        gradient.setColorAt(1, QColor(0, 0, 30, 200))
        painter.fillRect(self.rect(), gradient)
        
        # Draw holographic grid
        self.draw_grid(painter)
        
    def draw_grid(self, painter):
        pen = QPen(QColor(0, 255, 242, 20))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Draw horizontal and vertical grid lines
        spacing = 30
        for x in range(0, self.width(), spacing):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), spacing):
            painter.drawLine(0, y, self.width(), y)
        self.update_timer.start(1000)
        
    def create_status_panel(self, layout, title, items):
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #00FFFF; font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)
        
        for item in items:
            label = QLabel(item)
            label.setStyleSheet("color: #00FFFF; font-size: 16px;")
            layout.addWidget(label)
            
    def update_stats(self):
        # Update system statistics here
        pass
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw holographic-style border
        pen = QPen(QColor(0, 255, 255, 100))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(1, 1, -1, -1))
        
    def keyPressEvent(self, event):
        # Press Esc to exit
        if event.key() == Qt.Key.Key_Escape:
            self.close()