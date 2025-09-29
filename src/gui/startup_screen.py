from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient
import random
import math

class ParticleSystem:
    """Particle system for visual effects"""
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

class StartupScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.setup_animation()
        
    def setup_animation(self):
        """Initialize animation components"""
        self.circuit_points = []
        self.connections = []
        self.particle_system = ParticleSystem()
        self.energy_rings = []
        self.opacity = 0
        self.fade_in = True
        
        # Create circuit board points
        self.create_circuit_points()
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # 60 FPS
        
        # Energy ring spawner
        self.ring_timer = QTimer(self)
        self.ring_timer.timeout.connect(self.spawn_energy_ring)
        self.ring_timer.start(2000)  # Spawn ring every 2 seconds
        
    def create_circuit_points(self):
        """Create the circuit board layout"""
        width = self.width() or 1920
        height = self.height() or 1080
        spacing = 50
        
        # Create grid of points with slight randomization
        for x in range(0, width, spacing):
            for y in range(0, height, spacing):
                if random.random() < 0.7:  # 70% chance to create a point
                    offset_x = random.uniform(-10, 10)
                    offset_y = random.uniform(-10, 10)
                    point = QPointF(x + offset_x, y + offset_y)
                    self.circuit_points.append(point)
                    
        # Create connections between nearby points
        for point in self.circuit_points:
            nearest = self.find_nearest_points(point)
            for end_point in nearest:
                self.connections.append({
                    'start': point,
                    'end': end_point,
                    'progress': random.uniform(0, 100),
                    'speed': random.uniform(0.5, 2.0),
                    'color': QColor(0, random.randint(150, 255), random.randint(200, 255)),
                    'width': random.uniform(1, 3)
                })
                
    def find_nearest_points(self, point, count=3):
        """Find nearest points for connections"""
        distances = []
        for p in self.circuit_points:
            if p != point:
                distance = ((p.x() - point.x()) ** 2 + (p.y() - point.y()) ** 2) ** 0.5
                if distance < 200:  # Only connect points within range
                    distances.append((distance, p))
        distances.sort(key=lambda x: x[0])
        return [p[1] for p in distances[:count]]
        
    def spawn_energy_ring(self):
        """Create a new energy ring effect"""
        if self.circuit_points:
            center = random.choice(self.circuit_points)
            self.energy_rings.append({
                'center': center,
                'radius': 0,
                'max_radius': random.uniform(100, 200),
                'color': QColor(0, random.randint(150, 255), random.randint(200, 255), 150)
            })
            
    def update_animation(self):
        """Update all animation elements"""
        # Update circuit connections
        for conn in self.connections:
            conn['progress'] += conn['speed']
            if conn['progress'] > 100:
                conn['progress'] = 0
                # Emit particles at end point
                self.particle_system.emit(conn['end'], count=2)
                
        # Update energy rings
        i = 0
        while i < len(self.energy_rings):
            ring = self.energy_rings[i]
            ring['radius'] += 2
            if ring['radius'] > ring['max_radius']:
                self.energy_rings.pop(i)
            else:
                i += 1
                
        # Update particles
        self.particle_system.update(0.016)
        
        # Update fade effect
        if self.fade_in:
            self.opacity = min(1.0, self.opacity + 0.02)
            
        self.update()
        
    def paintEvent(self, event):
        """Render the animation"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set global opacity
        painter.setOpacity(self.opacity)
        
        # Draw energy rings
        for ring in self.energy_rings:
            self.draw_energy_ring(painter, ring)
            
        # Draw circuit connections
        for conn in self.connections:
            self.draw_connection(painter, conn)
            
        # Draw particles
        for particle in self.particle_system.particles:
            self.draw_particle(painter, particle)
            
    def draw_energy_ring(self, painter, ring):
        """Draw an energy ring effect"""
        gradient = QLinearGradient(ring['center'], 
                                 QPointF(ring['center'].x(), ring['center'].y() + ring['radius']))
        color = ring['color']
        gradient.setColorAt(0, color)
        color.setAlpha(0)
        gradient.setColorAt(1, color)
        
        pen = QPen()
        pen.setWidth(2)
        pen.setBrush(gradient)
        painter.setPen(pen)
        painter.drawEllipse(ring['center'], ring['radius'], ring['radius'])
        
    def draw_connection(self, painter, conn):
        """Draw a circuit connection line"""
        progress = conn['progress'] / 100.0
        start = conn['start']
        end = conn['end']
        
        # Calculate current point
        current_x = start.x() + (end.x() - start.x()) * progress
        current_y = start.y() + (end.y() - start.y()) * progress
        
        # Create gradient effect
        gradient = QLinearGradient(start, QPointF(current_x, current_y))
        gradient.setColorAt(0, conn['color'])
        color = QColor(conn['color'])
        color.setAlpha(0)
        gradient.setColorAt(1, color)
        
        # Draw line
        pen = QPen()
        pen.setWidth(conn['width'])
        pen.setBrush(gradient)
        painter.setPen(pen)
        painter.drawLine(start.x(), start.y(), current_x, current_y)
        
        # Draw glow effect at current point
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(conn['color'])
        painter.drawEllipse(QPointF(current_x, current_y), 5, 5)
        
    def draw_particle(self, painter, particle):
        """Draw a particle effect"""
        color = QColor(particle.color)
        color.setAlpha(int(255 * (particle.life / particle.max_life)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(particle.pos, 3, 3)
        
    def resizeEvent(self, event):
        """Handle window resize"""
        super().resizeEvent(event)
        self.circuit_points.clear()
        self.connections.clear()
        self.create_circuit_points()