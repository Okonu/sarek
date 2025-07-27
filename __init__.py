#!/usr/bin/env python3
"""
Sarek - Advanced Terminal AI Assistant

A comprehensive AI assistant with code analysis, git integration,
voice commands, and system monitoring capabilities.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core.config import ConfigManager
from .core.database import EnhancedMemoryDB
from .core.ai_interface import AIInterface
from .core.data_models import Conversation, CodeAnalysis, Achievement

__all__ = [
    "ConfigManager",
    "EnhancedMemoryDB",
    "AIInterface",
    "Conversation",
    "CodeAnalysis",
    "Achievement"
]