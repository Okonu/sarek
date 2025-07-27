#!/usr/bin/env python3
"""
Database management for Sarek AI Assistant
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from rich.console import Console

from .data_models import Conversation, Achievement
from ..constants import DB_PATH

console = Console()


class EnhancedMemoryDB:
    """Enhanced database with achievements and learning concepts"""

    def __init__(self):
        self.init_db()
        self.migrate_if_needed()

    def init_db(self) -> None:
        """Initialize SQLite database with all required tables"""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_name TEXT NOT NULL DEFAULT 'default',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_input TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    context_used TEXT DEFAULT '',
                    model_used TEXT DEFAULT 'mistral'
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS code_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_hash TEXT NOT NULL,
                    language TEXT,
                    lines_of_code INTEGER,
                    complexity_score REAL,
                    analysis_data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    name TEXT PRIMARY KEY,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                    description TEXT,
                    mood TEXT DEFAULT 'neutral'
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    unlocked BOOLEAN DEFAULT FALSE,
                    progress INTEGER DEFAULT 0,
                    target INTEGER DEFAULT 100,
                    unlocked_at DATETIME
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_concepts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    concept TEXT UNIQUE NOT NULL,
                    explanation TEXT NOT NULL,
                    difficulty INTEGER DEFAULT 1,
                    last_reviewed DATETIME DEFAULT CURRENT_TIMESTAMP,
                    review_count INTEGER DEFAULT 0,
                    mastery_level INTEGER DEFAULT 0,
                    tags TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS git_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_path TEXT NOT NULL,
                    commit_hash TEXT,
                    action TEXT,
                    description TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def migrate_if_needed(self) -> None:
        """Handle database migrations for schema changes"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("PRAGMA table_info(conversations)")
            columns = [row[1] for row in cursor.fetchall()]

            if 'model_used' not in columns:
                conn.execute("ALTER TABLE conversations ADD COLUMN model_used TEXT DEFAULT 'mistral'")

    def save_conversation(self, session_name: str, user_input: str, ai_response: str,
                          context: str = "", model: str = "mistral") -> None:
        """Save conversation and update achievements"""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO conversations (session_name, user_input, ai_response, context_used, model_used)
                VALUES (?, ?, ?, ?, ?)
            """, (session_name, user_input, ai_response, context, model))

            conn.execute("""
                INSERT OR REPLACE INTO sessions (name, last_used)
                VALUES (?, CURRENT_TIMESTAMP)
            """, (session_name,))

        self.update_achievements('conversation')

    def update_achievements(self, action_type: str) -> None:
        """Update achievement progress based on action type"""
        achievements_to_check = {
            'conversation': [('chat_master', 100), ('session_expert', 10)],
            'code_analysis': [('code_analyzer', 50), ('quality_guru', 25)],
            'git_usage': [('git_ninja', 25), ('commit_master', 50)],
            'learning': [('knowledge_seeker', 20), ('concept_master', 100)]
        }

        if action_type in achievements_to_check:
            for achievement_name, target in achievements_to_check[action_type]:
                self.increment_achievement(achievement_name, target)

    def increment_achievement(self, name: str, target: int) -> None:
        """Increment achievement progress and check for unlock"""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO achievements (name, target, description)
                VALUES (?, ?, ?)
            """, (name, target, f"Achievement: {name}"))

            conn.execute("""
                UPDATE achievements
                SET progress = progress + 1
                WHERE name = ? AND unlocked = FALSE
            """, (name,))

            cursor = conn.execute("""
                SELECT progress FROM achievements
                WHERE name = ? AND progress >= target AND unlocked = FALSE
            """, (name,))

            if cursor.fetchone():
                conn.execute("""
                    UPDATE achievements
                    SET unlocked = TRUE, unlocked_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (name,))

                console.print(f"🏆 [bold yellow]Achievement Unlocked: {name}![/bold yellow]")

    def get_recent_context(self, session_name: str, limit: int = 3) -> List[Conversation]:
        """Get recent conversations for context"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                SELECT id, session_name, timestamp, user_input, ai_response, context_used, model_used
                FROM conversations
                WHERE session_name = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (session_name, limit))

            conversations = []
            for row in cursor.fetchall():
                conversations.append(Conversation(
                    id=row[0],
                    session_name=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_input=row[3],
                    ai_response=row[4],
                    context_used=row[5],
                    model_used=row[6] if row[6] else "mistral"
                ))
            return list(reversed(conversations))

    def search_conversations(self, query: str, session_name: Optional[str] = None) -> List[Conversation]:
        """Search conversation history"""
        base_query = """
            SELECT id, session_name, timestamp, user_input, ai_response, context_used, model_used
            FROM conversations
            WHERE (user_input LIKE ? OR ai_response LIKE ?)
        """
        params = [f"%{query}%", f"%{query}%"]

        if session_name:
            base_query += " AND session_name = ?"
            params.append(session_name)

        base_query += " ORDER BY timestamp DESC LIMIT 20"

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(base_query, params)
            conversations = []
            for row in cursor.fetchall():
                conversations.append(Conversation(
                    id=row[0],
                    session_name=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_input=row[3],
                    ai_response=row[4],
                    context_used=row[5],
                    model_used=row[6] if row[6] else "mistral"
                ))
            return conversations

    def get_achievements(self) -> List[Achievement]:
        """Get all achievements"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                SELECT name, description, unlocked, progress, target
                FROM achievements
                ORDER BY unlocked DESC, progress DESC
            """)

            achievements = []
            for row in cursor.fetchall():
                achievements.append(Achievement(
                    name=row[0],
                    description=row[1],
                    unlocked=bool(row[2]),
                    progress=row[3],
                    target=row[4]
                ))
            return achievements

    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get all conversation sessions"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                SELECT s.name, s.created_at, s.last_used, s.description,
                       COUNT(c.id) as message_count
                FROM sessions s
                LEFT JOIN conversations c ON s.name = c.session_name
                GROUP BY s.name, s.created_at, s.last_used, s.description
                ORDER BY s.last_used DESC
            """)

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'name': row[0],
                    'created_at': row[1],
                    'last_used': row[2],
                    'description': row[3],
                    'message_count': row[4]
                })
            return sessions

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics from database"""
        with sqlite3.connect(DB_PATH) as conn:

            cursor = conn.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM code_analysis")
            total_analyses = cursor.fetchone()[0]

            db_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0

            return {
                'conversations': total_conversations,
                'sessions': total_sessions,
                'code_analyses': total_analyses,
                'database_size_mb': db_size / (1024 * 1024)
            }