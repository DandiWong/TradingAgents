from tradingagents.config_manager import get_config as get_json_config
from typing import Dict, Optional

# Use default config but allow it to be overridden
_config: Optional[Dict] = None
DATA_DIR: Optional[str] = None


def initialize_config():
    """Initialize the configuration with default values."""
    global _config, DATA_DIR
    if _config is None:
        config_manager = get_json_config()
        _config = config_manager.get_config()
        DATA_DIR = _config["project_settings"]["data_dir"]


def set_config(config: Dict):
    """Update the configuration with custom values."""
    global _config, DATA_DIR
    if _config is None:
        initialize_config()
    _config.update(config)
    DATA_DIR = _config["project_settings"]["data_dir"]


def get_config() -> Dict:
    """Get the current configuration."""
    if _config is None:
        initialize_config()
    return _config.copy()


# Initialize with default config
initialize_config()
