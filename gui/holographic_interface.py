from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPointF, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QRadialGradient, QPainterPath, QFont
import math, random
import psutil

class HolographicInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initCore()
        
    def initCore(self):
        # Initialize JARVIS core systems
        from core.jarvis_core import JarvisCore
        from core.voice_engine import VoiceEngine
        
        self.core = JarvisCore()
        self.voice = VoiceEngine()
        self.voice.start_listening()
        
        # Timer to check for voice commands
        self.command_timer = QTimer()
        self.command_timer.timeout.connect(self.check_commands)
        self.command_timer.start(100)  # Check every 100ms
        
    def initUI(self):
        # Set window properties for holographic effect
        self.setWindowTitle('J.A.R.V.I.S.')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1920, 1080)
        
        # Initialize effects
        self.particles = []
        self.energy_rings = []
        self.holo_elements = []
        self.angle = 0
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.start(16)  # 60 FPS
        
        # Add floating elements
        self.initializeHolographicElements()
        
    def initializeHolographicElements(self):
        # Create arc reactor core
        self.core_size = 150
        self.core_rings = 3
        self.core_particles = []
        
        # Create holographic circles
        for i in range(5):
            self.energy_rings.append({
                'radius': 100 + i * 50,
                'rotation': random.uniform(0, 360),
                'speed': random.uniform(0.5, 2.0),
                'opacity': random.uniform(0.3, 0.8)
            })
            
        # Initialize particle system
        for _ in range(100):
            self.particles.append({
                'pos': QPointF(random.randint(0, self.width()), 
                             random.randint(0, self.height())),
                'velocity': QPointF(random.uniform(-1, 1), 
                                  random.uniform(-1, 1)),
                'life': random.uniform(0.5, 1.0),
                'size': random.uniform(2, 5)
            })
    
    def check_commands(self):
        """Check for and process voice commands"""
        command = self.voice.get_command()
        if command:
            # Process the command
            response = self.core.process_command(command)
            # Speak the response
            self.voice.speak(response)
            # Update UI with the command and response
            self.update_command_display(command, response)
            # Trigger special effects
            self.trigger_command_effects()
    
    def update_command_display(self, command, response):
        """Update the UI with command and response"""
        self.last_command = command
        self.last_response = response
        self.command_opacity = 1.0
        self.response_opacity = 1.0
        self.update()
        
    def trigger_command_effects(self):
        """Trigger special effects when command is processed"""
        # Add an energy ring
        self.energy_rings.append({
            'radius': 100,
            'rotation': random.uniform(0, 360),
            'speed': random.uniform(1.0, 3.0),
            'opacity': 1.0
        })
        
        # Add more particles
        for _ in range(20):
            self.particles.append({
                'pos': QPointF(self.width()/2, self.height()/2),
                'velocity': QPointF(random.uniform(-2, 2), random.uniform(-2, 2)),
                'life': 1.0,
                'size': random.uniform(3, 6)
            })
    
    def updateAnimation(self):
        # Update arc reactor rotation
        self.angle += 1
        if self.angle >= 360:
            self.angle = 0
            
        # Update energy rings with fade-out
        i = 0
        while i < len(self.energy_rings):
            ring = self.energy_rings[i]
            ring['rotation'] += ring['speed']
            ring['opacity'] -= 0.01
            
            if ring['opacity'] <= 0:
                self.energy_rings.pop(i)
            else:
                i += 1
            
        # Update particles
        for particle in self.particles:
            particle['pos'] += particle['velocity']
            particle['life'] -= 0.01
            
            if particle['life'] <= 0:
                particle['pos'] = QPointF(random.randint(0, self.width()), 
                                        random.randint(0, self.height()))
                particle['life'] = 1.0
                
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with gradient
        gradient = QRadialGradient(self.width()/2, self.height()/2, 
                                 max(self.width(), self.height()))
        gradient.setColorAt(0, QColor(0, 40, 80, 50))
        gradient.setColorAt(1, QColor(0, 0, 0, 30))
        painter.fillRect(self.rect(), gradient)
        
        # Draw system status
        self.draw_system_status(painter)
        
        # Draw command and response
        if hasattr(self, 'last_command'):
            self.draw_command_interface(painter)
        
        # Draw arc reactor
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Draw core rings
        for i in range(self.core_rings):
            pen = QPen(QColor(0, 200, 255, 150 - i * 30))
            pen.setWidth(3)
            painter.setPen(pen)
            radius = self.core_size - i * 20
            painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
            
        # Draw rotating elements
        for i in range(6):
            angle = self.angle + (i * 60)
            rad = math.radians(angle)
            x = center_x + math.cos(rad) * self.core_size
            y = center_y + math.sin(rad) * self.core_size
            
            painter.setPen(QPen(QColor(0, 255, 255, 200)))
            painter.drawLine(int(center_x), int(center_y), int(x), int(y))
            
        # Draw energy rings
        for ring in self.energy_rings:
            pen = QPen(QColor(0, 255, 255, int(ring['opacity'] * 255)))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.save()
            painter.translate(center_x, center_y)
            painter.rotate(ring['rotation'])
            painter.drawEllipse(QPointF(0, 0), ring['radius'], ring['radius'])
            painter.restore()
            
        # Draw particles
        for particle in self.particles:
            color = QColor(0, 255, 255, int(particle['life'] * 255))
            painter.setPen(QPen(color))
            painter.setBrush(color)
            painter.drawEllipse(particle['pos'], particle['size'], particle['size'])
            
    def draw_system_status(self, painter):
        """Draw system status information"""
        # Set up text properties
        painter.setPen(QPen(QColor(0, 255, 255, 200)))
        painter.setFont(QFont('Arial', 12))
        
        # Draw status boxes
        status_items = [
            ('CPU Usage', f"{psutil.cpu_percent()}%"),
            ('Memory', f"{psutil.virtual_memory().percent}%"),
            ('Network', 'Connected'),
            ('Voice System', 'Active'),
            ('Face Recognition', 'Ready')
        ]
        
        x = 50
        y = 50
        for label, value in status_items:
            # Draw box
            painter.drawRect(x, y, 200, 30)
            # Draw label
            painter.drawText(x + 10, y + 20, f"{label}: {value}")
            y += 40
            
    def draw_command_interface(self, painter):
        """Draw command interface with holographic effects"""
        # Draw command area
        center_x = self.width() / 2
        center_y = self.height() - 200
        
        # Set up text properties
        painter.setFont(QFont('Arial', 14))
        
        # Draw command
        if hasattr(self, 'last_command'):
            painter.setPen(QPen(QColor(0, 255, 255, int(getattr(self, 'command_opacity', 1.0) * 255))))
            painter.drawText(
                QRect(int(center_x - 300), int(center_y), 600, 30),
                Qt.AlignmentFlag.AlignCenter,
                f"Command: {self.last_command}"
            )
        
        # Draw response
        if hasattr(self, 'last_response'):
            painter.setPen(QPen(QColor(0, 255, 255, int(getattr(self, 'response_opacity', 1.0) * 255))))
            painter.drawText(
                QRect(int(center_x - 400), int(center_y + 40), 800, 60),
                Qt.AlignmentFlag.AlignCenter,
                f"Response: {self.last_response}"
            )
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            
    def closeEvent(self, event):
        """Clean up when closing"""
        self.voice.stop_listening()
        super().closeEvent(event)