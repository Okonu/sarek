#!/usr/bin/env python3
"""
Configuration management for Sarek AI Assistant
"""

import json
from typing import Any, Dict
from ..constants import CONFIG_PATH


class ConfigManager:
    """Manages user configuration settings"""

    def __init__(self):
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load user configuration from file"""
        default_config = {
            'theme': 'vulcan',
            'default_model': 'mistral',
            'voice_enabled': False,
            'startup_animation': True,
            'context_limit': 3,
            'auto_git_integration': True,
            'achievements_enabled': True,
            'system_monitoring': True
        }

        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                # If config is corrupted, use defaults
                pass

        return default_config

    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value and save"""
        self.config[key] = value
        self.save_config()

    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(updates)
        self.save_config()

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = {
            'theme': 'vulcan',
            'default_model': 'mistral',
            'voice_enabled': False,
            'startup_animation': True,
            'context_limit': 3,
            'auto_git_integration': True,
            'achievements_enabled': True,
            'system_monitoring': True
        }
        self.save_config()