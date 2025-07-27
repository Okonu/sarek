#!/usr/bin/env python3
"""
Constants and configuration values for Sarek
"""

from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
DEFAULT_MODEL = "mistral"
DB_PATH = Path.home() / ".sarek.db"
CONFIG_PATH = Path.home() / ".sarek_config.json"

SAREK_LOGO = """
[bold cyan]
╔═══════════════════════════════════════════════════════════╗
║  ███████  █████  ██████  ███████ ██   ██                 ║
║  ██      ██   ██ ██   ██ ██      ██  ██                  ║
║  ███████ ███████ ██████  █████   █████                   ║
║       ██ ██   ██ ██   ██ ██      ██  ██                  ║
║  ███████ ██   ██ ██   ██ ███████ ██   ██                 ║
║                                                           ║
║           Advanced Terminal AI Assistant                  ║
║        "Logic is the beginning of wisdom"                 ║
╚═══════════════════════════════════════════════════════════╝
[/bold cyan]
"""

THEMES = {
    'vulcan': {
        'primary': 'blue',
        'secondary': 'cyan',
        'accent': 'green',
        'warning': 'yellow',
        'error': 'red'
    },
    'matrix': {
        'primary': 'green',
        'secondary': 'bright_green',
        'accent': 'white',
        'warning': 'yellow',
        'error': 'red'
    },
    'cyberpunk': {
        'primary': 'magenta',
        'secondary': 'bright_magenta',
        'accent': 'cyan',
        'warning': 'yellow',
        'error': 'red'
    }
}

SMART_ALIASES = {
    'wtf': 'explain-code',
    'fix': 'debug-suggestions',
    'perf': 'performance-analysis',
    'sec': 'security-audit',
    'deploy': 'deployment-check',
    'test': 'generate-tests',
    'doc': 'generate-docs',
    'review': 'code-review',
    'refactor': 'refactoring-suggestions',
    'bench': 'benchmark-analysis',
    'health': 'system-health',
    'optimize': 'optimization-suggestions'
}

MODEL_ROUTING = {
    'code_analysis': 'codellama',
    'general_chat': 'mistral',
    'creative_writing': 'llama2',
    'technical_docs': 'mistral',
    'math_problems': 'mistral',
    'debugging': 'codellama'
}

SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.php': 'php',
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.sh': 'bash',
    '.sql': 'sql'
}