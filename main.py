from tradingagents.config_manager import get_default_config_dict

# Get configuration
config = get_default_config_dict()
config["llm_provider"] = "google"

# Initialize with custom config (with error handling)
try:
    from tradingagents.graph.trading_graph import TradingAgentsGraph
    ta = TradingAgentsGraph(debug=True, config=config)
except ImportError as e:
    print(f"❌ Failed to import TradingAgentsGraph: {e}")
    print("This may be due to dependency issues. Please check your environment.")
    exit(1)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)

# Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
