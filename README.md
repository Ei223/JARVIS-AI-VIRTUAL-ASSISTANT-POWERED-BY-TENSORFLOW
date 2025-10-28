# Advanced J.A.R.V.I.S AI Assistant

An advanced AI assistant inspired by Iron Man's JARVIS, featuring a futuristic GUI interface, voice commands, and multiple advanced capabilities.

## Features

- 🎯 Futuristic GUI with holographic displays
- 🗣️ Advanced voice recognition and natural language processing
- 🖥️ Real-time system monitoring
- 👤 Facial recognition
- 🌐 Web search and information retrieval
- 📊 Data analysis and visualization
- 🤖 AI-powered conversations
- 🎨 Beautiful startup animation
- 📱 System control and automation

## Requirements

- Python 3.8 or higher
- Windows/Linux/MacOS
- Webcam (for facial recognition)
- Microphone (for voice commands)
- GPU recommended for better performance

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Ei223/jarvis.git
cd jarvis
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Configure the application:
- Copy `config.json.example` to `config.json`
- Add your API keys for OpenAI, Wolfram Alpha, etc.

## Usage

1. Start JARVIS:
```bash
python main.py
```

2. Wake word: "Jarvis"

3. Example commands:
- "Jarvis, system status"
- "Jarvis, search [query]"
- "Jarvis, tell me about [topic]"
- "Jarvis, recognize face"
- "Jarvis, what's the weather"

## Advanced Features

1. **System Monitoring**
   - CPU/GPU usage
   - Memory utilization
   - Temperature monitoring
   - Process management
   - Tells the Battery Level

2. **Voice Interaction**
   - Natural language processing
   - Context-aware conversations
   - Multiple voice options
   - Custom wake word support

3. **Visual Interface**
   - Holographic displays
   - Real-time animations
   - System status visualization
   - Data processing views

4. **AI Capabilities**
   - Face recognition
   - Object detection
   - Natural language processing
   - Contextual responses

## Customization

1. Edit `config.json` to modify:
   - Voice settings
   - GUI preferences
   - API configurations
   - System parameters

2. Add custom commands in `core/jarvis_core.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by Iron Man's JARVIS
- Built with Python and PyQt6

- Uses various open-source libraries
