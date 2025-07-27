#!/usr/bin/env python3

import sys
import os
import fileinput
import requests
import pickle
import subprocess
import sqlite3
import json
import ast
import hashlib
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.tree import Tree
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.text import Text
from rich.columns import Columns
from rich.progress import track

console = Console()
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"
MEMORY_FILE = Path.home() / ".sarek_memory.pkl"  # Keep for backward compatibility
DB_PATH = Path.home() / ".sarek.db"


# ===================== Data Models =====================
@dataclass
class Conversation:
    id: int
    session_name: str
    timestamp: datetime
    user_input: str
    ai_response: str
    context_used: str = ""


@dataclass
class CodeAnalysis:
    file_path: str
    language: str
    lines_of_code: int
    complexity_score: float
    functions: List[str]
    classes: List[str]
    imports: List[str]
    issues: List[str]


# ===================== Enhanced Database Memory System =====================
class EnhancedMemoryDB:
    def __init__(self):
        self.init_db()
        self.migrate_pickle_data()

    def init_db(self):
        """Initialize SQLite database with required tables"""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                         CREATE TABLE IF NOT EXISTS conversations
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             session_name
                             TEXT
                             NOT
                             NULL
                             DEFAULT
                             'default',
                             timestamp
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             user_input
                             TEXT
                             NOT
                             NULL,
                             ai_response
                             TEXT
                             NOT
                             NULL,
                             context_used
                             TEXT
                             DEFAULT
                             ''
                         )
                         """)

            conn.execute("""
                         CREATE TABLE IF NOT EXISTS code_analysis
                         (
                             id
                             INTEGER
                             PRIMARY
                             KEY
                             AUTOINCREMENT,
                             file_path
                             TEXT
                             UNIQUE
                             NOT
                             NULL,
                             file_hash
                             TEXT
                             NOT
                             NULL,
                             language
                             TEXT,
                             lines_of_code
                             INTEGER,
                             complexity_score
                             REAL,
                             analysis_data
                             TEXT,
                             timestamp
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP
                         )
                         """)

            conn.execute("""
                         CREATE TABLE IF NOT EXISTS sessions
                         (
                             name
                             TEXT
                             PRIMARY
                             KEY,
                             created_at
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             last_used
                             DATETIME
                             DEFAULT
                             CURRENT_TIMESTAMP,
                             description
                             TEXT
                         )
                         """)

    def migrate_pickle_data(self):
        """Migrate old pickle data to SQLite"""
        if MEMORY_FILE.exists():
            try:
                with open(MEMORY_FILE, "rb") as f:
                    old_memory = pickle.load(f)

                # Convert old format to new format
                for user_input, ai_response in old_memory:
                    self.save_conversation("default", user_input, ai_response, "migrated")

                # Backup and remove old file
                MEMORY_FILE.rename(MEMORY_FILE.with_suffix('.pkl.backup'))
                console.print("[yellow]📦 Migrated old memory data to SQLite database[/yellow]")
            except Exception as e:
                console.print(f"[red]⚠️ Could not migrate old data: {e}[/red]")

    def save_conversation(self, session_name: str, user_input: str, ai_response: str, context: str = ""):
        """Save a conversation to database"""
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                         INSERT INTO conversations (session_name, user_input, ai_response, context_used)
                         VALUES (?, ?, ?, ?)
                         """, (session_name, user_input, ai_response, context))

            # Update session last_used
            conn.execute("""
                INSERT OR REPLACE INTO sessions (name, last_used)
                VALUES (?, CURRENT_TIMESTAMP)
            """, (session_name,))

    def get_recent_context(self, session_name: str, limit: int = 3) -> List[Conversation]:
        """Get recent conversations for context"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                                  SELECT id, session_name, timestamp, user_input, ai_response, context_used
                                  FROM conversations
                                  WHERE session_name = ?
                                  ORDER BY timestamp DESC
                                      LIMIT ?
                                  """, (session_name, limit))

            conversations = []
            for row in cursor.fetchall():
                conversations.append(Conversation(
                    id=row[0],
                    session_name=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    user_input=row[3],
                    ai_response=row[4],
                    context_used=row[5]
                ))
            return list(reversed(conversations))  # Return in chronological order

    def search_conversations(self, query: str, session_name: str = None) -> List[Conversation]:
        """Search through conversation history"""
        base_query = """
                     SELECT id, session_name, timestamp, user_input, ai_response, context_used
                     FROM conversations
                     WHERE (user_input LIKE ? OR ai_response LIKE ?) \
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
                    context_used=row[5]
                ))
            return conversations

    def get_sessions(self) -> List[Dict[str, Any]]:
        """Get all conversation sessions"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                                  SELECT s.name,
                                         s.created_at,
                                         s.last_used,
                                         s.description,
                                         COUNT(c.id) as message_count
                                  FROM sessions s
                                           LEFT JOIN conversations c ON s.name = c.session_name
                                  GROUP BY s.name
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
        """Get memory statistics"""
        with sqlite3.connect(DB_PATH) as conn:
            # Get conversation count
            cursor = conn.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]

            # Get session count
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]

            # Get code analysis count
            cursor = conn.execute("SELECT COUNT(*) FROM code_analysis")
            total_analyses = cursor.fetchone()[0]

            # Get database size
            db_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0

            return {
                'conversations': total_conversations,
                'sessions': total_sessions,
                'code_analyses': total_analyses,
                'database_size_mb': db_size / (1024 * 1024)
            }


# ===================== Advanced Code Analysis Engine =====================
class CodeAnalyzer:
    def __init__(self):
        self.db = EnhancedMemoryDB()
        self.supported_extensions = {
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

    def get_file_hash(self, file_path: str) -> str:
        """Generate hash of file content for caching"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def analyze_python_file(self, file_path: str) -> CodeAnalysis:
        """Analyze a Python file using AST"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return CodeAnalysis(
                file_path=file_path,
                language="python",
                lines_of_code=len(content.splitlines()),
                complexity_score=0.0,
                functions=[],
                classes=[],
                imports=[],
                issues=[f"Syntax Error: {e}"]
            )

        functions = []
        classes = []
        imports = []
        complexity = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                # Calculate complexity: count decision points
                complexity += sum(1 for n in ast.walk(node)
                                  if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With)))

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

            elif isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.extend([f"{module}.{alias.name}" for alias in node.names])

        lines_of_code = len([line for line in content.splitlines()
                             if line.strip() and not line.strip().startswith('#')])
        complexity_score = complexity / max(len(functions), 1)

        # Enhanced code quality checks
        issues = []
        if len(functions) > 25:
            issues.append("🔴 High function count - consider splitting into modules")
        if lines_of_code > 1000:
            issues.append("🟡 Large file - consider refactoring")
        if complexity_score > 8:
            issues.append("🔴 High complexity - simplify conditional logic")
        if len(classes) > 10:
            issues.append("🟡 Many classes - consider design patterns")

        # Check for common patterns
        content_lower = content.lower()
        if 'todo' in content_lower or 'fixme' in content_lower:
            issues.append("📝 Contains TODO/FIXME comments")
        if content.count('except:') > 0:
            issues.append("⚠️ Bare except clauses found - specify exception types")

        return CodeAnalysis(
            file_path=file_path,
            language="python",
            lines_of_code=lines_of_code,
            complexity_score=complexity_score,
            functions=functions,
            classes=classes,
            imports=imports,
            issues=issues
        )

    def analyze_generic_file(self, file_path: str, language: str) -> CodeAnalysis:
        """Basic analysis for non-Python files"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        lines = content.splitlines()
        lines_of_code = len([line for line in lines if line.strip()])

        # Basic pattern matching for different languages
        functions = []
        classes = []
        imports = []
        issues = []

        if language == 'javascript':
            # Simple regex patterns for JS
            import re
            functions = re.findall(r'function\s+(\w+)', content)
            functions.extend(re.findall(r'(\w+)\s*:\s*function', content))
            classes = re.findall(r'class\s+(\w+)', content)
            imports = re.findall(r'import.*from\s+[\'"]([^\'"]+)[\'"]', content)

        elif language == 'php':
            import re
            functions = re.findall(r'function\s+(\w+)', content)
            classes = re.findall(r'class\s+(\w+)', content)

        # Common issues
        if lines_of_code > 500:
            issues.append("🟡 Large file - consider refactoring")
        if content.count('TODO') + content.count('FIXME') > 0:
            issues.append("📝 Contains TODO/FIXME comments")

        return CodeAnalysis(
            file_path=file_path,
            language=language,
            lines_of_code=lines_of_code,
            complexity_score=0.0,
            functions=functions,
            classes=classes,
            imports=imports,
            issues=issues
        )

    def analyze_file(self, file_path: str) -> Optional[CodeAnalysis]:
        """Analyze any supported code file"""
        if not os.path.exists(file_path):
            return None

        file_hash = self.get_file_hash(file_path)

        # Check cache first
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("""
                                  SELECT analysis_data
                                  FROM code_analysis
                                  WHERE file_path = ?
                                    AND file_hash = ?
                                  """, (file_path, file_hash))

            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                return CodeAnalysis(**data)

        # Determine language and analyze
        ext = Path(file_path).suffix.lower()
        language = self.supported_extensions.get(ext, 'unknown')

        if language == 'python':
            analysis = self.analyze_python_file(file_path)
        elif language != 'unknown':
            analysis = self.analyze_generic_file(file_path, language)
        else:
            # Very basic analysis for unknown file types
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            analysis = CodeAnalysis(
                file_path=file_path,
                language="unknown",
                lines_of_code=len(content.splitlines()),
                complexity_score=0.0,
                functions=[],
                classes=[],
                imports=[],
                issues=["❓ Unknown file type - limited analysis available"]
            )

        if analysis:
            # Cache the analysis
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO code_analysis 
                    (file_path, file_hash, language, lines_of_code, complexity_score, analysis_data)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    file_path, file_hash, analysis.language, analysis.lines_of_code,
                    analysis.complexity_score, json.dumps(analysis.__dict__, default=str)
                ))

        return analysis

    def analyze_directory(self, directory_path: str, recursive: bool = True) -> List[CodeAnalysis]:
        """Analyze all code files in a directory"""
        path = Path(directory_path)
        if not path.exists():
            return []

        analyses = []
        pattern = "**/*" if recursive else "*"

        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                analysis = self.analyze_file(str(file_path))
                if analysis:
                    analyses.append(analysis)

        return analyses


# ===================== Enhanced Help Command =====================
def show_help():
    console.print(Panel.fit("""
🧠 [bold cyan]SAREK: Advanced Terminal AI Assistant[/bold cyan]

[bold]Basic Usage:[/bold]
  [green]sarek[/green]                         → Interactive mode
  [green]sarek "prompt"[/green]                → Ask a direct question
  [green]echo '...' | sarek[/green]            → Pipe input
  [green]sarek help[/green]                    → Show this help message

[bold]Document & Shell Commands:[/bold]
  [green]sarek read <file.txt>[/green]         → Read and summarize file content
  [green]sarek explain <shell-cmd>[/green]     → Explain Linux commands via TLDR/man

[bold]Enhanced Memory System:[/bold]
  [green]sarek --session <name>[/green]        → Use named conversation session
  [green]sarek sessions[/green]                → List all conversation sessions
  [green]sarek search "query"[/green]          → Search conversation history
  [green]sarek memory[/green]                  → Show memory statistics

[bold]Code Analysis:[/bold]
  [green]sarek analyze <file.py>[/green]       → Analyze code file (Python, JS, PHP, etc.)
  [green]sarek analyze-dir <path>[/green]      → Analyze all code files in directory
  [green]sarek explain-code <file.py>[/green]  → Get AI explanation of code

[bold]Visual Interface:[/bold]
  [green]sarek ui[/green]                      → Launch interactive terminal UI
  [green]sarek dashboard[/green]               → Show project overview dashboard

[bold]Advanced Features:[/bold]
  [green]sarek project-summary[/green]         → Analyze entire project structure
  [green]sarek --context[/green]               → Show conversation context
  [green]sarek --debug[/green]                 → Enable debug mode

[bold]Features:[/bold]
🧠 Smart Memory: SQLite-based conversation history with search
📊 Code Analysis: Deep analysis of Python, JavaScript, PHP, and more
🎨 Visual Interface: Rich terminal UI with interactive elements
📄 Document Processing: Read and understand various file formats
🤖 Powered by: [italic]Ollama + Mistral (local LLM)[/italic]
    """, title="Sarek Help", border_style="cyan"))


# ===================== Enhanced Memory Functions =====================
def load_memory():
    """Legacy function for backward compatibility"""
    db = EnhancedMemoryDB()
    recent = db.get_recent_context("default", 5)
    return [(conv.user_input, conv.ai_response) for conv in recent]


def save_memory(memory):
    """Legacy function for backward compatibility"""
    # This is now handled by the database
    pass


def build_context_prompt(memory, new_prompt):
    """Enhanced context building using database"""
    db = EnhancedMemoryDB()
    recent_conversations = db.get_recent_context("default", limit=3)

    if not recent_conversations:
        return new_prompt

    context_parts = []
    for conv in recent_conversations:
        context_parts.append(f"User: {conv.user_input}")
        context_parts.append(f"Assistant: {conv.ai_response}")

    context = "\n".join(context_parts)
    return f"Previous conversation:\n{context}\n\nCurrent question:\nUser: {new_prompt}\nAssistant:"


# ===================== Original Functions (Enhanced) =====================
def query_document(filepath):
    if not os.path.exists(filepath):
        return f"❌ File not found: {filepath}"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Enhanced file reading with better formatting
        file_size = len(content)
        line_count = len(content.splitlines())

        preview = content[:2000] if len(content) > 2000 else content

        return f"""📄 [bold]File Analysis: {Path(filepath).name}[/bold]

📊 [bold]Stats:[/bold] {file_size:,} characters, {line_count:,} lines

📝 [bold]Content Preview:[/bold]
{preview}
{"..." if len(content) > 2000 else ""}"""
    except Exception as e:
        return f"❌ Error reading file: {e}"


def explain_shell_command(cmd):
    try:
        out = subprocess.check_output(["tldr", cmd], text=True, timeout=10)
        return f"📚 TLDR for `{cmd}`:\n{out}"
    except subprocess.TimeoutExpired:
        return f"❌ TLDR command timed out for `{cmd}`"
    except Exception:
        try:
            out = subprocess.check_output(["man", cmd], text=True, stderr=subprocess.DEVNULL, timeout=10)
            return f"📖 Manual page snippet for `{cmd}`:\n{out[:1500]}"
        except Exception:
            return f"❌ Could not find TLDR or manual page for `{cmd}`"


def ask_mistral(prompt):
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.Timeout:
        return "❌ Request timed out. Ollama might be processing a large request."
    except requests.exceptions.ConnectionError:
        return "❌ Cannot connect to Ollama. Make sure it's running with `ollama serve`"
    except Exception as e:
        return f"❌ Error querying Ollama: {e}"


def get_input():
    if not sys.stdin.isatty():
        return "".join(fileinput.input()).strip()
    elif len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    else:
        return input("🖖 Enter your prompt: ").strip()


# ===================== New Enhanced Features =====================
def show_sessions():
    """Show all conversation sessions"""
    db = EnhancedMemoryDB()
    sessions = db.get_sessions()

    if not sessions:
        console.print("📂 No conversation sessions found.")
        return

    table = Table(title="🗂️ Conversation Sessions", border_style="cyan")
    table.add_column("Session", style="cyan", min_width=15)
    table.add_column("Created", style="green")
    table.add_column("Last Used", style="yellow")
    table.add_column("Messages", style="magenta", justify="right")

    for session in sessions:
        table.add_row(
            session['name'],
            session['created_at'][:10] if session['created_at'] else "Unknown",
            session['last_used'][:10] if session['last_used'] else "Unknown",
            str(session['message_count'])
        )

    console.print(table)


def search_memory(query: str, session_name: str = None):
    """Search conversation history"""
    db = EnhancedMemoryDB()
    conversations = db.search_conversations(query, session_name)

    if not conversations:
        console.print(f"🔍 No conversations found matching '{query}'")
        return

    console.print(f"🔍 Found {len(conversations)} matching conversations:")

    for conv in conversations:
        # Truncate long responses for readability
        ai_preview = conv.ai_response[:150] + "..." if len(conv.ai_response) > 150 else conv.ai_response
        user_preview = conv.user_input[:100] + "..." if len(conv.user_input) > 100 else conv.user_input

        panel = Panel(
            f"[bold cyan]User:[/bold cyan] {user_preview}\n[bold green]AI:[/bold green] {ai_preview}",
            title=f"📅 {conv.session_name} | {conv.timestamp.strftime('%Y-%m-%d %H:%M')}",
            border_style="blue"
        )
        console.print(panel)


def show_memory_stats():
    """Show memory and database statistics"""
    db = EnhancedMemoryDB()
    stats = db.get_memory_stats()

    table = Table(title="🧠 Memory Statistics", border_style="cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")

    table.add_row("Total Conversations", f"{stats['conversations']:,}")
    table.add_row("Active Sessions", f"{stats['sessions']:,}")
    table.add_row("Code Analyses", f"{stats['code_analyses']:,}")
    table.add_row("Database Size", f"{stats['database_size_mb']:.2f} MB")

    console.print(table)


def analyze_code_file(file_path: str):
    """Analyze a single code file"""
    analyzer = CodeAnalyzer()
    analysis = analyzer.analyze_file(file_path)

    if not analysis:
        console.print(f"❌ Could not analyze {file_path}")
        return

    # Create rich visualization
    tree = Tree(f"📄 {Path(file_path).name}", style="bold cyan")

    # Basic info
    info_branch = tree.add("📊 Code Metrics")
    info_branch.add(f"Language: {analysis.language}")
    info_branch.add(f"Lines of Code: {analysis.lines_of_code:,}")
    info_branch.add(f"Complexity Score: {analysis.complexity_score:.2f}")

    # Functions
    if analysis.functions:
        func_branch = tree.add(f"🔧 Functions ({len(analysis.functions)})")
        for func in analysis.functions[:15]:  # Show first 15
            func_branch.add(func)
        if len(analysis.functions) > 15:
            func_branch.add(f"... and {len(analysis.functions) - 15} more")

    # Classes
    if analysis.classes:
        class_branch = tree.add(f"🏗️ Classes ({len(analysis.classes)})")
        for cls in analysis.classes:
            class_branch.add(cls)

    # Imports
    if analysis.imports:
        import_branch = tree.add(f"📦 Imports ({len(analysis.imports)})")
        for imp in analysis.imports[:10]:  # Show first 10
            import_branch.add(imp)
        if len(analysis.imports) > 10:
            import_branch.add(f"... and {len(analysis.imports) - 10} more")

    # Issues
    if analysis.issues:
        issue_branch = tree.add("⚠️ Issues & Suggestions")
        for issue in analysis.issues:
            issue_branch.add(f"{issue}")

    console.print(tree)


def analyze_directory(dir_path: str):
    """Analyze all code files in a directory"""
    analyzer = CodeAnalyzer()

    console.print(f"🔍 Analyzing directory: {dir_path}")
    analyses = analyzer.analyze_directory(dir_path)

    if not analyses:
        console.print("❌ No code files found in directory")
        return

    # Summary table
    table = Table(title=f"📊 Directory Analysis: {Path(dir_path).name}", border_style="cyan")
    table.add_column("File", style="cyan")
    table.add_column("Language", style="yellow")
    table.add_column("LOC", style="green", justify="right")
    table.add_column("Complexity", style="magenta", justify="right")
    table.add_column("Issues", style="red", justify="right")

    total_loc = 0
    total_files = len(analyses)
    languages = {}

    for analysis in analyses:
        total_loc += analysis.lines_of_code
        languages[analysis.language] = languages.get(analysis.language, 0) + 1

        file_name = Path(analysis.file_path).name
        table.add_row(
            file_name,
            analysis.language,
            f"{analysis.lines_of_code:,}",
            f"{analysis.complexity_score:.1f}",
            str(len(analysis.issues))
        )

    console.print(table)

    # Summary stats
    console.print(f"\n📈 [bold]Summary:[/bold] {total_files} files, {total_loc:,} total lines")
    console.print(f"🏷️ [bold]Languages:[/bold] {', '.join(f'{lang} ({count})' for lang, count in languages.items())}")


def explain_code_with_ai(file_path: str):
    """Use AI to explain code file"""
    if not os.path.exists(file_path):
        console.print(f"❌ File not found: {file_path}")
        return

    # First do code analysis
    analyzer = CodeAnalyzer()
    analysis = analyzer.analyze_file(file_path)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code_content = f.read()

    # Truncate very long files
    if len(code_content) > 3000:
        code_content = code_content[:3000] + "\n... (file truncated for analysis)"

    # Build prompt for AI explanation
    prompt = f"""Please explain this {analysis.language if analysis else 'code'} file:

File: {Path(file_path).name}
{f"Functions: {', '.join(analysis.functions[:5])}" if analysis and analysis.functions else ""}
{f"Classes: {', '.join(analysis.classes)}" if analysis and analysis.classes else ""}

Code:
```{analysis.language if analysis else 'text'}
{code_content}
```

Please provide:
1. A brief overview of what this code does
2. Key functions and their purposes
3. Any potential improvements or issues you notice
4. Overall code quality assessment
"""

    console.print("🤖 Analyzing code with AI...")
    response = ask_mistral(prompt)

    # Save this interaction
    db = EnhancedMemoryDB()
    db.save_conversation("code-analysis", f"explain code: {file_path}", response)

    console.print(Panel(Markdown(response), title=f"🤖 AI Analysis: {Path(file_path).name}", border_style="green"))


def show_project_summary():
    """Show a comprehensive project overview"""
    current_dir = Path.cwd()
    analyzer = CodeAnalyzer()

    console.print(f"🚀 [bold cyan]Project Summary: {current_dir.name}[/bold cyan]")

    # Analyze all code files
    analyses = analyzer.analyze_directory(str(current_dir))

    if not analyses:
        console.print("❌ No code files found in current directory")
        return

    # Calculate metrics
    total_loc = sum(a.lines_of_code for a in analyses)
    total_files = len(analyses)
    languages = {}
    total_functions = 0
    total_classes = 0
    all_issues = []

    for analysis in analyses:
        languages[analysis.language] = languages.get(analysis.language, 0) + 1
        total_functions += len(analysis.functions)
        total_classes += len(analysis.classes)
        all_issues.extend(analysis.issues)

    # Create overview panels
    metrics_panel = Panel(
        f"📊 [bold]Files:[/bold] {total_files}\n"
        f"📏 [bold]Lines of Code:[/bold] {total_loc:,}\n"
        f"🔧 [bold]Functions:[/bold] {total_functions}\n"
        f"🏗️ [bold]Classes:[/bold] {total_classes}\n"
        f"⚠️ [bold]Issues Found:[/bold] {len(all_issues)}",
        title="Project Metrics",
        border_style="cyan"
    )

    languages_text = "\n".join(f"• {lang}: {count} files" for lang, count in languages.items())
    languages_panel = Panel(
        languages_text,
        title="Languages Used",
        border_style="green"
    )

    # Show most complex files
    complex_files = sorted(analyses, key=lambda x: x.complexity_score, reverse=True)[:5]
    complexity_text = "\n".join(
        f"• {Path(a.file_path).name}: {a.complexity_score:.1f}"
        for a in complex_files if a.complexity_score > 0
    )
    complexity_panel = Panel(
        complexity_text if complexity_text else "No complexity data available",
        title="Most Complex Files",
        border_style="yellow"
    )

    # Show issues summary
    issue_types = {}
    for issue in all_issues:
        issue_type = issue.split()[0] if issue else "Other"
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

    issues_text = "\n".join(f"• {issue_type}: {count}" for issue_type, count in issue_types.items())
    issues_panel = Panel(
        issues_text if issues_text else "No issues found! 🎉",
        title="Issue Summary",
        border_style="red" if all_issues else "green"
    )

    # Display in columns
    console.print(Columns([metrics_panel, languages_panel]))
    console.print(Columns([complexity_panel, issues_panel]))


def launch_dashboard():
    """Launch an interactive dashboard view"""
    console.clear()

    # Header
    console.print(Panel.fit(
        "🖖 [bold cyan]SAREK DASHBOARD[/bold cyan]\n"
        "Advanced Terminal AI Assistant",
        border_style="cyan"
    ))

    # Memory stats
    db = EnhancedMemoryDB()
    stats = db.get_memory_stats()

    # Recent sessions
    sessions = db.get_sessions()[:5]  # Last 5 sessions

    # Project info
    current_dir = Path.cwd()
    python_files = list(current_dir.glob("*.py"))

    # Create dashboard layout
    memory_panel = Panel(
        f"💬 Conversations: {stats['conversations']:,}\n"
        f"📂 Sessions: {stats['sessions']:,}\n"
        f"📊 Code Analyses: {stats['code_analyses']:,}\n"
        f"💾 DB Size: {stats['database_size_mb']:.1f} MB",
        title="Memory Stats",
        border_style="blue"
    )

    sessions_text = "\n".join(
        f"• {s['name']} ({s['message_count']} msgs)"
        for s in sessions[:5]
    ) if sessions else "No sessions yet"

    sessions_panel = Panel(
        sessions_text,
        title="Recent Sessions",
        border_style="green"
    )

    project_panel = Panel(
        f"📁 Directory: {current_dir.name}\n"
        f"🐍 Python files: {len(python_files)}\n"
        f"📝 Total files: {len(list(current_dir.iterdir()))}\n"
        f"🔧 Git repo: {'Yes' if (current_dir / '.git').exists() else 'No'}",
        title="Current Project",
        border_style="magenta"
    )

    commands_panel = Panel(
        "🔍 [cyan]sarek analyze .[/cyan] - Analyze project\n"
        "💬 [cyan]sarek --session work[/cyan] - Start work session\n"
        "🔎 [cyan]sarek search 'python'[/cyan] - Search memory\n"
        "📊 [cyan]sarek memory[/cyan] - Memory stats\n"
        "❓ [cyan]sarek help[/cyan] - Full help",
        title="Quick Commands",
        border_style="yellow"
    )

    console.print(Columns([memory_panel, sessions_panel]))
    console.print(Columns([project_panel, commands_panel]))

    console.print("\n🖖 [italic]Ready for your questions![/italic]")


def interactive_mode():
    """Enhanced interactive mode with session support"""
    console.print("🖖 [bold cyan]Welcome to Sarek Interactive Mode![/bold cyan]")
    console.print("Type 'help' for commands, 'ui' for dashboard, 'sessions' to manage sessions, or 'exit' to quit.\n")

    # Determine session
    session_name = "default"
    for i, arg in enumerate(sys.argv):
        if arg == "--session" and i + 1 < len(sys.argv):
            session_name = sys.argv[i + 1]
            break

    db = EnhancedMemoryDB()

    console.print(f"💼 Session: [bold cyan]{session_name}[/bold cyan]")

    # Show recent context if available
    recent = db.get_recent_context(session_name, 2)
    if recent:
        console.print("📚 [dim]Recent context available from previous conversations[/dim]")

    while True:
        try:
            user_input = Prompt.ask(f"\n[bold cyan][{session_name}][/bold cyan] 🖖", default="").strip()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                console.print("👋 [bold]Live long and prosper![/bold]")
                break

            elif user_input.lower() == 'help':
                show_help()

            elif user_input.lower() in ['ui', 'dashboard']:
                if TEXTUAL_AVAILABLE:
                    launch_dashboard()
                else:
                    console.print("❌ [red]Visual UI requires textual package[/red]")
                    console.print("   Install with: [cyan]pip install textual[/cyan]")
                    console.print("   [dim]Showing text-based dashboard instead...[/dim]")
                    launch_dashboard()  # Will show text version

            elif user_input.lower() == 'sessions':
                show_sessions()

            elif user_input.lower() == 'memory':
                show_memory_stats()

            elif user_input.lower() == 'clear':
                console.clear()

            elif user_input.startswith('search '):
                query = user_input[7:]
                search_memory(query, session_name)

            elif user_input.startswith('analyze '):
                target = user_input[8:].strip()
                if os.path.isfile(target):
                    analyze_code_file(target)
                elif os.path.isdir(target):
                    analyze_directory(target)
                else:
                    console.print(f"❌ Path not found: {target}")

            elif user_input.startswith('explain-code '):
                file_path = user_input[13:].strip()
                explain_code_with_ai(file_path)

            elif user_input == 'project-summary':
                show_project_summary()

            elif user_input.startswith('session '):
                new_session = user_input[8:].strip()
                session_name = new_session
                console.print(f"💼 Switched to session: [bold cyan]{session_name}[/bold cyan]")

            elif user_input:
                # Regular AI query with enhanced context
                console.print("🤖 [dim]Thinking...[/dim]")

                # Build context-aware prompt
                recent_conversations = db.get_recent_context(session_name, limit=3)
                if recent_conversations:
                    context_parts = []
                    for conv in recent_conversations:
                        context_parts.append(f"User: {conv.user_input}")
                        context_parts.append(f"Assistant: {conv.ai_response}")

                    context = "\n".join(context_parts)
                    full_prompt = f"Previous conversation:\n{context}\n\nCurrent question:\nUser: {user_input}\nAssistant:"
                else:
                    full_prompt = user_input

                response = ask_mistral(full_prompt)

                # Save to database
                context_used = f"{len(recent_conversations)} previous exchanges" if recent_conversations else ""
                db.save_conversation(session_name, user_input, response, context_used)

                # Display response
                console.print(Panel(Markdown(response), title="🤖 Sarek", border_style="green"))

        except KeyboardInterrupt:
            console.print("\n👋 [bold]Goodbye![/bold]")
            break
        except Exception as e:
            console.print(f"❌ [red]Error: {e}[/red]")


# ===================== Enhanced Main Function =====================
def main():
    try:
        # Handle command line arguments
        args = sys.argv[1:]

        # Filter out session arguments for main logic
        filtered_args = []
        session_name = "default"
        i = 0
        while i < len(args):
            if args[i] == "--session" and i + 1 < len(args):
                session_name = args[i + 1]
                i += 2  # Skip both --session and the session name
            else:
                filtered_args.append(args[i])
                i += 1

        # Initialize database
        db = EnhancedMemoryDB()

        if not filtered_args:
            # Interactive mode
            interactive_mode()
            return

        # Handle specific commands
        command = filtered_args[0].lower()

        if command in {"--help", "-h", "help"}:
            show_help()

        elif command in {"ui", "dashboard"}:
            if TEXTUAL_AVAILABLE:
                launch_dashboard()
            else:
                console.print("❌ [red]Advanced UI requires textual package[/red]")
                console.print("   Install with: [cyan]pip install textual[/cyan]")
                console.print("   [dim]Showing text-based dashboard instead...[/dim]")
                launch_dashboard()  # Will show text version

        elif command == "sessions":
            show_sessions()

        elif command == "memory":
            show_memory_stats()

        elif command == "search" and len(filtered_args) > 1:
            query = " ".join(filtered_args[1:])
            search_memory(query, session_name)

        elif command == "analyze" and len(filtered_args) > 1:
            target = filtered_args[1]
            if os.path.isfile(target):
                analyze_code_file(target)
            elif os.path.isdir(target):
                analyze_directory(target)
            else:
                console.print(f"❌ Path not found: {target}")

        elif command == "analyze-dir" and len(filtered_args) > 1:
            analyze_directory(filtered_args[1])

        elif command == "explain-code" and len(filtered_args) > 1:
            explain_code_with_ai(filtered_args[1])

        elif command == "project-summary":
            show_project_summary()

        elif command.startswith("read "):
            filepath = command[5:].strip()
            content = query_document(filepath)
            console.print(Markdown(content))

        elif command.startswith("explain "):
            cmd = command.split(" ", 1)[1]
            explanation = explain_shell_command(cmd)
            user_input = f"Explain this shell command:\n\n{explanation}"

            # Use AI to explain
            response = ask_mistral(user_input)
            db.save_conversation(session_name, f"explain command: {cmd}", response)
            console.print(Markdown(response))

        else:
            # Regular AI query
            user_input = " ".join(filtered_args)

            # Handle special input formats
            if not sys.stdin.isatty():
                piped_input = "".join(fileinput.input()).strip()
                user_input = piped_input if piped_input else user_input

            if user_input.startswith("read "):
                filepath = user_input[5:].strip()
                content = query_document(filepath)
                console.print(Markdown(content))
                return

            if user_input.startswith("explain "):
                cmd = user_input.split(" ", 1)[1]
                explanation = explain_shell_command(cmd)
                user_input = f"Explain this shell command:\n\n{explanation}"

            # Build context and query AI
            recent_conversations = db.get_recent_context(session_name, limit=3)
            if recent_conversations:
                context_parts = []
                for conv in recent_conversations:
                    context_parts.append(f"User: {conv.user_input}")
                    context_parts.append(f"Assistant: {conv.ai_response}")

                context = "\n".join(context_parts)
                full_prompt = f"Previous conversation:\n{context}\n\nCurrent question:\nUser: {user_input}\nAssistant:"
            else:
                full_prompt = user_input

            response = ask_mistral(full_prompt)

            # Save conversation
            context_used = f"{len(recent_conversations)} previous exchanges" if recent_conversations else ""
            db.save_conversation(session_name, user_input, response, context_used)

            console.print(Markdown(response))

    except KeyboardInterrupt:
        console.print("\n👋 Interrupted. Goodbye!")
    except Exception as e:
        console.print(f"❌ [red]Unexpected error: {e}[/red]")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()