from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
import math

class ObjectDetectionVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.detections = []
        self.radius = 150
        self.rotation = 0
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_rotation)
        self.timer.start(16)  # 60 FPS
        
    def set_detections(self, detections):
        """Update current detections"""
        self.detections = detections
        self.update()
        
    def update_rotation(self):
        """Update ring rotation"""
        self.rotation += 0.5
        if self.rotation >= 360:
            self.rotation -= 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate center
        center = QPoint(self.width() // 2, self.height() // 2)
        
        # Draw detection ring
        if self.detections:
            angle_step = 360 / len(self.detections)
            for i, det in enumerate(self.detections):
                angle = math.radians(i * angle_step + self.rotation)
                
                # Calculate point position
                x = center.x() + math.cos(angle) * self.radius
                y = center.y() + math.sin(angle) * self.radius
                
                # Draw connecting line
                pen = QPen(QColor(0, 255, 255, 50), 1)
                painter.setPen(pen)
                painter.drawLine(center, QPoint(int(x), int(y)))
                
                # Draw detection point
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(QColor(0, 255, 255, 150)))
                painter.drawEllipse(QPoint(int(x), int(y)), 5, 5)
                
                # Draw label
                painter.setPen(QPen(QColor(0, 255, 255)))
                painter.drawText(
                    int(x + 10), int(y),
                    f"{det['class']} ({det['confidence']:.2f})"
                )