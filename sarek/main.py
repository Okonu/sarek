#!/usr/bin/env python3
"""
Main entry point for Sarek AI Assistant
"""

import sys
import argparse
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm

from .core.config import ConfigManager
from .core.database import EnhancedMemoryDB
from .core.ai_interface import AIInterface

from .features.code_analyzer import AdvancedCodeAnalyzer
from .features.git_integration import GitIntegration
from .features.voice_interface import VoiceInterface
from .features.system_monitor import SystemMonitor

from .ui.dashboard import Dashboard, AchievementDisplay
from .ui.commands import (
    CommandInterface, CodeDisplayHelper, SystemDisplayHelper,
    SessionDisplayHelper, ModelDisplayHelper
)

from .constants import SMART_ALIASES

console = Console()


class SarekApplication:
    """Main Sarek application class"""

    def __init__(self):
        self.config = ConfigManager()
        self.db = EnhancedMemoryDB()
        self.ai = AIInterface(self.config)

        self.code_analyzer = AdvancedCodeAnalyzer()
        self.git_integration = GitIntegration()
        self.voice_interface = VoiceInterface()
        self.system_monitor = SystemMonitor()

        self.dashboard = Dashboard(
            self.config, self.db, self.system_monitor, self.git_integration
        )

    def run(self, args: argparse.Namespace) -> None:
        """Main application entry point"""
        if self.config.get('startup_animation', True) or args.startup_animation:
            CommandInterface.show_startup_animation()

        if args.theme:
            self.config.set('theme', args.theme)
            console.print(f"🎨 Theme changed to: {args.theme}")

        if args.help or (not args.command and len(sys.argv) == 1):
            CommandInterface.show_enhanced_help()
            return

        session_name = args.session or "default"

        if args.voice:
            self.config.set('voice_enabled', True)
            console.print("🎤 [bold cyan]Voice mode enabled[/bold cyan]")

            if not self.voice_interface.available:
                console.print("❌ Voice interface not available. Install: pip install SpeechRecognition pyttsx3")
                return

        if not args.command:
            self._run_interactive_mode(session_name, args)
        else:
            self._run_command_mode(args.command, session_name, args)

    def _run_interactive_mode(self, session_name: str, args: argparse.Namespace) -> None:
        """Run interactive mode with command palette"""
        try:
            while True:
                console.print("\n🖖 [bold cyan]Sarek Interactive Mode[/bold cyan]")
                console.print("Type a command, 'palette' for menu, 'help' for help, or 'exit' to quit.")

                if self.config.get('voice_enabled', False):
                    user_input = Prompt.ask(f"[{session_name}] 🖖", default="")
                    if user_input.lower() == 'listen':
                        voice_input = self.voice_interface.listen()
                        if voice_input:
                            user_input = voice_input
                else:
                    user_input = Prompt.ask(f"[{session_name}] 🖖", default="")

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    console.print("👋 [bold]Live long and prosper![/bold]")
                    break
                elif user_input.lower() == 'palette':
                    command = CommandInterface.show_command_palette()
                    self._process_command(command, [], session_name, args)
                elif user_input.lower() == 'help':
                    CommandInterface.show_enhanced_help()
                elif user_input:
                    self._process_query(user_input, session_name, args)

        except KeyboardInterrupt:
            console.print("\n👋 Interrupted. Goodbye!")

    def _run_command_mode(self, command_list: List[str], session_name: str, args: argparse.Namespace) -> None:
        """Run single command mode"""
        command = command_list[0].lower() if command_list else ""
        command_args = command_list[1:] if len(command_list) > 1 else []

        if command in SMART_ALIASES:
            command = SMART_ALIASES[command]

        self._process_command(command, command_args, session_name, args)

    def _process_command(self, command: str, command_args: List[str], session_name: str,
                         args: argparse.Namespace) -> None:
        """Process specific commands"""

        if command == "help":
            CommandInterface.show_enhanced_help()

        elif command == "palette":
            new_command = CommandInterface.show_command_palette()
            self._process_command(new_command, [], session_name, args)

        elif command == "dashboard":
            if args.live:
                self.dashboard.create_live_dashboard()
            else:
                self.dashboard.create_static_dashboard()

        elif command == "achievements":
            achievements = self.db.get_achievements()
            AchievementDisplay.display_achievements(achievements)

        elif command == "health-check":
            if self.system_monitor.available:
                assessment = self.system_monitor.get_health_assessment()
                SystemDisplayHelper.display_health_assessment(assessment)
            else:
                console.print("❌ System monitoring not available")

        elif command == "git-status":
            if self.git_integration.available:
                status = self.git_integration.get_status()
                SystemDisplayHelper.display_git_status(status)
            else:
                console.print("❌ Git not available or not in repository")

        elif command.startswith("git"):
            self._handle_git_commands(command, command_args, session_name)

        elif command == "analyze":
            self._handle_analyze_command(command_args)

        elif command == "analyze-dir":
            self._handle_analyze_dir_command(command_args)

        elif command == "explain-code":
            self._handle_explain_code_command(command_args, session_name)

        elif command == "project-summary":
            self._handle_project_summary()

        elif command == "sessions":
            SessionDisplayHelper.show_sessions(self.db)

        elif command == "search":
            self._handle_search_command(command_args, session_name)

        elif command == "memory":
            SessionDisplayHelper.show_memory_stats(self.db)

        elif command == "models":
            ModelDisplayHelper.show_available_models(self.ai)

        elif command == "voice":
            self._handle_voice_commands(session_name)

        elif command == "config":
            ModelDisplayHelper.show_config(self.config)

        else:
            full_query = " ".join([command] + command_args)
            self._process_query(full_query, session_name, args)

    def _process_query(self, user_input: str, session_name: str, args: argparse.Namespace) -> None:
        """Process a regular AI query"""

        if args.auto_model:
            model = self.ai.auto_select_model(user_input)
            console.print(f"🤖 [dim]Auto-selected model: {model}[/dim]")
        else:
            model = args.model or self.config.get('default_model', 'mistral')

        console.print("🤖 [dim]Thinking...[/dim]")

        try:
            response, context = self.ai.query_with_context(session_name, user_input, model)

            self.db.save_conversation(session_name, user_input, response, context, model)

            console.print(Panel(Markdown(response), title=f"🤖 Sarek ({model})", border_style="green"))

            if self.config.get('voice_enabled', False) and self.voice_interface.available:
                self.voice_interface.speak(response)

        except Exception as e:
            console.print(f"❌ Error processing query: {e}")

    def _handle_git_commands(self, command: str, command_args: List[str], session_name: str) -> None:
        """Handle git-related commands"""
        if not self.git_integration.available:
            console.print("❌ Git not available or not in a git repository")
            return

        if command == "git-commit-msg":
            console.print("🤖 Generating commit message...")
            try:
                import subprocess

                result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True)
                diff = result.stdout

                if not diff:
                    result = subprocess.run(['git', 'diff'], capture_output=True, text=True)
                    diff = result.stdout

                if not diff:
                    console.print("📝 No changes to commit")
                    return

                diff_sample = diff[:2000] if len(diff) > 2000 else diff

                prompt = f"""Generate a concise, conventional commit message for these git changes:

{diff_sample}

Follow conventional commit format: type(scope): description

Examples:
- feat(auth): add JWT token validation
- fix(api): resolve null pointer exception  
- docs(readme): update installation instructions
- refactor(utils): simplify string formatting
- chore(deps): update dependencies

Respond with just the commit message, no explanation."""

                response, context = self.ai.query_with_context(session_name, prompt, 'mistral')

                commit_msg = response.strip()
                if commit_msg.startswith('"') and commit_msg.endswith('"'):
                    commit_msg = commit_msg[1:-1]

                lines = commit_msg.split('\n')
                commit_msg = lines[0].strip()

                console.print(Panel(commit_msg, title="🔗 Suggested Commit Message", border_style="green"))

                from rich.prompt import Confirm
                if Confirm.ask("Use this commit message?"):
                    try:
                        result = subprocess.run(['git', 'commit', '-m', commit_msg],
                                                capture_output=True, text=True)
                        if result.returncode == 0:
                            console.print("✅ Commit successful!")

                            self.db.save_conversation(
                                session_name,
                                f"generate commit message for changes",
                                f"Generated: {commit_msg}",
                                context,
                                'mistral'
                            )
                        else:
                            console.print(f"❌ Commit failed: {result.stderr}")
                    except Exception as e:
                        console.print(f"❌ Error committing: {e}")

            except Exception as e:
                console.print(f"❌ Error generating commit message: {e}")

        elif command == "git-explain" and command_args:
            commit_hash = command_args[0]
            console.print(f"🤖 Explaining commit {commit_hash}...")
            try:
                import subprocess

                result = subprocess.run(['git', 'show', '--stat', commit_hash],
                                        capture_output=True, text=True)
                if result.returncode != 0:
                    console.print(f"❌ Commit {commit_hash} not found")
                    return

                commit_info = result.stdout[:2000]

                prompt = f"""Explain what this git commit does in simple terms:

{commit_info}

Provide a clear, technical explanation of what was changed and why."""

                response, context = self.ai.query_with_context(session_name, prompt, 'mistral')

                self.db.save_conversation(
                    session_name,
                    f"explain git commit {commit_hash}",
                    response,
                    context,
                    'mistral'
                )

                console.print(Panel(Markdown(response), title=f"📖 Commit {commit_hash}", border_style="blue"))

            except Exception as e:
                console.print(f"❌ Error explaining commit: {e}")

        elif command == "git-review":
            console.print("🤖 Reviewing current changes...")
            try:
                import subprocess

                result = subprocess.run(['git', 'diff'], capture_output=True, text=True)
                diff = result.stdout

                if not diff:
                    result = subprocess.run(['git', 'diff', '--cached'], capture_output=True, text=True)
                    diff = result.stdout

                if diff:
                    diff_sample = diff[:3000] if len(diff) > 3000 else diff

                    prompt = f"""Review these git changes and provide feedback:

{diff_sample}

Please provide:
1. Code quality assessment
2. Potential issues or improvements
3. Security considerations
4. Best practices recommendations"""

                    response, context = self.ai.query_with_context(session_name, prompt, 'codellama')

                    self.db.save_conversation(
                        session_name,
                        "review current git changes",
                        response,
                        context,
                        'codellama'
                    )

                    console.print(Panel(Markdown(response), title="📝 Code Review", border_style="yellow"))
                else:
                    console.print("📝 No changes to review")

            except Exception as e:
                console.print(f"❌ Error reviewing changes: {e}")

        else:
            console.print(f"❌ Unknown git command: {command}")
            console.print("Available: git-status, git-commit-msg, git-explain, git-review")

    def _handle_analyze_command(self, command_args: List[str]) -> None:
        """Handle code analysis command"""
        if not command_args:
            console.print("❌ Please specify a file or directory to analyze")
            return

        import os
        from pathlib import Path

        target = command_args[0]
        if os.path.isfile(target):
            analysis = self.code_analyzer.analyze_file_with_progress(target)
            if analysis:
                CodeDisplayHelper.display_code_analysis(analysis)
        elif os.path.isdir(target):
            self._analyze_directory_with_progress(target)
        else:
            console.print(f"❌ Path not found: {target}")

    def _handle_analyze_dir_command(self, command_args: List[str]) -> None:
        """Handle directory analysis command"""
        if not command_args:
            console.print("❌ Please specify a directory to analyze")
            return

        self._analyze_directory_with_progress(command_args[0])

    def _handle_explain_code_command(self, command_args: List[str], session_name: str) -> None:
        """Handle code explanation command"""
        if not command_args:
            console.print("❌ Please specify a file to explain")
            return

        file_path = command_args[0]
        if not os.path.exists(file_path):
            console.print(f"❌ File not found: {file_path}")
            return

        console.print(f"🤖 [bold cyan]Analyzing {Path(file_path).name} with AI...[/bold cyan]")

        try:
            analysis = self.code_analyzer.analyze_file_with_progress(file_path)

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code_content = f.read()

            if len(code_content) > 4000:
                code_content = code_content[:4000] + "\n... (file truncated for analysis)"

            file_info = ""
            if analysis:
                file_info = f"""
File Analysis:
- Language: {analysis.language}
- Lines of Code: {analysis.lines_of_code}
- Functions: {', '.join(analysis.functions[:5])} {'...' if len(analysis.functions) > 5 else ''}
- Classes: {', '.join(analysis.classes)} 
- Complexity Score: {analysis.complexity_score:.2f}
"""

            prompt = f"""Analyze and explain this code file:

File: {Path(file_path).name}
{file_info}

Code:
```{analysis.language if analysis else 'text'}
{code_content}
```

Please provide:
1. High-level overview of what this code does
2. Key functions/classes and their purposes  
3. Code quality assessment
4. Potential improvements or issues
5. Security considerations (if any)

Be detailed but concise."""

            model = 'codellama' if analysis and analysis.language == 'python' else 'mistral'
            response, context = self.ai.query_with_context(session_name, prompt, model)

            self.db.save_conversation(
                session_name,
                f"explain code: {file_path}",
                response,
                context,
                model
            )

            console.print(
                Panel(Markdown(response), title=f"🤖 AI Analysis: {Path(file_path).name}", border_style="green"))

        except Exception as e:
            console.print(f"❌ Error explaining code: {e}")

    def _handle_project_summary(self) -> None:
        """Handle project summary command"""
        from pathlib import Path
        current_dir = Path.cwd()
        console.print(f"🚀 [bold cyan]Project Analysis: {current_dir.name}[/bold cyan]")
        self._analyze_directory_with_progress(str(current_dir))

    def _handle_search_command(self, command_args: List[str], session_name: str) -> None:
        """Handle search command"""
        if not command_args:
            console.print("❌ Please specify a search query")
            return

        query = " ".join(command_args)
        SessionDisplayHelper.search_memory(query, session_name, self.db)

    def _handle_voice_commands(self, session_name: str) -> None:
        """Handle voice interaction mode"""
        if not self.voice_interface.available:
            console.print("❌ Voice interface not available")
            console.print("Install with: pip install SpeechRecognition pyttsx3")
            return

        console.print("🎤 [bold cyan]Voice Command Mode[/bold cyan]")
        console.print("Say 'exit' or 'quit' to return to text mode")

        while True:
            user_input = self.voice_interface.listen()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'stop']:
                console.print("🔇 Voice mode disabled")
                break

            console.print("🤖 [dim]Processing...[/dim]")
            try:
                response, context = self.ai.query_with_context(session_name, user_input)

                self.db.save_conversation(session_name, user_input, response, context)

                console.print(Panel(Markdown(response), title="🤖 Sarek", border_style="green"))
                self.voice_interface.speak(response)

            except Exception as e:
                console.print(f"❌ Error processing voice command: {e}")

    def _analyze_directory_with_progress(self, directory: str) -> None:
        """Analyze directory with progress bar"""
        from pathlib import Path
        from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

        console.print(f"🔍 [bold cyan]Analyzing directory: {directory}[/bold cyan]")

        path = Path(directory)
        all_files = []
        for ext in self.code_analyzer.supported_extensions.keys():
            all_files.extend(path.rglob(f"*{ext}"))

        if not all_files:
            console.print("❌ No supported code files found")
            return

        analyses = []

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
        ) as progress:

            task = progress.add_task("Analyzing files...", total=len(all_files))

            for file_path in all_files:
                progress.update(task, description=f"Analyzing {file_path.name}...")
                analysis = self.code_analyzer.analyze_file_with_progress(str(file_path))
                if analysis:
                    analyses.append(analysis)
                progress.advance(task)

        if analyses:
            CodeDisplayHelper.display_directory_summary(analyses, directory)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Sarek - Advanced Terminal AI Assistant",
        add_help=False
    )

    parser.add_argument('command', nargs='*', help='Command or query')
    parser.add_argument('--session', '-s', help='Session name')
    parser.add_argument('--model', '-m', help='AI model to use')
    parser.add_argument('--voice', '-v', action='store_true', help='Enable voice mode')
    parser.add_argument('--theme', '-t', help='Color theme')
    parser.add_argument('--help', '-h', action='store_true', help='Show help')
    parser.add_argument('--startup-animation', action='store_true', help='Show startup animation')
    parser.add_argument('--auto-model', action='store_true', help='Auto-select model')
    parser.add_argument('--live', action='store_true', help='Live dashboard mode')

    return parser


def main() -> None:
    """Main entry point"""
    try:
        parser = create_argument_parser()

        try:
            args = parser.parse_args()
        except SystemExit:
            args = argparse.Namespace(command=[], help=True)

        app = SarekApplication()
        app.run(args)

    except KeyboardInterrupt:
        console.print("\n👋 Interrupted. Live long and prosper!")
    except Exception as e:
        console.print(f"❌ [red]Unexpected error: {e}[/red]")
        if "--debug" in sys.argv:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()