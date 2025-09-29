import json
import os

def load_config():
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    if not os.path.exists(config_path):
        return create_default_config(config_path)
        
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return create_default_config(config_path)
        
def create_default_config(config_path):
    """Create and return default configuration"""
    default_config = {
        'voice': {
            'rate': 180,
            'volume': 0.9,
            'wake_word': 'jarvis'
        },
        'gui': {
            'fullscreen': True,
            'animations': True,
            'theme': 'blue'
        },
        'system': {
            'startup_sound': True,
            'monitoring_interval': 1.0,
            'face_recognition': True
        },
        'api_keys': {
            'openai': '',
            'wolfram': '',
            'weather': ''
        }
    }
    
    try:
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=4)
    except Exception as e:
        print(f"Error creating config: {str(e)}")
        
    return default_config
    
def save_config(config):
    """Save configuration to config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        return False
        
def update_config(key, value):
    """Update a specific configuration value"""
    config = load_config()
    
    # Handle nested keys (e.g., 'voice.rate')
    keys = key.split('.')
    current = config
    
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
        
    current[keys[-1]] = value
    save_config(config)
    return True