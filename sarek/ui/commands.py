#!/usr/bin/env python3
"""
Command interface and help system for Sarek AI Assistant
"""

import time
from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import IntPrompt
from rich.tree import Tree
from rich.markdown import Markdown
from pathlib import Path

from ..constants import SAREK_LOGO, SMART_ALIASES

console = Console()


class CommandInterface:
    """Command interface and help system"""

    @staticmethod
    def show_startup_animation() -> None:
        """Show Star Trek-inspired startup animation"""
        frames = [
            "🖖 [bold cyan]Initializing Sarek...[/bold cyan]",
            "🖖 [bold cyan]Loading neural pathways...[/bold cyan]",
            "🖖 [bold cyan]Establishing logical connections...[/bold cyan]",
            "🖖 [bold green]Ready to assist, human.[/bold green]"
        ]

        for frame in frames:
            console.print(frame)
            time.sleep(0.8)

        console.print()

    @staticmethod
    def show_enhanced_help() -> None:
        """Enhanced help with all features"""
        console.print(SAREK_LOGO)

        help_sections = [
            {
                'title': "🚀 Basic Commands",
                'commands': [
                    ("sarek", "Interactive mode with command palette"),
                    ("sarek 'prompt'", "Ask a direct question"),
                    ("sarek help", "Show this help message"),
                    ("sarek palette", "Show interactive command palette")
                ]
            },
            {
                'title': "🧠 Memory & Sessions",
                'commands': [
                    ("sarek --session <name>", "Use named conversation session"),
                    ("sarek sessions", "List all conversation sessions"),
                    ("sarek search 'query'", "Search conversation history"),
                    ("sarek memory", "Show memory statistics")
                ]
            },
            {
                'title': "🔍 Code Analysis",
                'commands': [
                    ("sarek analyze file.py", "Analyze code file with security checks"),
                    ("sarek analyze-dir ./src", "Analyze entire directory"),
                    ("sarek explain-code file.py", "Get AI explanation of code"),
                    ("sarek project-summary", "Comprehensive project analysis"),
                    ("sarek wtf file.py", "Quick code explanation (alias)")
                ]
            },
            {
                'title': "🔧 Git Integration",
                'commands': [
                    ("sarek git-status", "Enhanced git status with insights"),
                    ("sarek git-commit-msg", "AI-generated commit message"),
                    ("sarek git-explain <hash>", "Explain what a commit does"),
                    ("sarek git-review", "Review current branch changes")
                ]
            },
            {
                'title': "🎤 Voice & Interactive",
                'commands': [
                    ("sarek --voice", "Enable voice interaction mode"),
                    ("sarek voice", "Start voice command mode"),
                    ("sarek dashboard --live", "Real-time dashboard")
                ]
            },
            {
                'title': "🤖 AI Models",
                'commands': [
                    ("sarek --model codellama", "Use CodeLlama for code tasks"),
                    ("sarek --model mistral", "Use Mistral for general tasks"),
                    ("sarek models", "List available models"),
                    ("sarek --auto-model", "Auto-select best model for task")
                ]
            },
            {
                'title': "🏆 Learning & Progress",
                'commands': [
                    ("sarek achievements", "View unlocked achievements"),
                    ("sarek progress", "Show learning progress")
                ]
            },
            {
                'title': "🛠️ System & Utilities",
                'commands': [
                    ("sarek health-check", "System health analysis"),
                    ("sarek config", "View/edit configuration"),
                    ("sarek --theme <name>", "Change color theme")
                ]
            }
        ]

        for section in help_sections:
            console.print(f"\n[bold cyan]{section['title']}[/bold cyan]")

            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Command", style="green", width=30)
            table.add_column("Description", style="white")

            for cmd, desc in section['commands']:
                table.add_row(cmd, desc)

            console.print(table)

        console.print(f"\n[bold yellow]🎯 Smart Aliases:[/bold yellow]")
        alias_text = ", ".join(SMART_ALIASES.keys())
        console.print(f"  {alias_text}")

        console.print(f"\n[bold red]📌 Important:[/bold red] Git commands use hyphens:")
        console.print("  • sarek git-status (not 'git status')")
        console.print("  • sarek git-commit-msg")
        console.print("  • Use spaces for AI queries: sarek 'explain git'")

        console.print(f"\n[bold cyan]🖖 Live long and prosper![/bold cyan]")

    @staticmethod
    def show_command_palette() -> str:
        """Comprehensive command reference with working status"""
        console.print("🖖 [bold cyan]Sarek Complete Command Reference[/bold cyan]\n")

        working_table = Table(title="✅ Confirmed Working Commands")
        working_table.add_column("Command", style="green", width=30)
        working_table.add_column("Description", style="white")
        working_table.add_column("Example", style="dim")

        working_commands = [
            ("sarek help", "Show help system", "sarek help"),
            ("sarek palette", "Interactive command menu", "sarek palette"),
            ("sarek git-status", "Enhanced git status", "sarek git-status"),
            ("sarek analyze <file>", "Analyze code file", "sarek analyze script.py"),
            ("sarek health-check", "System health analysis", "sarek health-check"),
            ("sarek memory", "Memory statistics", "sarek memory"),
            ("sarek achievements", "View achievements", "sarek achievements"),
            ("sarek sessions", "List sessions", "sarek sessions"),
            ("sarek wtf <file>", "Quick code explanation", "sarek wtf script.py"),
            ("sarek 'query'", "AI conversation", "sarek 'explain Python'"),
        ]

        for cmd, desc, example in working_commands:
            working_table.add_row(cmd, desc, example)

        console.print(working_table)
        console.print()

        experimental_table = Table(title="🧪 Experimental Commands (May Need Implementation)")
        experimental_table.add_column("Command", style="yellow", width=30)
        experimental_table.add_column("Description", style="white")
        experimental_table.add_column("Status", style="cyan")

        experimental_commands = [
            ("sarek git-commit-msg", "AI commit messages", "Needs AI integration"),
            ("sarek git-explain <hash>", "Explain commit", "Needs AI integration"),
            ("sarek git-review", "Review changes", "Needs AI integration"),
            ("sarek explain-code <file>", "AI code explanation", "Needs AI integration"),
            ("sarek project-summary", "Project analysis", "Partially working"),
            ("sarek voice", "Voice commands", "Needs voice packages"),
            ("sarek dashboard --live", "Live dashboard", "Working if psutil available"),
        ]

        for cmd, desc, status in experimental_commands:
            experimental_table.add_row(cmd, desc, status)

        console.print(experimental_table)
        console.print()

        format_panel = Panel(
            """🔑 Command Format Rules:

• HYPHENS for specific commands: git-status, health-check, analyze-dir
• SPACES for AI queries: 'explain Python', 'help me debug'
• Files as arguments: analyze script.py, wtf mycode.py

Examples:
✅ sarek git-status           (specific git command)
✅ sarek 'git help'           (AI query about git)
✅ sarek analyze myfile.py    (code analysis)
✅ sarek 'explain this error' (AI conversation)""",
            title="📖 Format Guide",
            border_style="blue"
        )

        console.print(format_panel)
        console.print()

        options_table = Table(title="⚙️ Available Options")
        options_table.add_column("Option", style="cyan", width=25)
        options_table.add_column("Description", style="white")
        options_table.add_column("Example", style="dim")

        options = [
            ("--session <name>", "Use named session", "sarek --session work 'help me'"),
            ("--model <model>", "Specify AI model", "sarek --model codellama 'debug this'"),
            ("--auto-model", "Auto-select model", "sarek --auto-model 'fix my code'"),
            ("--voice", "Enable voice mode", "sarek --voice"),
            ("--theme <theme>", "Change theme", "sarek --theme matrix"),
            ("--live", "Live dashboard", "sarek dashboard --live"),
        ]

        for option, desc, example in options:
            options_table.add_row(option, desc, example)

        console.print(options_table)
        """Interactive command palette"""
        commands = {
            1: ("🔍 Analyze Project", "project-summary"),
            2: ("💬 Start Chat Session", "interactive"),
            3: ("📊 View Memory Stats", "memory"),
            4: ("🔎 Search History", "search"),
            5: ("🎯 Code Analysis", "analyze"),
            6: ("📚 Git Status", "git-status"),
            7: ("🚀 System Health", "health-check"),
            8: ("🏆 Achievements", "achievements"),
            9: ("🎤 Voice Mode", "voice"),
            10: ("🎨 Live Dashboard", "dashboard"),
            11: ("📋 Command Reference", "commands")
        }

        console.print(Panel.fit("🖖 [bold cyan]Sarek Command Palette[/bold cyan]", style="cyan"))

        table = Table(show_header=False, box=None)
        table.add_column("", style="cyan", width=4)
        table.add_column("", style="white")

        for num, (desc, cmd) in commands.items():
            table.add_row(f"{num}.", desc)

        console.print(table)
        console.print()

        choice = IntPrompt.ask("Select command", choices=list(map(str, commands.keys())))
        return commands[choice][1]


class CodeDisplayHelper:
    """Helper for displaying code analysis results"""

    @staticmethod
    def display_code_analysis(analysis) -> None:
        """Display enhanced code analysis"""
        tree = Tree(f"📄 [bold cyan]{Path(analysis.file_path).name}[/bold cyan]")

        metrics = tree.add("📊 Code Metrics")
        metrics.add(f"Language: [yellow]{analysis.language}[/yellow]")
        metrics.add(f"Lines of Code: [green]{analysis.lines_of_code:,}[/green]")

        complexity_color = "red" if analysis.complexity_score > 5 else "green"
        metrics.add(f"Complexity Score: [{complexity_color}]{analysis.complexity_score:.2f}[/{complexity_color}]")

        if analysis.functions:
            funcs = tree.add(f"🔧 Functions ([green]{len(analysis.functions)}[/green])")
            for func in analysis.functions[:15]:
                funcs.add(func)
            if len(analysis.functions) > 15:
                funcs.add(f"[dim]... and {len(analysis.functions) - 15} more[/dim]")

        if analysis.classes:
            classes = tree.add(f"🏗️ Classes ([blue]{len(analysis.classes)}[/blue])")
            for cls in analysis.classes:
                classes.add(cls)

        if analysis.imports:
            imports = tree.add(f"📦 Imports ([cyan]{len(analysis.imports)}[/cyan])")
            for imp in analysis.imports[:10]:
                imports.add(imp)
            if len(analysis.imports) > 10:
                imports.add(f"[dim]... and {len(analysis.imports) - 10} more[/dim]")

        if analysis.issues:
            issues = tree.add("⚠️ Quality Issues")
            for issue in analysis.issues:
                issues.add(issue)

        if analysis.security_issues:
            security = tree.add("🔒 Security Issues")
            for issue in analysis.security_issues:
                security.add(issue)

        console.print(tree)

    @staticmethod
    def display_directory_summary(analyses: List, directory: str) -> None:
        """Display directory analysis summary"""
        console.print(f"\n📊 [bold cyan]Analysis Summary: {Path(directory).name}[/bold cyan]")

        table = Table(title="File Analysis")
        table.add_column("File", style="cyan")
        table.add_column("Language", style="yellow")
        table.add_column("LOC", style="green", justify="right")
        table.add_column("Complexity", style="magenta", justify="right")
        table.add_column("Issues", style="red", justify="right")
        table.add_column("Security", style="orange", justify="right")

        total_loc = 0
        total_files = len(analyses)
        languages = {}
        total_issues = 0
        total_security = 0

        for analysis in analyses:
            total_loc += analysis.lines_of_code
            languages[analysis.language] = languages.get(analysis.language, 0) + 1
            total_issues += len(analysis.issues)
            total_security += len(analysis.security_issues or [])

            file_name = Path(analysis.file_path).name
            complexity_color = "red" if analysis.complexity_score > 5 else "green"

            table.add_row(
                file_name,
                analysis.language,
                f"{analysis.lines_of_code:,}",
                f"[{complexity_color}]{analysis.complexity_score:.1f}[/{complexity_color}]",
                str(len(analysis.issues)),
                str(len(analysis.security_issues or []))
            )

        console.print(table)

        console.print(f"\n📈 [bold]Summary:[/bold]")
        console.print(f"  • Files analyzed: {total_files}")
        console.print(f"  • Total lines of code: {total_loc:,}")
        console.print(f"  • Quality issues: {total_issues}")
        console.print(f"  • Security issues: {total_security}")
        console.print(f"  • Languages: {', '.join(f'{lang} ({count})' for lang, count in languages.items())}")


class SystemDisplayHelper:
    """Helper for displaying system information"""

    @staticmethod
    def display_health_assessment(assessment: Dict[str, Any]) -> None:
        """Display system health assessment"""
        health_colors = {
            'good': 'green',
            'warning': 'yellow',
            'critical': 'red'
        }

        color = health_colors.get(assessment['overall_health'], 'green')
        score = assessment.get('score', 100)

        header = f"🏥 [bold]Overall Health:[/bold] [{color}]{assessment['overall_health'].upper()}[/{color}]"
        if 'score' in assessment:
            header += f" ([bold]{score}/100[/bold])"

        console.print(Panel(header, title="System Health", border_style=color))

        if assessment['critical_issues']:
            console.print("\n🔴 [bold red]Critical Issues:[/bold red]")
            for issue in assessment['critical_issues']:
                console.print(f"  • {issue}")

        if assessment['warnings']:
            console.print("\n🟡 [bold yellow]Warnings:[/bold yellow]")
            for warning in assessment['warnings']:
                console.print(f"  • {warning}")

        if assessment['recommendations']:
            console.print("\n💡 [bold cyan]Recommendations:[/bold cyan]")
            for rec in assessment['recommendations']:
                console.print(f"  • {rec}")

    @staticmethod
    def display_git_status(status: Dict[str, Any]) -> None:
        """Display enhanced git status"""
        if 'error' in status:
            console.print(f"❌ {status['error']}")
            return

        main_content = (
            f"🌿 [bold]Branch:[/bold] {status['branch']}\n"
            f"📝 [bold]Uncommitted changes:[/bold] {status['uncommitted_changes']}\n"
            f"📁 [bold]Untracked files:[/bold] {status['untracked_files']}\n"
            f"⬆️ [bold]Ahead:[/bold] {status['ahead_behind']['ahead']} commits\n"
            f"⬇️ [bold]Behind:[/bold] {status['ahead_behind']['behind']} commits"
        )

        console.print(Panel(main_content, title="Git Status", border_style="green"))

        if 'last_commit' in status:
            commit = status['last_commit']
            from datetime import datetime
            commit_date = datetime.fromtimestamp(commit['date']).strftime('%Y-%m-%d %H:%M')

            commit_content = (
                f"🔗 [bold]Hash:[/bold] {commit['hash']}\n"
                f"📝 [bold]Message:[/bold] {commit['message']}\n"
                f"👤 [bold]Author:[/bold] {commit['author']}\n"
                f"📅 [bold]Date:[/bold] {commit_date}"
            )

            console.print(Panel(commit_content, title="Last Commit", border_style="blue"))


class SessionDisplayHelper:
    """Helper for displaying session and memory information"""

    @staticmethod
    def show_sessions(db) -> None:
        """Display all conversation sessions"""
        try:
            sessions = db.get_sessions()

            if not sessions:
                console.print("📂 No conversation sessions found.")
                return

            table = Table(title="🗂️ Conversation Sessions")
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
        except Exception as e:
            console.print(f"❌ Error loading sessions: {e}")

    @staticmethod
    def show_memory_stats(db) -> None:
        """Show memory statistics"""
        try:
            from ..features.system_monitor import SystemMonitor
            system_monitor = SystemMonitor()
            stats = system_monitor.get_memory_stats()

            table = Table(title="🧠 Memory Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green", justify="right")

            table.add_row("Total Conversations", f"{stats['conversations']:,}")
            table.add_row("Active Sessions", f"{stats['sessions']:,}")
            table.add_row("Code Analyses", f"{stats['code_analyses']:,}")
            table.add_row("Database Size", f"{stats['database_size_mb']:.2f} MB")

            if 'system_memory_percent' in stats:
                table.add_row("System Memory Usage", f"{stats['system_memory_percent']:.1f}%")

            console.print(table)
        except Exception as e:
            console.print(f"❌ Error loading memory stats: {e}")

    @staticmethod
    def search_memory(query: str, session_name: str, db) -> None:
        """Search conversation history"""
        try:
            conversations = db.search_conversations(query, session_name)

            if not conversations:
                console.print(f"🔍 No conversations found matching '{query}'")
                return

            console.print(f"🔍 Found {len(conversations)} matching conversations:")

            for conv in conversations:
                ai_preview = conv.ai_response[:150] + "..." if len(conv.ai_response) > 150 else conv.ai_response
                user_preview = conv.user_input[:100] + "..." if len(conv.user_input) > 100 else conv.user_input

                panel = Panel(
                    f"[bold cyan]User:[/bold cyan] {user_preview}\n[bold green]AI ({conv.model_used}):[/bold green] {ai_preview}",
                    title=f"📅 {conv.session_name} | {conv.timestamp.strftime('%Y-%m-%d %H:%M')}",
                    border_style="blue"
                )
                console.print(panel)
        except Exception as e:
            console.print(f"❌ Error searching conversations: {e}")


class ModelDisplayHelper:
    """Helper for displaying AI model information"""

    @staticmethod
    def show_available_models(ai) -> None:
        """Show available AI models"""
        try:
            models = ai.get_available_models()

            console.print("🤖 [bold cyan]Available Models:[/bold cyan]")

            table = Table()
            table.add_column("Model", style="cyan")
            table.add_column("Best For", style="green")

            model_descriptions = {
                'mistral': 'General conversation, technical questions',
                'codellama': 'Code analysis, programming help',
                'llama2': 'Creative writing, general chat',
                'gemma': 'Fast responses, lightweight tasks'
            }

            for model in models:
                description = model_descriptions.get(model, 'General purpose')
                table.add_row(model, description)

            console.print(table)

            console.print(f"\n💡 Use --model <name> to specify a model")
            console.print(f"💡 Use --auto-model for automatic selection")

        except Exception as e:
            console.print(f"❌ Error getting available models: {e}")

    @staticmethod
    def show_config(config) -> None:
        """Show current configuration"""
        console.print("⚙️ [bold cyan]Sarek Configuration[/bold cyan]")

        table = Table()
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Description", style="dim")

        settings = [
            ('theme', config.get('theme'), 'Color theme (vulcan, matrix, cyberpunk)'),
            ('default_model', config.get('default_model'), 'Default AI model'),
            ('voice_enabled', config.get('voice_enabled'), 'Voice interaction enabled'),
            ('startup_animation', config.get('startup_animation'), 'Show startup animation'),
            ('context_limit', config.get('context_limit'), 'Conversation context limit'),
            ('auto_git_integration', config.get('auto_git_integration'), 'Automatic git integration'),
            ('achievements_enabled', config.get('achievements_enabled'), 'Achievement system enabled')
        ]

        for setting, value, description in settings:
            table.add_row(setting, str(value), description)

        console.print(table)
        from ..constants import CONFIG_PATH
        console.print(f"\n💡 Edit config file: {CONFIG_PATH}")