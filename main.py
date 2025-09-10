from tradingagents.config_manager import get_default_config_dict

# Get configuration
config = get_default_config_dict()
config["llm_provider"] = "google"

# Initialize with custom config (with error handling)
try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    ta = TradingAgentsGraph(debug=True, config=config)
except ImportError as e:
    # Initialize i18n if available
    try:
        from tradingagents.config_manager import ConfigManager
        config_manager = ConfigManager()
        current_locale = config_manager.get_locale()
        from tradingagents.i18n import set_locale, _
        set_locale(current_locale)
    except:
        def _(key: str, **kwargs) -> str:
            return key.format(**kwargs) if kwargs else key
    print(_("main.import_error", error=e))
    print(_("main.dependency_issues"))
    exit(1)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
