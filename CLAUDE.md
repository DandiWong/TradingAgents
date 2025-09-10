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
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
```

## Configuration

The system uses a configuration-driven approach in `tradingagents/default_config.py`:
- **LLM Settings**: Provider selection (OpenAI, OpenRouter, Google), model choices for deep/quick thinking
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

- Default uses OpenRouter with Gemini models for cost efficiency
- For production, consider using stronger models like `gpt-4o` and `o1-preview`
- `online_tools=True` enables real-time data, `False` uses cached data
- Debate rounds can be adjusted based on desired analysis depth