from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QEasingCurve, QPointF, QRectF, QPropertyAnimation, QParallelAnimationGroup
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QRadialGradient, QBrush, QTransform
import math
import random
import psutil
import numpy as np
from .font_manager import FontManager

class CommandVisualizer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_manager = FontManager()
        self.command_queue = []
        self.current_command = None
        self.fade_animation = None
        self.opacity = 0.0
        
    def add_command(self, command: str, response: str):
        self.command_queue.append((command, response))
        if not self.current_command:
            self.show_next_command()
            
    def show_next_command(self):
        if self.command_queue:
            self.current_command = self.command_queue.pop(0)
            self.start_fade_animation()
            
    def start_fade_animation(self):
        self.opacity = 0.0
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.finished.connect(self.fade_out_after_delay)
        self.fade_animation.start()
        
    def fade_out_after_delay(self):
        QTimer.singleShot(3000, self.start_fade_out)
        
    def start_fade_out(self):
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.show_next_command)
        self.fade_animation.start()
        
    def paintEvent(self, event):
        if not self.current_command:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        command, response = self.current_command
        painter.setOpacity(self.opacity)
        
        # Draw command
        command_font = self.font_manager.get_appropriate_font(command, 16, True)
        painter.setFont(command_font)
        painter.setPen(QColor("#00FFFF"))
        painter.drawText(10, 30, command)
        
        # Draw response
        response_font = self.font_manager.get_appropriate_font(response, 14)
        painter.setFont(response_font)
        painter.setPen(QColor("#00FFFF"))
        painter.drawText(10, 60, response)

class ParticleSystem:
    def __init__(self, max_particles=100):
        self.particles = []
        self.max_particles = max_particles
        
    def create_particle(self, pos, velocity, life=1.0):
        if len(self.particles) < self.max_particles:
            self.particles.append({
                'pos': pos,
                'velocity': velocity,
                'life': life,
                'original_life': life
            })
            
    def update(self):
        self.particles = [p for p in self.particles if p['life'] > 0]
        for p in self.particles:
            p['pos'] = QPoint(p['pos'].x() + p['velocity'][0], 
                            p['pos'].y() + p['velocity'][1])
            p['life'] -= 0.016

class CircularInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S")
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Initialize components
        self.rings = []
        self.particles = ParticleSystem(max_particles=200)
        self.data_points = []
        self.fps = 0
        self.last_time = 0
        
        # Create multiple rings with different properties and effects
        for i in range(3):
            self.rings.append({
                'radius': 150 + i * 50,
                'width': 4 - i,
                'rotation': random.uniform(0, 360),
                'speed': 0.3 - i * 0.1,
                'data_points': [],
                'glow_intensity': 0.8 - i * 0.2
            })
            
            # Add data points to each ring
            num_points = 8 + i * 4
            for j in range(num_points):
                angle = (j * 360 / num_points)
                self.rings[i]['data_points'].append({
                    'angle': angle,
                    'value': random.random(),
                    'target_value': random.random(),
                    'color': QColor(0, 255, 255, 150)
                })
            
        # Setup timers
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(16)  # 60 FPS
        
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_system_data)
        self.data_timer.start(1000)  # Update system data every second
        
        # Initialize effects
        self.glow_animation = QPropertyAnimation(self, b"windowOpacity")
        self.glow_animation.setDuration(2000)
        self.glow_animation.setStartValue(0.0)
        self.glow_animation.setEndValue(1.0)
        self.glow_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.glow_animation.start()
        
        self.showFullScreen()
        
    def update_animation(self):
        # Update rings
        for ring in self.rings:
            ring['rotation'] += ring['speed']
            if ring['rotation'] >= 360:
                ring['rotation'] = 0
            
            # Animate data points
            for point in ring['data_points']:
                if random.random() < 0.05:  # 5% chance to change target
                    point['target_value'] = random.random()
                point['value'] += (point['target_value'] - point['value']) * 0.1
                
        # Update particles
        self.particles.update()
        
        # Create new particles occasionally
        if random.random() < 0.1:
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(100, 300)
            x = self.width() / 2 + math.cos(angle) * radius
            y = self.height() / 2 + math.sin(angle) * radius
            self.create_particles_at(QPoint(int(x), int(y)), 3)
            
        self.update()
        
    def update_system_data(self):
        """Update system statistics for visualization"""
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        
        # Update ring data based on system stats
        if self.rings:
            # CPU usage affects inner ring
            for point in self.rings[0]['data_points']:
                point['target_value'] = cpu / 100.0
            
            # Memory usage affects middle ring
            if len(self.rings) > 1:
                for point in self.rings[1]['data_points']:
                    point['target_value'] = memory / 100.0
            
        # Update existing points
        i = 0
        while i < len(self.data_points):
            point = self.data_points[i]
            point['life'] -= 0.02
            if point['life'] <= 0:
                self.data_points.pop(i)
            else:
                i += 1
                
        self.update()
    
    def create_particles_at(self, pos, count=5):
        """Create particle burst at given position"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.create_particle(pos, velocity, 1.0)
    
    def mousePressEvent(self, event):
        """Create particle burst on click"""
        self.create_particles_at(event.pos(), 10)
        super().mousePressEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Calculate center
        center = QPoint(self.width() // 2, self.height() // 2)
        
        # Draw background glow
        gradient = QRadialGradient(center, 300)
        gradient.setColorAt(0, QColor(0, 255, 255, 20))
        gradient.setColorAt(0.5, QColor(0, 255, 255, 10))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 300, 300)
        
        # Draw rings
        for ring in self.rings:
            # Draw base ring
            pen = QPen(QColor(0, 255, 255, 100), ring['width'])
            painter.setPen(pen)
            painter.drawEllipse(center, ring['radius'], ring['radius'])
            
            # Draw data points and connections
            for i, point in enumerate(ring['data_points']):
                angle_rad = math.radians(point['angle'] + ring['rotation'])
                radius = ring['radius'] * (0.9 + point['value'] * 0.2)  # Vary radius based on value
                x = center.x() + math.cos(angle_rad) * radius
                y = center.y() + math.sin(angle_rad) * radius
                
                # Draw data point with glow
                gradient = QRadialGradient(QPointF(x, y), 10)
                color = point['color']
                gradient.setColorAt(0, color)
                gradient.setColorAt(1, QColor(0, 255, 255, 0))
                painter.setBrush(gradient)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(x, y), 5, 5)
                
                # Draw connecting lines to next point
                next_point = ring['data_points'][(i + 1) % len(ring['data_points'])]
                next_angle = math.radians(next_point['angle'] + ring['rotation'])
                next_radius = ring['radius'] * (0.9 + next_point['value'] * 0.2)
                next_x = center.x() + math.cos(next_angle) * next_radius
                next_y = center.y() + math.sin(next_angle) * next_radius
                
                # Draw connection with fade effect
                path = QPainterPath()
                path.moveTo(x, y)
                
                # Calculate control points for curved line
                ctrl1_x = x + (next_x - x) * 0.5 - (next_y - y) * 0.2
                ctrl1_y = y + (next_y - y) * 0.5 + (next_x - x) * 0.2
                ctrl2_x = x + (next_x - x) * 0.5 + (next_y - y) * 0.2
                ctrl2_y = y + (next_y - y) * 0.5 - (next_x - x) * 0.2
                
                path.cubicTo(
                    ctrl1_x, ctrl1_y,
                    ctrl2_x, ctrl2_y,
                    next_x, next_y
                )
                
                pen = QPen(QColor(0, 255, 255, 50), 1)
                painter.setPen(pen)
                painter.drawPath(path)
        
        # Draw particles
        for particle in self.particles.particles:
            alpha = int(255 * (particle['life'] / particle['original_life']))
            painter.setPen(QPen(QColor(0, 255, 255, alpha), 2))
            painter.drawPoint(particle['pos'])
        
        # Draw center core
        core_gradient = QRadialGradient(center, 40)
        core_gradient.setColorAt(0, QColor(0, 255, 255, 255))
        core_gradient.setColorAt(0.4, QColor(0, 255, 255, 150))
        core_gradient.setColorAt(1, QColor(0, 255, 255, 0))
        painter.setBrush(core_gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, 40, 40)
        
        # Draw inner core
        inner_gradient = QRadialGradient(center, 20)
        inner_gradient.setColorAt(0, QColor(255, 255, 255, 255))
        inner_gradient.setColorAt(1, QColor(0, 255, 255, 100))
        painter.setBrush(inner_gradient)
        painter.drawEllipse(center, 20, 20)
        
        # Set center point
        center = QPointF(self.width() / 2, self.height() / 2)
        
        # Draw outer ring
        for ring in self.rings:
            self.drawRing(painter, center, ring)
            
        # Draw data points
        for point in self.data_points:
            self.drawDataPoint(painter, center, point)
            
        # Draw center circle
        self.drawCenterCircle(painter, center)
        
    def drawRing(self, painter, center, ring):
        segments = ring['segments']
        radius = ring['radius']
        rotation = ring['rotation']
        
        pen = QPen(QColor(0, 255, 255, 100))
        pen.setWidth(2)
        painter.setPen(pen)
        
        for i in range(segments):
            angle1 = math.radians(i * (360 / segments) + rotation)
            angle2 = math.radians((i + 1) * (360 / segments) + rotation)
            
            # Calculate points
            x1 = center.x() + radius * math.cos(angle1)
            y1 = center.y() + radius * math.sin(angle1)
            x2 = center.x() + radius * math.cos(angle2)
            y2 = center.y() + radius * math.sin(angle2)
            
            # Draw segment
            if i % 2 == 0:  # Skip every other segment for dashed effect
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
                
    def drawDataPoint(self, painter, center, point):
        angle = math.radians(point['angle'])
        x = center.x() + point['distance'] * math.cos(angle)
        y = center.y() + point['distance'] * math.sin(angle)
        
        color = QColor(0, 255, 255, int(255 * point['life']))
        painter.setPen(QPen(color))
        painter.setBrush(color)
        
        painter.drawEllipse(QPointF(x, y), point['size'], point['size'])
        
    def drawCenterCircle(self, painter, center):
        # Inner glow
        gradient_radius = 100
        for i in range(20):
            alpha = 150 - i * 7
            if alpha > 0:
                color = QColor(0, 255, 255, alpha)
                pen = QPen(color)
                pen.setWidth(2)
                painter.setPen(pen)
                current_radius = 80 - i * 2
                painter.drawEllipse(center, current_radius, current_radius)
                
        # Center core
        painter.setPen(QPen(QColor(0, 255, 255, 255)))
        painter.setBrush(QColor(0, 255, 255, 100))
        painter.drawEllipse(center, 40, 40)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()