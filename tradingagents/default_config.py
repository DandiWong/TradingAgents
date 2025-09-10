import os
from tradingagents.config_manager import get_default_config_dict

# Legacy DEFAULT_CONFIG for backward compatibility
# This now loads from config.json but maintains the same structure
DEFAULT_CONFIG = get_default_config_dict()

# Ensure project directory is set correctly
DEFAULT_CONFIG["project_dir"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
DEFAULT_CONFIG["data_cache_dir"] = os.path.join(
    DEFAULT_CONFIG["project_dir"],
    "dataflows/data_cache",
)
