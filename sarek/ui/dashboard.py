#!/usr/bin/env python3
"""
Dashboard UI components for Sarek AI Assistant
"""

import time
from typing import Dict, Any
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.tree import Tree
from rich.text import Text

from ..core.config import ConfigManager
from ..core.database import EnhancedMemoryDB
from ..features.system_monitor import SystemMonitor
from ..features.git_integration import GitIntegration

console = Console()


class Dashboard:
    """Main dashboard for displaying system information"""

    def __init__(self, config: ConfigManager, db: EnhancedMemoryDB,
                 system_monitor: SystemMonitor, git_integration: GitIntegration):
        self.config = config
        self.db = db
        self.system_monitor = system_monitor
        self.git_integration = git_integration

    def create_static_dashboard(self) -> None:
        """Display static dashboard"""
        console.print("📊 [bold cyan]Sarek Dashboard[/bold cyan]\n")

        self._display_project_info()

        self._display_system_metrics()

        self._display_memory_stats()

        self._display_git_status()

    def create_live_dashboard(self) -> None:
        """Create a live updating dashboard"""
        console.print("🚀 [bold cyan]Starting live dashboard...[/bold cyan]")
        console.print("[dim]Updates every 2 seconds. Press Ctrl+C to exit.[/dim]\n")

        try:
            with Live(self._create_live_layout(), refresh_per_second=0.5) as live:
                while True:
                    time.sleep(2)
                    live.update(self._create_live_layout())
        except KeyboardInterrupt:
            console.print("\n👋 Dashboard closed.")

    def _create_live_layout(self) -> Layout:
        """Create the live dashboard layout"""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )

        layout["main"].split_row(
            Layout(name="left", ratio=1),
            Layout(name="right", ratio=1)
        )

        layout["left"].split_column(
            Layout(name="system", ratio=1),
            Layout(name="git", ratio=1)
        )

        layout["right"].split_column(
            Layout(name="memory", ratio=1),
            Layout(name="achievements", ratio=1)
        )

        layout["header"].update(self._create_header_panel())
        layout["system"].update(self._create_system_panel())
        layout["git"].update(self._create_git_panel())
        layout["memory"].update(self._create_memory_panel())
        layout["achievements"].update(self._create_achievements_panel())
        layout["footer"].update(self._create_footer_panel())

        return layout

    def _create_header_panel(self) -> Panel:
        """Create header panel"""
        return Panel(
            "[bold cyan]🖖 SAREK LIVE DASHBOARD[/bold cyan]",
            style="cyan"
        )

    def _create_system_panel(self) -> Panel:
        """Create system metrics panel"""
        if not self.system_monitor.available:
            return Panel("System monitoring unavailable", title="System Status")

        try:
            metrics = self.system_monitor.get_system_metrics()
            health = self.system_monitor.get_health_assessment()

            if 'error' in metrics:
                return Panel(metrics['error'], title="System Status")

            health_color = {
                'good': 'green',
                'warning': 'yellow',
                'critical': 'red'
            }.get(health.get('overall_health', 'good'), 'green')

            content = (
                f"💻 [bold]CPU:[/bold] {metrics['cpu']['usage_percent']:.1f}%\n"
                f"🧠 [bold]Memory:[/bold] {metrics['memory']['usage_percent']:.1f}%\n"
                f"💾 [bold]Disk:[/bold] {metrics['disk']['usage_percent']:.1f}%\n"
                f"🏥 [bold]Health:[/bold] [{health_color}]{health['overall_health']}[/{health_color}]\n"
                f"⏱️ [bold]Uptime:[/bold] {metrics['system']['uptime_hours']:.1f}h"
            )

            return Panel(content, title="System Status", border_style="blue")

        except Exception as e:
            return Panel(f"Error: {e}", title="System Status")

    def _create_git_panel(self) -> Panel:
        """Create git status panel"""
        if not self.git_integration.available:
            return Panel("Git not available", title="Git Status")

        try:
            git_status = self.git_integration.get_status()

            if 'error' in git_status:
                return Panel(git_status['error'], title="Git Status")

            content = (
                f"🌿 [bold]Branch:[/bold] {git_status['branch']}\n"
                f"📝 [bold]Changes:[/bold] {git_status['uncommitted_changes']}\n"
                f"📁 [bold]Untracked:[/bold] {git_status['untracked_files']}\n"
                f"⬆️ [bold]Ahead:[/bold] {git_status['ahead_behind']['ahead']} "
                f"⬇️ [bold]Behind:[/bold] {git_status['ahead_behind']['behind']}"
            )

            return Panel(content, title="Git Status", border_style="green")

        except Exception as e:
            return Panel(f"Error: {e}", title="Git Status")

    def _create_memory_panel(self) -> Panel:
        """Create memory statistics panel"""
        try:
            stats = self.system_monitor.get_memory_stats()

            content = (
                f"💬 [bold]Conversations:[/bold] {stats['conversations']:,}\n"
                f"📂 [bold]Sessions:[/bold] {stats['sessions']:,}\n"
                f"📊 [bold]Analyses:[/bold] {stats['code_analyses']:,}\n"
                f"💾 [bold]DB Size:[/bold] {stats['database_size_mb']:.1f} MB"
            )

            return Panel(content, title="Memory Stats", border_style="magenta")

        except Exception as e:
            return Panel(f"Error: {e}", title="Memory Stats")

    def _create_achievements_panel(self) -> Panel:
        """Create achievements panel"""
        try:
            achievements = self.db.get_achievements()
            recent_unlocked = [a for a in achievements if a.unlocked][-3:]

            if recent_unlocked:
                content = "\n".join([f"🏆 {a.name}" for a in recent_unlocked])
            else:
                content = "No achievements unlocked yet"

            return Panel(content, title="Recent Achievements", border_style="yellow")

        except Exception as e:
            return Panel(f"Error: {e}", title="Achievements")

    def _create_footer_panel(self) -> Panel:
        """Create footer panel"""
        return Panel(
            "[dim]Press Ctrl+C to exit dashboard[/dim]",
            style="dim"
        )

    def _display_project_info(self) -> None:
        """Display current project information"""
        from pathlib import Path

        current_dir = Path.cwd()
        file_count = len(list(current_dir.iterdir()))
        python_files = len(list(current_dir.glob('*.py')))
        has_git = (current_dir / '.git').exists()

        content = (
            f"📁 [bold]Directory:[/bold] {current_dir.name}\n"
            f"📝 [bold]Files:[/bold] {file_count}\n"
            f"🐍 [bold]Python files:[/bold] {python_files}\n"
            f"🔧 [bold]Git repo:[/bold] {'Yes' if has_git else 'No'}"
        )

        console.print(Panel(content, title="Current Project", border_style="cyan"))

    def _display_system_metrics(self) -> None:
        """Display system performance metrics"""
        if not self.system_monitor.available:
            console.print("❌ System monitoring not available")
            return

        try:
            metrics = self.system_monitor.get_system_metrics()

            if 'error' in metrics:
                console.print(f"❌ {metrics['error']}")
                return

            table = Table(title="System Metrics")
            table.add_column("Component", style="cyan")
            table.add_column("Usage", style="green", justify="right")
            table.add_column("Details", style="dim")

            cpu_color = "red" if metrics['cpu']['usage_percent'] > 80 else "green"
            table.add_row(
                "CPU",
                f"[{cpu_color}]{metrics['cpu']['usage_percent']:.1f}%[/{cpu_color}]",
                f"{metrics['cpu']['cores_logical']} cores"
            )

            mem_color = "red" if metrics['memory']['usage_percent'] > 80 else "green"
            table.add_row(
                "Memory",
                f"[{mem_color}]{metrics['memory']['usage_percent']:.1f}%[/{mem_color}]",
                f"{metrics['memory']['used_gb']:.1f}GB / {metrics['memory']['total_gb']:.1f}GB"
            )

            disk_color = "red" if metrics['disk']['usage_percent'] > 85 else "green"
            table.add_row(
                "Disk",
                f"[{disk_color}]{metrics['disk']['usage_percent']:.1f}%[/{disk_color}]",
                f"{metrics['disk']['free_gb']:.1f}GB free"
            )

            console.print(table)

        except Exception as e:
            console.print(f"❌ Error displaying system metrics: {e}")

    def _display_memory_stats(self) -> None:
        """Display memory and database statistics"""
        try:
            stats = self.system_monitor.get_memory_stats()

            table = Table(title="Memory Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green", justify="right")

            table.add_row("Total Conversations", f"{stats['conversations']:,}")
            table.add_row("Active Sessions", f"{stats['sessions']:,}")
            table.add_row("Code Analyses", f"{stats['code_analyses']:,}")
            table.add_row("Database Size", f"{stats['database_size_mb']:.2f} MB")

            console.print(table)

        except Exception as e:
            console.print(f"❌ Error loading memory stats: {e}")

    def _display_git_status(self) -> None:
        """Display git repository status"""
        if not self.git_integration.available:
            console.print("❌ Git not available or not in repository")
            return

        try:
            status = self.git_integration.get_status()

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

        except Exception as e:
            console.print(f"❌ Error displaying git status: {e}")


class AchievementDisplay:
    """Display achievements and progress"""

    @staticmethod
    def display_achievements(achievements) -> None:
        """Display achievements in a beautiful format"""
        unlocked = [a for a in achievements if a.unlocked]
        locked = [a for a in achievements if not a.unlocked]

        if unlocked:
            console.print("🏆 [bold yellow]Unlocked Achievements[/bold yellow]")
            for achievement in unlocked:
                console.print(f"  ✅ [bold green]{achievement.name}[/bold green]: {achievement.description}")
            console.print()

        if locked:
            console.print("🔒 [bold dim]Progress Towards Achievements[/bold dim]")
            for achievement in locked:
                progress_bar = "█" * int(achievement.progress / achievement.target * 20)
                progress_bar += "░" * (20 - len(progress_bar))
                percentage = int(achievement.progress / achievement.target * 100)

                console.print(f"  {progress_bar} [dim]{achievement.name}[/dim] ({percentage}%)")
                console.print(f"    {achievement.description} ({achievement.progress}/{achievement.target})")
            console.print()