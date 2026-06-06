"""Settings management - Load, save, validate configuration"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .defaults import DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class Settings:
    """Load and manage application settings"""

    def __init__(self, config_file: str = "config/settings.json"):
        self.config_file = Path(config_file)
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge with defaults
                self.config = self._deep_merge(DEFAULT_CONFIG, user_config)
                logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading config: {str(e)}. Using defaults.")
        else:
            logger.info("Using default configuration")
            self.save_config()  # Save defaults for reference

    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        Example: settings.get('llm.primary_provider')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
        self.save_config()

    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.get('llm')

    def get_approval_config(self) -> Dict[str, Any]:
        """Get approval configuration"""
        return self.get('approval')

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
