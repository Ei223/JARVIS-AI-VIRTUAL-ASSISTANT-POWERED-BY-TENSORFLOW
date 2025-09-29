from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath, QLinearGradient
import random
import math

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    class Particle:
        def __init__(self, pos, velocity, life, color):
            self.pos = pos
            self.velocity = velocity
            self.life = life
            self.max_life = life
            self.color = color
            
    def emit(self, pos, count=1):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            velocity = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
            life = random.uniform(0.5, 2.0)
            color = QColor(0, random.randint(150, 255), random.randint(200, 255))
            self.particles.append(self.Particle(QPointF(pos), velocity, life, color))
            
    def update(self, dt):
        i = 0
        while i < len(self.particles):
            particle = self.particles[i]
            particle.pos += particle.velocity
            particle.life -= dt
            
            if particle.life <= 0:
                self.particles.pop(i)
            else:
                i += 1

class StartupAnimation(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.circuit_points = []
        self.animations = []
        self.opacity = 0
        self.fade_in = True
        self.particle_system = ParticleSystem()
        self.energy_rings = []
        
        # Initialize circuit board points
        self.initialize_circuit()
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # 60 FPS
        
        # Energy ring animation
        self.spawn_energy_ring_timer = QTimer(self)
        self.spawn_energy_ring_timer.timeout.connect(self.spawn_energy_ring)
        self.spawn_energy_ring_timer.start(2000)  # Spawn every 2 seconds

    def spawn_energy_ring(self):
        """Create a new energy ring at a random position"""
        width = self.width() or 1920
        height = self.height() or 1080
        x = random.randint(0, width)
        y = random.randint(0, height)
        self.energy_rings.append({
            'pos': QPointF(x, y),
            'radius': 0,
            'max_radius': random.randint(50, 150),
            'alpha': 255
        })

    def initialize_circuit(self):
        width = self.width() or 1920
        height = self.height() or 1080
        spacing = 50
        
        # Create grid points with better distribution
        for x in range(0, width, spacing):
            for y in range(0, height, spacing):
                if random.random() < 0.7:  # 70% chance of creating a point
                    offset_x = random.uniform(-10, 10)
                    offset_y = random.uniform(-10, 10)
                    self.circuit_points.append(QPointF(x + offset_x, y + offset_y))
                    
        # Create more organic connections between points
        for point in self.circuit_points:
            nearest = self.find_nearest_points(point, random.randint(2, 4))
            for end_point in nearest:
                self.animations.append({
                    'start': point,
                    'end': end_point,
                    'progress': random.uniform(0, 100),
                    'speed': random.uniform(0.5, 2.0),
                    'color': QColor(0, random.randint(150, 255), random.randint(200, 255)),
                    'width': random.uniform(1, 3)
                })

    def find_nearest_points(self, point, count):
        distances = []
        for p in self.circuit_points:
            if p != point:
                distance = ((p.x() - point.x()) ** 2 + (p.y() - point.y()) ** 2) ** 0.5
                distances.append((distance, p))
        distances.sort(key=lambda x: x[0])
        return [p[1] for p in distances[:count]]

    def update_animation(self):
        # Update circuit animations
        for anim in self.animations:
            anim['progress'] += anim['speed']
            if anim['progress'] > 100:
                anim['progress'] = 0

        # Update fade effect
        if self.fade_in:
            self.opacity = min(1.0, self.opacity + 0.02)
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set global opacity
        painter.setOpacity(self.opacity)
        
        # Draw circuit animations
        for anim in self.animations:
            progress = anim['progress'] / 100.0
            start = anim['start']
            end = anim['end']
            
            # Calculate current point along the line
            current_x = start.x() + (end.x() - start.x()) * progress
            current_y = start.y() + (end.y() - start.y()) * progress
            
            # Draw the circuit line
            painter.setPen(QPen(anim['color'], 2))
            painter.drawLine(int(start.x()), int(start.y()), int(current_x), int(current_y))
            
            # Draw glowing effect
            glow = QPainterPath()
            glow.addEllipse(QPointF(current_x, current_y), 5, 5)
            painter.fillPath(glow, anim['color'])

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.circuit_points.clear()
        self.animations.clear()
        self.initialize_circuit()