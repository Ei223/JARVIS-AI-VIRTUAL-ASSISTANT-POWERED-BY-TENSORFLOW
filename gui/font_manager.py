from PyQt6.QtGui import QFont, QFontDatabase
from typing import Optional, Dict
import os

class FontManager:
    """Utility class for managing fonts and text rendering"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.fonts = {}
            self.load_fonts()
    
    def load_fonts(self):
        """Load custom fonts including Hindi fonts"""
        font_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'fonts')
        os.makedirs(font_dir, exist_ok=True)
        
        # Define font files to load - you'll need to add these font files
        font_files = {
            'hindi': 'Noto-Sans-Devanagari.ttf',
            'scifi': 'Orbitron-Regular.ttf',
            'monospace': 'JetBrainsMono-Regular.ttf'
        }
        
        for font_type, filename in font_files.items():
            font_path = os.path.join(font_dir, filename)
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id >= 0:
                    self.fonts[font_type] = QFontDatabase.applicationFontFamilies(font_id)[0]
                    print(f"Loaded font: {font_type}")
                else:
                    print(f"Failed to load font: {font_type}")
            else:
                print(f"Font file not found: {filename}")
    
    def get_font(self, font_type: str = 'scifi', size: int = 12, bold: bool = False) -> QFont:
        """Get a font with the specified properties"""
        if font_type in self.fonts:
            font = QFont(self.fonts[font_type], size)
        else:
            # Fallback fonts for different purposes
            fallbacks = {
                'hindi': 'Noto Sans Devanagari',
                'scifi': 'Orbitron',
                'monospace': 'JetBrains Mono',
            }
            font = QFont(fallbacks.get(font_type, 'Arial'), size)
        
        font.setBold(bold)
        return font
    
    def get_text_style(self, font_type: str = 'scifi', size: int = 12, 
                      color: str = '#00FFFF', bold: bool = False) -> str:
        """Get CSS style string for text"""
        family = self.fonts.get(font_type, 'Arial')
        weight = 'bold' if bold else 'normal'
        return f"""
            font-family: '{family}';
            font-size: {size}px;
            color: {color};
            font-weight: {weight};
        """
    
    def is_hindi_text(self, text: str) -> bool:
        """Check if text contains Hindi characters"""
        return any('\u0900' <= c <= '\u097F' for c in text)
    
    def get_appropriate_font(self, text: str, size: int = 12, bold: bool = False) -> QFont:
        """Get appropriate font based on text content"""
        font_type = 'hindi' if self.is_hindi_text(text) else 'scifi'
        return self.get_font(font_type, size, bold)