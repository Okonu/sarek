#!/usr/bin/env python3
"""
Data models for Sarek AI Assistant
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Conversation:
    """Represents a conversation between user and AI"""
    id: int
    session_name: str
    timestamp: datetime
    user_input: str
    ai_response: str
    context_used: str = ""
    model_used: str = "mistral"


@dataclass
class CodeAnalysis:
    """Represents the result of code analysis"""
    file_path: str
    language: str
    lines_of_code: int
    complexity_score: float
    functions: List[str]
    classes: List[str]
    imports: List[str]
    issues: List[str]
    security_issues: Optional[List[str]] = None


@dataclass
class Achievement:
    """Represents a user achievement/badge"""
    name: str
    description: str
    unlocked: bool = False
    progress: int = 0
    target: int = 100


@dataclass
class GitCommit:
    """Represents a git commit"""
    hash: str
    message: str
    author: str
    date: datetime
    files_changed: int


@dataclass
class SystemMetrics:
    """Represents system performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    processes: int
    boot_time: str