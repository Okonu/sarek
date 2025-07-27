#!/usr/bin/env python3
"""
Git integration for Sarek AI Assistant
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

try:
    import git

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

from ..core.database import EnhancedMemoryDB


class GitIntegration:
    """Git repository integration and analysis"""

    def __init__(self):
        self.db = EnhancedMemoryDB()
        self.available = GIT_AVAILABLE
        self.repo = None

        if self.available:
            try:
                self.repo = git.Repo('.', search_parent_directories=True)
                print(f"✅ Git repository found: {self.repo.working_dir}")
            except git.exc.InvalidGitRepositoryError:
                print("❌ Not a git repository")
                self.available = False
            except Exception as e:
                print(f"❌ Git initialization error: {e}")
                self.available = False

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive git status"""
        if not self.available:
            return {'error': 'Git not available'}

        if not self.repo:
            return {'error': 'Git repository not initialized'}

        try:
            try:
                current_branch = self.repo.active_branch.name
            except TypeError:
                current_branch = str(self.repo.head.commit)[:8] + " (detached)"

            uncommitted_changes = len(self.repo.index.diff(None))
            untracked_files = len(self.repo.untracked_files)

            ahead_behind = self.get_ahead_behind()

            last_commit = self.repo.head.commit

            status = {
                'branch': current_branch,
                'uncommitted_changes': uncommitted_changes,
                'untracked_files': untracked_files,
                'ahead_behind': ahead_behind,
                'last_commit': {
                    'hash': last_commit.hexsha[:8],
                    'message': last_commit.message.strip(),
                    'author': str(last_commit.author),
                    'date': last_commit.committed_date
                }
            }
            return status
        except Exception as e:
            return {'error': f'Git status error: {e}'}

    def get_ahead_behind(self) -> Dict[str, int]:
        """Get ahead/behind commit count"""
        try:
            origin = self.repo.remotes.origin
            origin.fetch()
            local = self.repo.head.commit
            remote = origin.refs[self.repo.active_branch.name].commit

            ahead = list(self.repo.iter_commits(f'{remote}..{local}'))
            behind = list(self.repo.iter_commits(f'{local}..{remote}'))

            return {'ahead': len(ahead), 'behind': len(behind)}
        except Exception:
            return {'ahead': 0, 'behind': 0}

    def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent git activity"""
        if not self.available:
            return []

        try:
            commits = list(self.repo.iter_commits(max_count=limit))
            activity = []

            for commit in commits:
                activity.append({
                    'hash': commit.hexsha[:8],
                    'message': commit.message.strip(),
                    'author': str(commit.author),
                    'date': datetime.fromtimestamp(commit.committed_date),
                    'files_changed': len(commit.stats.files)
                })

            return activity
        except Exception:
            return []

    def get_commit_info(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific commit"""
        if not self.available:
            return None

        try:
            commit = self.repo.commit(commit_hash)

            diffs = commit.diff(commit.parents[0] if commit.parents else None)

            files_changed = []
            for diff in diffs:
                if diff.a_path:
                    files_changed.append({
                        'path': diff.a_path,
                        'change_type': diff.change_type,
                        'insertions': diff.new_file,
                        'deletions': diff.deleted_file
                    })

            return {
                'hash': commit.hexsha[:8],
                'full_hash': commit.hexsha,
                'message': commit.message.strip(),
                'author': str(commit.author),
                'date': datetime.fromtimestamp(commit.committed_date),
                'files_changed': files_changed,
                'stats': commit.stats.total
            }
        except Exception:
            return None

    def get_branch_info(self) -> Dict[str, Any]:
        """Get information about current branch"""
        if not self.available:
            return {'error': 'Git not available'}

        try:
            current_branch = self.repo.active_branch
            branches = [branch.name for branch in self.repo.branches]

            return {
                'current': current_branch.name,
                'all_branches': branches,
                'remote_branches': [ref.name for ref in self.repo.remote().refs],
                'is_dirty': self.repo.is_dirty(),
                'untracked_files': self.repo.untracked_files
            }
        except Exception as e:
            return {'error': f'Git error: {e}'}

    def analyze_repository(self) -> Dict[str, Any]:
        """Analyze repository structure and health"""
        if not self.available:
            return {'error': 'Git not available'}

        try:
            commits = list(self.repo.iter_commits(max_count=100))
            authors = set(str(commit.author) for commit in commits)

            file_types = {}
            for item in self.repo.tree().traverse():
                if item.type == 'blob':  # It's a file
                    ext = item.path.split('.')[-1] if '.' in item.path else 'no_ext'
                    file_types[ext] = file_types.get(ext, 0) + 1

            return {
                'total_commits': len(commits),
                'total_authors': len(authors),
                'authors': list(authors),
                'file_types': file_types,
                'branches': len(list(self.repo.branches)),
                'tags': len(list(self.repo.tags)),
                'remotes': [remote.name for remote in self.repo.remotes]
            }
        except Exception as e:
            return {'error': f'Analysis error: {e}'}

    def is_repository_healthy(self) -> Dict[str, Any]:
        """Check repository health and suggest improvements"""
        if not self.available:
            return {'error': 'Git not available'}

        health_check = {
            'status': 'healthy',
            'issues': [],
            'recommendations': []
        }

        try:
            if self.repo.is_dirty():
                health_check['issues'].append("Uncommitted changes detected")
                health_check['recommendations'].append("Consider committing or stashing changes")

            if self.repo.untracked_files:
                health_check['issues'].append(f"{len(self.repo.untracked_files)} untracked files")
                health_check['recommendations'].append("Add important files to git or update .gitignore")

            large_files = []
            for item in self.repo.tree().traverse():
                if item.type == 'blob' and item.size > 10 * 1024 * 1024:  # 10MB
                    large_files.append(item.path)

            if large_files:
                health_check['issues'].append(f"Large files detected: {len(large_files)}")
                health_check['recommendations'].append("Consider using Git LFS for large files")

            recent_commits = list(self.repo.iter_commits(max_count=5))
            if recent_commits:
                last_commit_date = datetime.fromtimestamp(recent_commits[0].committed_date)
                days_since_commit = (datetime.now() - last_commit_date).days

                if days_since_commit > 30:
                    health_check['issues'].append("No recent commits (>30 days)")
                    health_check['recommendations'].append("Consider making regular commits")

            if health_check['issues']:
                health_check['status'] = 'needs_attention'

            return health_check

        except Exception as e:
            return {'error': f'Health check error: {e}'}

    def record_git_activity(self, action: str, description: str) -> None:
        """Record git activity in the database"""
        if not self.available:
            return

        try:
            repo_path = str(self.repo.working_dir)
            commit_hash = self.repo.head.commit.hexsha[:8] if self.repo.head.commit else None

            self.db.update_achievements('git_usage')

        except Exception:
            pass