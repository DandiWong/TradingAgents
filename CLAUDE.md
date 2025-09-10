# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents is a multi-agent LLM financial trading framework that simulates real-world trading firms. It uses specialized AI agents for market analysis, research, trading decisions, and risk management to evaluate market conditions collaboratively.

## Architecture

The framework is built using LangGraph and consists of several key components:

### Core Structure
- **tradingagents/graph/**: Contains the main workflow orchestration using LangGraph
- **tradingagents/agents/**: Individual agent implementations organized by function
- **tradingagents/dataflows/**: Data fetching and processing utilities
- **cli/**: Command-line interface with rich TUI for interactive analysis

### Agent Teams
1. **Analyst Team** (`tradingagents/agents/analysts/`): Market, Social, News, and Fundamentals analysts
2. **Researcher Team** (`tradingagents/agents/researchers/`): Bull and Bear researchers with debate mechanics
3. **Trader** (`tradingagents/agents/trader/`): Makes trading decisions based on analysis
4. **Risk Management** (`tradingagents/agents/risk_mgmt/`): Risk assessment with different risk profiles
5. **Management** (`tradingagents/agents/managers/`): Research and risk managers for final decisions

## Common Commands

### CLI Usage
```bash
# Run the interactive CLI
python -m cli.main

# Install dependencies
pip install -r requirements.txt

# Run main script
python main.py
```

### Development Setup
```bash
# Set up environment
conda create -n tradingagents python=3.13
conda activate tradingagents
pip install -r requirements.txt

# Required API keys
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY

# API Key Configuration (two methods):
# Method 1: Environment variables (fallback)
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
export ANTHROPIC_API_KEY=$YOUR_ANTHROPIC_API_KEY
export GOOGLE_API_KEY=$YOUR_GOOGLE_API_KEY
export MOONSHOT_API_KEY=$YOUR_MOONSHOT_API_KEY
export ZHIPUAI_API_KEY=$YOUR_ZHIPUAI_API_KEY
export DEEPSEEK_API_KEY=$YOUR_DEEPSEEK_API_KEY

# Method 2: Configuration file (recommended)
# Edit tradingagents/default_config.py and set API keys in the "api_keys" section
```

## Configuration

The system uses a configuration-driven approach in `tradingagents/default_config.py`:
- **LLM Settings**: Provider selection (OpenAI, Anthropic, Google, OpenRouter, Kimi, Zhipu AI, DeepSeek), model choices for deep/quick thinking
- **API Keys**: Configurable API keys for each provider in the `api_keys` section
- **Debate Settings**: Number of rounds for investment and risk discussions
- **Data Settings**: Cache directories, online tools toggle
- **Results Directory**: Where analysis reports and logs are stored

## Key Implementation Details

### Graph Architecture
The main workflow is implemented in `tradingagents/graph/trading_graph.py` using LangGraph's state machine pattern. The graph coordinates agent interactions and manages the flow of information between teams.

### Data Flow
- **Online Tools**: Real-time data from FinnHub, Reddit, Google News, Yahoo Finance
- **Offline Cache**: Cached data in `tradingagents/dataflows/data_cache/` for backtesting
- **Agent Memory**: Each agent maintains conversation history and reasoning traces

### Agent Communication
Agents use structured messages with tool calls for data fetching. The CLI provides real-time visualization of agent progress and decision-making through a rich terminal interface.

## Testing and Debugging

### Debug Mode
Set `debug=True` when initializing `TradingAgentsGraph` for detailed logging and agent state tracking.

### Results Analysis
Analysis results are stored in `./results/{ticker}/{date}/` with:
- **reports/**: Markdown files for each analysis section
- **message_tool.log**: Complete log of agent communications and tool calls

## Configuration Notes

- Default uses OpenAI with o4-mini and gpt-4o-mini models for cost efficiency
- For production, consider using stronger models like `gpt-4o` and `o1-preview`
- `online_tools=True` enables real-time data, `False` uses cached data
- Debate rounds can be adjusted based on desired analysis depth

## Supported LLM Providers

### OpenAI Compatible Providers
These providers use the OpenAI API format:

- **Kimi (Moonshot)**: Chinese AI models with strong multilingual capabilities
  - Models: `moonshot-v1-8k`, `moonshot-v1-32k`, `moonshot-v1-128k`
  - API Key: Configure in `config["api_keys"]["kimi (moonshot)"]` or set `MOONSHOT_API_KEY`
  
- **Zhipu AI**: Developer of GLM series models
  - Models: `glm-4-flash`, `glm-4-air`, `glm-4-airx`, `glm-4-plus`
  - API Key: Configure in `config["api_keys"]["zhipu ai"]` or set `ZHIPUAI_API_KEY`
  
- **DeepSeek**: Advanced reasoning models
  - Models: `deepseek-chat`, `deepseek-coder`
  - API Key: Configure in `config["api_keys"]["deepseek"]` or set `DEEPSEEK_API_KEY`

### Native API Providers
- **OpenAI**: Original OpenAI models
  - API Key: Configure in `config["api_keys"]["openai"]` or set `OPENAI_API_KEY`
- **Anthropic**: Claude models
  - API Key: Configure in `config["api_keys"]["anthropic"]` or set `ANTHROPIC_API_KEY`
- **Google**: Gemini models
  - API Key: Configure in `config["api_keys"]["google"]` or set `GOOGLE_API_KEY`
- **OpenRouter**: Aggregator service
  - API Key: Configure in `config["api_keys"]["openrouter"]` or set `OPENAI_API_KEY`
- **Ollama**: Local models (no API key required)

### CLI Integration
The CLI interface shows visual indicators for API key status:
- 🔑 = API key configured and ready to use
- 🔒 = No API key configured (provider will be displayed in dim text)