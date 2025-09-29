import json
import os

DEFAULT_CONFIG = {
    "voice": {
        "rate": 180,
        "volume": 0.9,
        "wake_word": "jarvis"
    },
    "system": {
        "startup_sound": True,
        "gui_animations": True,
        "fullscreen": True
    },
    "api_keys": {
        "openai": "",
        "wolfram": "",
        "weather": ""
    }
}

def load_config():
    """Load configuration from config.json or create default if not exists"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    if not os.path.exists(config_path):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
        
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"Error loading config: {str(e)}")
        return DEFAULT_CONFIG
        
def save_config(config):
    """Save configuration to config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {str(e)}")
        
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