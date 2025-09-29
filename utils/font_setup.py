import os
import requests
import zipfile
import shutil
from pathlib import Path

def setup_fonts():
    """Download and set up required fonts for JARVIS"""
    # Create fonts directory if it doesn't exist
    base_dir = Path(__file__).parent.parent
    fonts_dir = base_dir / 'assets' / 'fonts'
    fonts_dir.mkdir(parents=True, exist_ok=True)
    
    # Font URLs and their filenames
    fonts = {
        'Noto Sans Devanagari': {
            'url': 'https://fonts.google.com/download?family=Noto+Sans+Devanagari',
            'filename': 'NotoSansDevanagari.zip',
            'target_file': 'NotoSansDevanagari-Regular.ttf'
        },
        'Orbitron': {
            'url': 'https://fonts.google.com/download?family=Orbitron',
            'filename': 'Orbitron.zip',
            'target_file': 'Orbitron-Regular.ttf'
        },
        'JetBrains Mono': {
            'url': 'https://download.jetbrains.com/fonts/JetBrainsMono-2.304.zip',
            'filename': 'JetBrainsMono.zip',
            'target_file': 'JetBrainsMono-Regular.ttf'
        }
    }
    
    for font_name, font_info in fonts.items():
        print(f"\nProcessing {font_name}...")
        zip_path = fonts_dir / font_info['filename']
        
        # Check if font is already installed
        if (fonts_dir / font_info['target_file']).exists():
            print(f"{font_name} is already installed.")
            continue
            
        try:
            # Download font
            print(f"Downloading {font_name}...")
            response = requests.get(font_info['url'])
            response.raise_for_status()
            
            # Save zip file
            with open(zip_path, 'wb') as f:
                f.write(response.content)
            
            # Extract font file
            print(f"Extracting {font_name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Create temporary directory for extraction
                temp_dir = fonts_dir / 'temp'
                temp_dir.mkdir(exist_ok=True)
                zip_ref.extractall(temp_dir)
                
                # Find and move the target font file
                found = False
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.ttf') and ('Regular' in file or 'regular' in file.lower()):
                            src = Path(root) / file
                            dst = fonts_dir / font_info['target_file']
                            shutil.copy2(src, dst)
                            found = True
                            print(f"Installed {font_name}")
                            break
                    if found:
                        break
                        
                # Clean up
                shutil.rmtree(temp_dir)
                zip_path.unlink()
                
        except Exception as e:
            print(f"Error processing {font_name}: {str(e)}")
            continue
            
    print("\nFont setup complete!")
    
if __name__ == "__main__":
    setup_fonts()