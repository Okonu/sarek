# 🖖 Sarek: Advanced Terminal AI Assistant

> *"Logic is the beginning of wisdom, not the end."* - Spock

Sarek is a powerful, terminal-based AI assistant that combines the intelligence of local LLMs with advanced code analysis, persistent memory, and a beautiful visual interface. Named after Spock's father, Sarek brings Vulcan-like logic and precision to your development workflow.

## ✨ Features

### 🧠 **Intelligent Memory System**
- **SQLite Database**: Persistent conversation history with full-text search
- **Session Management**: Organize conversations by project, topic, or context
- **Smart Context**: Automatically includes relevant previous conversations
- **Memory Search**: Find any past discussion instantly
- **Data Migration**: Seamlessly upgrades from legacy pickle storage

### 🔍 **Advanced Code Analysis Engine**
- **Multi-Language Support**: Python, JavaScript, TypeScript, PHP, Java, C++, Go, Rust, Ruby, Bash, SQL
- **Deep Python Analysis**: AST parsing for functions, classes, imports, and complexity metrics
- **Smart Caching**: File hash-based caching prevents redundant analysis
- **Quality Assessment**: Automatically detects code smells, complexity issues, and improvements
- **Project Overview**: Comprehensive analysis of entire codebases
- **AI Code Explanation**: Get intelligent explanations of complex code

### 🎨 **Rich Visual Interface**
- **Interactive Dashboard**: Project overview with live statistics
- **Beautiful Terminal Output**: Tables, trees, panels, and syntax highlighting
- **Visual Code Analysis**: Tree-structured display of code metrics and relationships
- **Progress Indicators**: Visual feedback for long-running operations
- **Color-Coded Issues**: Immediate visual feedback on code quality

### 🤖 **AI-Powered Features**
- **Local LLM Integration**: Uses Ollama + Mistral for privacy and speed
- **Context-Aware Responses**: Remembers your conversation history
- **Code Understanding**: Explains complex algorithms and design patterns
- **Shell Command Help**: Explains Linux commands with TLDR and man pages
- **Document Analysis**: Reads and summarizes text files, markdown, and more

### 🛠 **Developer Tools**
- **File Reading**: Analyze and discuss any text-based file
- **Shell Integration**: Explain commands, generate scripts
- **Git Awareness**: Understand project structure and version control
- **Project Analysis**: Get insights into codebase health and structure
- **Issue Detection**: Identify potential problems before they become bugs

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Ollama with Mistral model
- Ubuntu/Debian system (or similar package manager)

### Quick Setup
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-rich python3-requests python3-textual

# Clone or download Sarek
git clone <your-repo> ~/code/sarek
cd ~/code/sarek

# Set up Ollama and Mistral (if not already done)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral

# Make Sarek globally available
chmod +x sarek.py
sudo ln -sf ~/code/sarek/sarek.py /usr/local/bin/sarek

# Test installation
sarek help
```

### Alternative Installation (pip)
```bash
# If system packages aren't available
pip install rich requests textual --break-system-packages
```

## 📖 Usage

### Basic Commands
```bash
# Interactive mode
sarek

# Ask a direct question
sarek "explain quantum computing"

# Get help
sarek help

# Use named conversation session
sarek --session physics "what is entropy?"
```

### Memory & Session Management
```bash
# List all conversation sessions
sarek sessions

# Search conversation history
sarek search "docker containers"

# Show memory statistics
sarek memory

# Use specific session
sarek --session work
```

### Code Analysis
```bash
# Analyze a single file
sarek analyze mycode.py

# Analyze entire directory
sarek analyze-dir ./src

# Get AI explanation of code
sarek explain-code complex_algorithm.py

# Project overview
sarek project-summary
```

### Document Processing
```bash
# Read and analyze files
sarek read documentation.md

# Explain shell commands
sarek explain "rsync -avzP"

# Pipe content for analysis
cat logfile.txt | sarek "summarize these errors"
```

### Visual Interface
```bash
# Launch interactive dashboard
sarek ui

# Project overview dashboard
sarek dashboard
```

## 🎯 Examples

### Conversation with Memory
```bash
$ sarek --session learning "what is a binary tree?"
🤖 A binary tree is a hierarchical data structure...

$ sarek --session learning "how do you traverse it?"
🤖 Based on our previous discussion about binary trees, there are three main traversal methods...
```

### Code Analysis
```bash
$ sarek analyze app.py
📄 app.py
├── 📊 Code Metrics
│   ├── Language: python
│   ├── Lines of Code: 245
│   └── Complexity Score: 3.2
├── 🔧 Functions (8)
│   ├── main()
│   ├── process_data()
│   └── ...
└── ⚠️ Issues
    └── 🟡 File is quite large - consider refactoring
```

### Memory Search
```bash
$ sarek search "kubernetes deployment"
🔍 Found 3 matching conversations:
📅 devops | 2024-01-15 14:30
User: How do I debug a failing kubernetes deployment?
AI: To debug a failing Kubernetes deployment, start by checking...
```

## 🔧 Configuration

### Database Location
Sarek stores its data in `~/.sarek.db` (SQLite database)

### Ollama Configuration
Make sure Ollama is running:
```bash
ollama serve  # Start Ollama server
ollama list   # Check available models
```

### Model Switching
Currently optimized for Mistral, but extensible to other Ollama models.

## 🎨 Advanced Features

### Session-Based Workflows
```bash
# Work session for development questions
sarek --session work

# Research session for learning
sarek --session research

# Debug session for troubleshooting
sarek --session debug
```

### Project Analysis Workflow
```bash
# Get project overview
sarek project-summary

# Analyze specific components
sarek analyze-dir ./backend
sarek analyze-dir ./frontend

# Get AI insights
sarek explain-code ./core/algorithm.py
```

### Memory Management
```bash
# View conversation statistics
sarek memory

# Search across all sessions
sarek search "error handling"

# Session-specific search
sarek --session work search "database"
```

## 🛠 Development

### Architecture
- **Memory Layer**: SQLite database with conversation, session, and analysis tables
- **Analysis Engine**: AST-based code analysis with caching
- **AI Interface**: Ollama REST API integration with context management
- **UI Layer**: Rich terminal output with optional Textual interactive mode

### Code Structure
```
sarek.py
├── Data Models (Conversation, CodeAnalysis)
├── Database Layer (EnhancedMemoryDB)
├── Analysis Engine (CodeAnalyzer)
├── AI Interface (ask_mistral, context building)
├── Visual Components (Rich formatting, Textual UI)
└── CLI Interface (argument parsing, command routing)
```

### Adding New Languages
The code analyzer is easily extensible. To add support for a new language:

1. Add the file extension to `supported_extensions`
2. Implement language-specific parsing logic
3. Add pattern matching for functions/classes/imports

## 🔍 Troubleshooting

### Common Issues

**Ollama Connection Error**
```bash
# Make sure Ollama is running
ollama serve

# Check if Mistral is available
ollama list
ollama pull mistral  # if not available
```

**Import Errors**
```bash
# Install missing dependencies
sudo apt install python3-rich python3-requests python3-textual
```

**Permission Denied**
```bash
# Make sure sarek.py is executable
chmod +x sarek.py
```

**Database Issues**
```bash
# Reset database (will lose conversation history)
rm ~/.sarek.db
```

## 🚀 Roadmap

### Planned Features
- [ ] **Multi-Model Support**: Switch between different Ollama models
- [ ] **Git Integration**: Analyze commits, suggest commit messages
- [ ] **Log Analysis**: Smart parsing of application logs
- [ ] **Voice Integration**: Speech input/output
- [ ] **Plugin System**: Extensible command system
- [ ] **Web Interface**: Browser-based dashboard
- [ ] **Collaborative Features**: Share insights and knowledge
- [ ] **Fine-tuning**: Personal model adaptation

### Contribution Areas
- Language support for code analysis
- Visual interface improvements
- Performance optimizations
- Documentation and examples
- Testing and quality assurance

## 📜 License

MIT License - Feel free to modify and distribute

## 🖖 Philosophy

Sarek embodies the Vulcan principles of logic, knowledge, and continuous learning. It's designed to be:

- **Logical**: Structured approach to information and analysis
- **Persistent**: Never forgets your conversations and insights
- **Extensible**: Grows with your needs and workflows
- **Private**: All processing happens locally on your machine
- **Efficient**: Fast, cached operations with intelligent context

## 🎯 Support

For issues, feature requests, or contributions:
- Create GitHub issues for bugs
- Submit pull requests for improvements
- Share your workflows and use cases
- Help improve documentation

---

*"The needs of the many outweigh the needs of the few."* - Use Sarek to multiply your development effectiveness and share knowledge with your team.

## Quick Reference

### Essential Commands
| Command | Purpose |
|---------|---------|
| `sarek help` | Show complete help |
| `sarek ui` | Launch visual interface |
| `sarek sessions` | List conversation sessions |
| `sarek analyze file.py` | Analyze code file |
| `sarek search "query"` | Search conversation history |
| `sarek memory` | Show database statistics |
| `sarek project-summary` | Analyze entire project |

### Pro Tips
- Use `--session <name>` for organized conversations
- Pipe file contents: `cat file.txt \| sarek "explain this"`
- Search across sessions: `sarek search "specific topic"`
- Use `sarek explain-code` for AI code explanations
- Regular `sarek memory` checks show your learning progress