"""
Configuration management for TradingAgents.
Handles loading and accessing configuration from JSON file.
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

# Import i18n support
try:
    from .i18n import _
except ImportError:
    # Fallback if i18n is not available
    def _(key: str, **kwargs) -> str:
        return key.format(**kwargs) if kwargs else key


class ConfigManager:
    """Manages configuration loading and access for TradingAgents."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize ConfigManager with optional config path."""
        self.config_path = config_path or self._get_default_config_path()
        self._config = None
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        # Look for config.json in current directory and parent directories
        current_dir = Path.cwd()
        
        # Check current directory
        config_file = current_dir / "config.json"
        if config_file.exists():
            return str(config_file)
        
        # Check parent directory (for when running from subdirectories)
        parent_config = current_dir.parent / "config.json"
        if parent_config.exists():
            return str(parent_config)
        
        # Check project root
        script_dir = Path(__file__).parent.parent
        root_config = script_dir / "config.json"
        if root_config.exists():
            return str(root_config)
        
        # Fallback to current directory
        return str(current_dir / "config.json")
    
    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                # Create default config if file doesn't exist
                self._config = self._get_default_config()
                self.save_config()
        except (json.JSONDecodeError, IOError) as e:
            # Initialize i18n if available
            try:
                current_locale = self.get_locale()
                from .i18n import set_locale
                set_locale(current_locale)
            except:
                pass
            print(_("config.load_warning", path=self.config_path, error=e))
            print(_("config.using_default"))
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "project_settings": {
                "project_dir": "./tradingagents",
                "results_dir": "./results",
                "data_dir": "./data",
                "data_cache_dir": "./tradingagents/dataflows/data_cache"
            },
            "llm_providers": {
                "openai": {
                    "models": {
                        "quick_think": "gpt-4o-mini",
                        "deep_think": "o4-mini"
                    },
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "",
                    "description": "Original OpenAI models"
                }
            },
            "active_provider": "openai",
            "debate_settings": {
                "max_debate_rounds": 1,
                "max_risk_discuss_rounds": 1,
                "max_recur_limit": 100
            },
            "tool_settings": {
                "online_tools": True
            },
            "embedding_settings": {
                "enabled": True,
                "provider": "auto",
                "fallback_to_mock": True,
                "embedding_dim": 1536
            },
            "language": "zh-CN"
        }
    
    def save_config(self) -> None:
        """Save current configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(_("config.save_warning", path=self.config_path, error=e))
    
    def get_config(self) -> Dict[str, Any]:
        """Get the complete configuration."""
        return self._config.copy()
    
    def get_locale(self) -> str:
        """Get the current locale/language setting."""
        return self._config.get("language", "en-US")
    
    def set_locale(self, locale: str) -> None:
        """Set the current locale/language setting."""
        self._config["language"] = locale
        self.save_config()
    
    def get_active_provider(self) -> str:
        """Get the active LLM provider."""
        return self._config.get("active_provider", "openai")
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        return self._config.get("llm_providers", {}).get(provider, {})
    
    def get_model_config(self, provider: str, model_type: str) -> str:
        """Get model configuration for a specific provider and type."""
        provider_config = self.get_provider_config(provider)
        models = provider_config.get("models", {})
        return models.get(model_type, "")
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for a specific provider."""
        provider_config = self.get_provider_config(provider)
        return provider_config.get("api_key", "")
    
    def get_base_url(self, provider: str) -> str:
        """Get base URL for a specific provider."""
        provider_config = self.get_provider_config(provider)
        return provider_config.get("base_url", "")
    
    def get_project_setting(self, key: str, default: Any = None) -> Any:
        """Get a project setting value."""
        return self._config.get("project_settings", {}).get(key, default)
    
    def get_debate_setting(self, key: str, default: Any = None) -> Any:
        """Get a debate setting value."""
        return self._config.get("debate_settings", {}).get(key, default)
    
    def get_tool_setting(self, key: str, default: Any = None) -> Any:
        """Get a tool setting value."""
        return self._config.get("tool_settings", {}).get(key, default)
    
    def get_embedding_setting(self, key: str, default: Any = None) -> Any:
        """Get an embedding setting value."""
        return self._config.get("embedding_settings", {}).get(key, default)
    
    def get_language(self) -> str:
        """Get the current language setting."""
        return self._config.get("language", "en-US")
    
    def set_language(self, language: str) -> None:
        """Set the current language."""
        self._config["language"] = language
    
    def set_active_provider(self, provider: str) -> None:
        """Set the active LLM provider."""
        self._config["active_provider"] = provider
    
    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for a specific provider."""
        if provider not in self._config.get("llm_providers", {}):
            self._config["llm_providers"][provider] = {}
        self._config["llm_providers"][provider]["api_key"] = api_key
    
    def set_model_config(self, provider: str, model_type: str, model_name: str) -> None:
        """Set model configuration for a specific provider and type."""
        if provider not in self._config.get("llm_providers", {}):
            self._config["llm_providers"][provider] = {}
        if "models" not in self._config["llm_providers"][provider]:
            self._config["llm_providers"][provider]["models"] = {}
        self._config["llm_providers"][provider]["models"][model_type] = model_name
    
    def get_available_providers(self) -> Dict[str, Dict[str, Any]]:
        """Get all available providers with their configurations."""
        return self._config.get("llm_providers", {})
    
    def get_provider_description(self, provider: str) -> str:
        """Get description for a specific provider."""
        provider_config = self.get_provider_config(provider)
        return provider_config.get("description", "")


# Global config instance
_config_manager = None


def get_config() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_config() -> None:
    """Reload the configuration from file."""
    global _config_manager
    _config_manager = ConfigManager()


def get_default_config_dict() -> Dict[str, Any]:
    """Get default configuration dictionary for backward compatibility."""
    config = get_config()
    
    # Return both flat config for legacy support and full config for embedding
    full_config = config.get_config()
    flat_config = {
        "project_dir": config.get_project_setting("project_dir"),
        "results_dir": config.get_project_setting("results_dir"),
        "data_dir": config.get_project_setting("data_dir"),
        "data_cache_dir": config.get_project_setting("data_cache_dir"),
        "llm_provider": config.get_active_provider(),
        "deep_think_llm": config.get_model_config(config.get_active_provider(), "deep_think"),
        "quick_think_llm": config.get_model_config(config.get_active_provider(), "quick_think"),
        "backend_url": config.get_base_url(config.get_active_provider()),
        "max_debate_rounds": config.get_debate_setting("max_debate_rounds"),
        "max_risk_discuss_rounds": config.get_debate_setting("max_risk_discuss_rounds"),
        "max_recur_limit": config.get_debate_setting("max_recur_limit"),
        "online_tools": config.get_tool_setting("online_tools"),
        "api_keys": {
            provider: config.get_api_key(provider)
            for provider in config.get_available_providers().keys()
        },
        # Include full config for embedding support
        "_full_config": full_config
    }
    
    return flat_config