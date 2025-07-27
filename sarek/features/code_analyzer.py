#!/usr/bin/env python3
"""
Advanced code analysis for Sarek AI Assistant
"""

import os
import ast
import re
import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.database import EnhancedMemoryDB
from ..core.data_models import CodeAnalysis
from ..constants import DB_PATH, SUPPORTED_EXTENSIONS

console = Console()


class AdvancedCodeAnalyzer:
    """Advanced code analysis with security checks and caching"""

    def __init__(self):
        self.db = EnhancedMemoryDB()
        self.supported_extensions = SUPPORTED_EXTENSIONS

    def get_file_hash(self, file_path: str) -> str:
        """Generate hash of file content for caching"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""

    def analyze_python_file(self, file_path: str) -> CodeAnalysis:
        """Enhanced Python analysis with security checks"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return CodeAnalysis(
                file_path=file_path,
                language="python",
                lines_of_code=0,
                complexity_score=0.0,
                functions=[],
                classes=[],
                imports=[],
                issues=[f"File read error: {e}"],
                security_issues=[]
            )

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
                issues=[f"Syntax Error: {e}"],
                security_issues=[]
            )

        functions = []
        classes = []
        imports = []
        complexity = 0
        security_issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
                complexity += sum(1 for n in ast.walk(node)
                                  if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.With)))

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

            elif isinstance(node, ast.Import):
                imports.extend([alias.name for alias in node.names])

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imports.extend([f"{module}.{alias.name}" for alias in node.names])

        security_patterns = [
            (r'eval\s*\(', "🔴 Use of eval() - potential code injection"),
            (r'exec\s*\(', "🔴 Use of exec() - potential code execution"),
            (r'__import__\s*\(', "🟡 Dynamic imports - review for security"),
            (r'shell=True', "🔴 Shell injection risk in subprocess"),
            (r'sql.*%.*%', "🔴 Potential SQL injection"),
            (r'pickle\.loads?\(', "🟡 Pickle usage - ensure trusted data only")
        ]

        for pattern, warning in security_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_issues.append(warning)

        lines_of_code = len([line for line in content.splitlines()
                             if line.strip() and not line.strip().startswith('#')])
        complexity_score = complexity / max(len(functions), 1)

        issues = []
        if len(functions) > 25:
            issues.append("🔴 High function count - consider splitting into modules")
        if lines_of_code > 1000:
            issues.append("🟡 Large file - consider refactoring")
        if complexity_score > 8:
            issues.append("🔴 High complexity - simplify conditional logic")
        if len(classes) > 10:
            issues.append("🟡 Many classes - consider design patterns")

        content_lower = content.lower()
        if 'todo' in content_lower or 'fixme' in content_lower:
            issues.append("📝 Contains TODO/FIXME comments")
        if content.count('except:') > 0:
            issues.append("⚠️ Bare except clauses - specify exception types")
        if 'print(' in content and 'debug' not in content_lower:
            issues.append("🟡 Print statements found - consider using logging")

        return CodeAnalysis(
            file_path=file_path,
            language="python",
            lines_of_code=lines_of_code,
            complexity_score=complexity_score,
            functions=functions,
            classes=classes,
            imports=imports,
            issues=issues,
            security_issues=security_issues
        )

    def analyze_generic_file(self, file_path: str, language: str) -> CodeAnalysis:
        """Basic analysis for non-Python files"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return CodeAnalysis(
                file_path=file_path,
                language=language,
                lines_of_code=0,
                complexity_score=0.0,
                functions=[],
                classes=[],
                imports=[],
                issues=[f"File read error: {e}"],
                security_issues=[]
            )

        lines = content.splitlines()
        lines_of_code = len([line for line in lines if line.strip()])

        functions = []
        classes = []
        imports = []
        issues = []
        security_issues = []

        if language == 'javascript':
            functions = re.findall(r'function\s+(\w+)', content)
            functions.extend(re.findall(r'(\w+)\s*:\s*function', content))
            functions.extend(re.findall(r'const\s+(\w+)\s*=\s*\(.*?\)\s*=>', content))
            classes = re.findall(r'class\s+(\w+)', content)
            imports = re.findall(r'import.*from\s+[\'"]([^\'"]+)[\'"]', content)

            js_security_patterns = [
                (r'eval\s*\(', "🔴 Use of eval() - code injection risk"),
                (r'innerHTML\s*=', "🟡 innerHTML usage - XSS risk"),
                (r'document\.write\s*\(', "🔴 document.write - XSS vulnerability"),
                (r'\.html\s*\(.*\$', "🟡 Potential XSS in jQuery html()")
            ]

            for pattern, warning in js_security_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    security_issues.append(warning)

        elif language == 'php':
            functions = re.findall(r'function\s+(\w+)', content)
            classes = re.findall(r'class\s+(\w+)', content)

            php_security_patterns = [
                (r'\$_GET\[', "🟡 Direct $_GET usage - validate input"),
                (r'\$_POST\[', "🟡 Direct $_POST usage - validate input"),
                (r'eval\s*\(', "🔴 Use of eval() - code injection"),
                (r'exec\s*\(', "🔴 Use of exec() - command injection"),
                (r'mysql_query\s*\(', "🔴 Deprecated mysql_query - use PDO"),
                (r'md5\s*\(.*password', "🟡 MD5 for passwords - use stronger hashing")
            ]

            for pattern, warning in php_security_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    security_issues.append(warning)

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
            issues=issues,
            security_issues=security_issues
        )

    def analyze_file_with_progress(self, file_path: str) -> Optional[CodeAnalysis]:
        """Analyze file with progress indication and caching"""
        if not os.path.exists(file_path):
            return None

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
        ) as progress:
            task = progress.add_task("🔍 Analyzing file...", total=None)

            file_hash = self.get_file_hash(file_path)
            if not file_hash:
                return None

            progress.update(task, description="💾 Checking cache...")

            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute("""
                    SELECT analysis_data FROM code_analysis
                    WHERE file_path = ? AND file_hash = ?
                """, (file_path, file_hash))

                row = cursor.fetchone()
                if row:
                    progress.update(task, description="✅ Found cached analysis")
                    try:
                        data = json.loads(row[0])
                        return CodeAnalysis(**data)
                    except Exception:
                        pass

            progress.update(task, description="🧠 Analyzing code structure...")

            ext = Path(file_path).suffix.lower()
            language = self.supported_extensions.get(ext, 'unknown')

            if language == 'python':
                analysis = self.analyze_python_file(file_path)
            else:
                analysis = self.analyze_generic_file(file_path, language)

            progress.update(task, description="💾 Caching results...")

            if analysis:
                try:
                    with sqlite3.connect(DB_PATH) as conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO code_analysis 
                            (file_path, file_hash, language, lines_of_code, complexity_score, analysis_data)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            file_path, file_hash, analysis.language, analysis.lines_of_code,
                            analysis.complexity_score, json.dumps(analysis.__dict__, default=str)
                        ))
                except Exception:
                    pass

            progress.update(task, description="✅ Analysis complete!")

        self.db.update_achievements('code_analysis')

        return analysis