# Sarek - Advanced Terminal AI Assistant

🖖 *"Logic is the beginning of wisdom"*

Sarek is a comprehensive terminal-based AI assistant named after Spock's father, featuring code analysis, git integration, voice commands, system monitoring, and achievement tracking.

## ✨ Features

### 🤖 AI Integration
- Multiple AI model support (Mistral, CodeLlama, Llama2)
- Intelligent model auto-selection based on task type
- Conversation context and memory
- Session management

### 🔍 Code Analysis
- Advanced static code analysis for multiple languages
- Security vulnerability detection
- Code complexity metrics
- Quality issue identification
- Project-wide analysis with progress tracking

### 🔧 Git Integration
- Enhanced git status with insights
- AI-powered commit message generation
- Commit explanation and analysis
- Repository health assessment

### 🎤 Voice Interface
- Speech-to-text input
- Text-to-speech output
- Voice command mode
- Audio device management

### 📊 System Monitoring
- Real-time system metrics (CPU, Memory, Disk)
- Health assessments and recommendations
- Process monitoring
- Performance optimization suggestions

### 🏆 Achievement System
- Progress tracking and gamification
- Learning milestone recognition
- Activity-based rewards

### 🎨 Rich Terminal UI
- Live updating dashboard
- Interactive command palette
- Beautiful code analysis trees
- Color themes (Vulcan, Matrix, Cyberpunk)

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Ubuntu/Debian-based Linux system
- Ollama (for AI functionality)

### Quick System-wide Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sarek.git
cd sarek

# Install system dependencies (no pip/virtual environments needed!)
chmod +x install_deps.sh
./install_deps.sh

# Install Sarek globally (available system-wide)
chmod +x setup_global.sh
sudo ./setup_global.sh
```

### Alternative: User-only Installation

```bash
# If you prefer user-only installation (no sudo required)
chmod +x make_global_simple.sh
./make_global_simple.sh
source ~/.bashrc
```

### Manual Dependency Installation

```bash
# Core dependencies (required)
sudo apt update
sudo apt install python3-requests python3-rich python3-git python3-psutil python3-full

# Audio support for voice features (optional)
sudo apt install portaudio19-dev espeak espeak-data

# Note: Some voice packages may need pip installation
# pip install --user SpeechRecognition pyttsx3  # if needed
```

## 🛠️ Setup

### 1. Install Ollama (Required for AI functionality)
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull AI models (in a new terminal)
ollama pull mistral
ollama pull codellama
ollama pull llama2
```

### 2. Verify Installation
```bash
# Test that Sarek is working
sarek help

# Test AI functionality (requires Ollama to be running)
sarek "Hello, can you help me with coding?"
```

### 3. Optional: Voice Features
```bash
# If you want voice features, install additional packages
pip install --user SpeechRecognition pyttsx3

# Test voice functionality
sarek voice
```

## 📖 Usage

### Command Format Rules

**🔑 Important**: Sarek uses different command formats:

- **Hyphens for specific commands**: `git-status`, `health-check`, `analyze-dir`
- **Spaces for AI queries**: `"explain Python"`, `"help me debug"`

```bash
# ✅ Correct - Specific commands use hyphens
sarek git-status
sarek health-check

# ✅ Correct - AI queries use natural language
sarek "explain git workflows"
sarek "help me optimize this code"
```

### Basic Commands

```bash
# Interactive mode with command palette
sarek

# Ask a direct question
sarek "How do I optimize this Python code?"

# Show help
sarek help

# Show comprehensive command reference
sarek commands

# Use specific AI model
sarek --model codellama "Explain this function"
```

### Code Analysis

```bash
# Analyze a single file
sarek analyze file.py

# Analyze entire directory
sarek analyze-dir ./src

# Get AI explanation of code
sarek explain-code script.py

# Project summary
sarek project-summary
```

### Git Integration

```bash
# Enhanced git status (note the hyphen!)
sarek git-status

# AI-generated commit message
sarek git-commit-msg

# Explain a commit
sarek git-explain abc1234

# Review current changes
sarek git-review
```

### Session Management

```bash
# Use named session
sarek --session work "What's the latest in AI?"

# List all sessions
sarek sessions

# Search conversation history
sarek search "machine learning"

# View memory statistics
sarek memory
```

### Voice Commands

```bash
# Enable voice mode
sarek --voice

# Start voice command mode
sarek voice
```

### System Monitoring

```bash
# System health check
sarek health-check

# Live dashboard
sarek dashboard --live

# View achievements
sarek achievements
```

### Smart Aliases

Sarek includes convenient aliases for common tasks:

- `sarek wtf file.py` → `sarek explain-code file.py`
- `sarek fix` → `sarek debug-suggestions`  
- `sarek sec` → `sarek security-audit`
- `sarek perf` → `sarek performance-analysis`
- `sarek health` → `sarek health-check`

**Note**: All aliases use hyphens in their expanded form.

## 🎨 Configuration

Sarek stores configuration in `~/.sarek_config.json`:

```json
{
  "theme": "vulcan",
  "default_model": "mistral",
  "voice_enabled": false,
  "startup_animation": true,
  "context_limit": 3,
  "auto_git_integration": true,
  "achievements_enabled": true,
  "system_monitoring": true
}
```

### Available Themes
- `vulcan` - Blue and cyan (default)
- `matrix` - Green matrix style
- `cyberpunk` - Magenta and cyan

## 🏗️ Project Structure

```
sarek/
├── __init__.py
├── main.py                 # Main entry point
├── constants.py            # Configuration constants
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # SQLite database
│   ├── ai_interface.py    # AI model interface
│   └── data_models.py     # Data structures
├── features/              # Feature modules
│   ├── __init__.py
│   ├── code_analyzer.py   # Code analysis
│   ├── git_integration.py # Git functionality
│   ├── voice_interface.py # Voice commands
│   └── system_monitor.py  # System monitoring
└── ui/                    # User interface
    ├── __init__.py
    ├── dashboard.py       # Dashboard displays
    └── commands.py        # Command interface
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone and setup for development
git clone https://github.com/yourusername/sarek.git
cd sarek

# Install dependencies
./install_deps.sh

# Install development tools (optional)
pip install --user pytest black flake8 mypy

# Run tests (if available)
pytest

# Format code
black sarek/

# Lint code  
flake8 sarek/

# Type checking
mypy sarek/

# Test your changes
python3 run_sarek.py help
```

### Project Structure for Contributors

```
sarek/
├── install_deps.sh         # System dependency installer
├── setup_global.sh         # Global installation script  
├── make_global_simple.sh   # User installation script
├── run_sarek.py           # Standalone runner
├── sarek/                 # Main package
│   ├── main.py           # Entry point
│   ├── constants.py      # Configuration
│   ├── core/            # Core functionality
│   ├── features/        # Feature modules  
│   └── ui/              # User interface
└── README.md            # This file
```

## 🐛 Troubleshooting

### Common Issues

**"sarek: command not found"**
```bash
# If using system-wide installation, try:
sudo ./setup_global.sh

# Verify installation:
which sarek
ls -la /usr/local/bin/sarek
```

**Ollama Connection Error**
```bash
# Make sure Ollama is running
ollama serve

# Check if models are available
ollama list

# Test Ollama directly
curl http://localhost:11434/api/tags
```

**Voice Recognition Not Working**
```bash
# Install audio dependencies
sudo apt install portaudio19-dev espeak espeak-data

# Install Python voice packages
pip install --user SpeechRecognition pyttsx3

# Test microphone access
python3 -c "import speech_recognition as sr; print('Voice support available')"
```

**Git Integration Issues**
```bash
# Make sure you're in a git repository
git init

# Verify git integration
sarek git status
```

**Permission Errors**
```bash
# For system-wide installation
sudo chown -R root:root /opt/sarek
sudo chmod +x /usr/local/bin/sarek

# Check database permissions
ls -la ~/.sarek*
```

**Missing Dependencies**
```bash
# Re-run the dependency installer
./install_deps.sh

# Check what's installed
python3 -c "import requests, rich, git, psutil; print('Core dependencies OK')"
```

## 🔒 Privacy & Data

- **Fully Local**: All data stored locally in `~/.sarek.db` 
- **No Cloud Dependencies**: Uses system packages, no pip/virtual environments
- **Offline Capable**: Can run completely offline with local Ollama models
- **Optional External Services**:
  - Ollama API (local by default)
  - Google Speech API (only if using voice recognition)
- **No Telemetry**: Zero data collection or tracking

## 📊 Installation Locations

**System-wide Installation (Method 2):**
- **Program**: `/opt/sarek/`
- **Command**: `/usr/local/bin/sarek`
- **Database**: `~/.sarek.db` (per user)
- **Config**: `~/.sarek_config.json` (per user)

**User-only Installation (Alternative):**
- **Program**: `~/code/sarek/` (wherever you cloned it)
- **Command**: `~/.local/bin/sarek`
- **Database**: `~/.sarek.db`
- **Config**: `~/.sarek_config.json`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Named after Sarek of Vulcan from Star Trek
- Built with [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- Powered by [Ollama](https://ollama.ai) for local AI inference
- Inspired by the logical precision of Vulcan philosophy

## 🖖 Live Long and Prosper

*"The needs of the many outweigh the needs of the few."*

---

**Star Trek Reference**: Sarek was Spock's father, a Vulcan ambassador known for his logical thinking and diplomatic skills. This AI assistant embodies those same principles of logic, precision, and helpfulness.