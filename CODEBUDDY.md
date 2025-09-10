# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with the TradingAgents repository.

## Project Overview

TradingAgents is a multi-agent LLM financial trading framework that simulates real-world trading firms using specialized AI agents for market analysis, research, trading decisions, and risk management.

## Development Commands

### Environment Setup
```bash
# Create and activate conda environment
conda create -n tradingagents python=3.13
conda activate tradingagents

# Install dependencies
pip install -r requirements.txt

# Install additional CLI dependency
pip install typer
```

### Required API Keys
```bash
# Essential for financial data (free tier available)
export FINNHUB_API_KEY=$YOUR_FINNHUB_API_KEY

# LLM providers (configure in config.json or use environment variables)
export OPENAI_API_KEY=$YOUR_OPENAI_API_KEY
export ANTHROPIC_API_KEY=$YOUR_ANTHROPIC_API_KEY
export GOOGLE_API_KEY=$YOUR_GOOGLE_API_KEY
```

### Running the Application
```bash
# Interactive CLI with rich TUI
python -m cli.main

# Direct Python usage
python main.py
```

## Architecture Overview

### Core Framework Structure
- **LangGraph-based**: Uses state machine pattern for agent orchestration
- **Multi-agent system**: Specialized agents work collaboratively through structured workflows
- **Configuration-driven**: JSON-based config system supporting multiple LLM providers

### Key Components

#### Agent Teams (`tradingagents/agents/`)
1. **Analysts** (`analysts/`): Market, Social Media, News, and Fundamentals analysts
2. **Researchers** (`researchers/`): Bull and Bear researchers with debate mechanics  
3. **Trader** (`trader/`): Makes trading decisions based on collective analysis
4. **Risk Management** (`risk_mgmt/`): Conservative, Neutral, and Aggressive risk assessors
5. **Managers** (`managers/`): Research and Risk managers for final approvals

#### Graph Orchestration (`tradingagents/graph/`)
- `trading_graph.py`: Main workflow coordinator using LangGraph
- `propagation.py`: Handles agent execution flow
- `conditional_logic.py`: Decision routing between agents
- `signal_processing.py`: Processes agent outputs and signals

#### Data Layer (`tradingagents/dataflows/`)
- **Online tools**: Real-time data from FinnHub, Reddit, Google News, Yahoo Finance
- **Cached data**: Offline backtesting data in `data_cache/`
- **Interface**: Unified data access layer with online/offline toggle

#### CLI Interface (`cli/`)
- Rich terminal UI with real-time progress visualization
- Interactive configuration and model selection
- Visual indicators for API key status (🔑 configured, 🔒 missing)

### Configuration System

The framework uses `config.json` for:
- **LLM Provider Selection**: OpenAI, Anthropic, Google, OpenRouter, Kimi, Zhipu AI, DeepSeek, Ollama
- **Model Configuration**: Separate "quick_think" and "deep_think" model assignments
- **Debate Settings**: Configurable rounds for investment and risk discussions
- **Tool Settings**: Online vs cached data toggle
- **Language Settings**: Dynamic Chinese/English language switching via "language" field

### Agent Communication Flow

1. **Analysis Phase**: Parallel execution of selected analyst agents
2. **Research Phase**: Bull/Bear researchers debate findings with configurable rounds
3. **Trading Phase**: Trader synthesizes analysis into trading recommendations
4. **Risk Assessment**: Risk management team evaluates proposals with different risk profiles
5. **Final Decision**: Management layer approves/rejects based on comprehensive analysis

### Data and Results

- **Results Directory**: `./results/{ticker}/{date}/` contains analysis reports and logs
- **Message Logging**: Complete agent communication traces in `message_tool.log`
- **Structured Reports**: Markdown files for each analysis phase

## Internationalization (i18n) System

TradingAgents features comprehensive dynamic language switching:

### Core Features
- **Configuration-Driven**: Language controlled via "language" field in config.json
- **Dynamic Switching**: All agent prompts, error messages, UI text automatically switch
- **Complete Coverage**: Includes agent system prompts, tool names, report headers, error messages
- **Supported Languages**: Chinese (zh-CN), English (en-US)

### Usage
```json
// config.json
{
  "language": "zh-CN"  // or "en-US"
}
```

### Technical Implementation
- **I18nManager**: Core internationalization manager in `tradingagents/i18n/`
- **Translation Files**: JSON files in `tradingagents/i18n/locales/` directory
- **Dynamic Loading**: Automatic language initialization based on configuration
- **Agent Integration**: All agents support locale-aware dynamic prompts

### Agent Language Switching
All agents implement dynamic language awareness:
```python
# Agents automatically select language based on configuration
current_locale = get_locale()
if current_locale.startswith("zh"):
    # Use Chinese prompts
else:
    # Use English prompts
```

### Example
Run `python examples/i18n_demo.py` to see the language switching in action.

## Development Notes

### Testing and Debugging
- Set `debug=True` in `TradingAgentsGraph` initialization for detailed logging
- Use `online_tools=False` for consistent backtesting with cached data
- Monitor agent states and decision flow through CLI progress indicators

### Cost Optimization
- Default configuration uses cost-effective models (o4-mini, gpt-4o-mini)
- For production: consider stronger models (gpt-4o, o1-preview)
- Adjust `max_debate_rounds` based on analysis depth requirements

### Internationalization (i18n)
- CLI supports Chinese (zh-CN) and English (en-US) localization
- Translation files located in `tradingagents/i18n/locales/`
- Tool names, parameters, and UI elements are translatable
- Language setting configured in `config.json` under `"language": "zh-CN"`
- Tool name translations in `ui.tool_names` section of zh-CN.json

### Memory and Reflection
- Agents maintain conversation history and reasoning traces
- Framework includes reflection capabilities for learning from trading outcomes
- Memory system tracks financial situations and market patterns

### Common Issues and Fixes
- **Missing typer dependency**: Install with `python -m pip install typer`
- **CLI UnboundLocalError**: Fixed indicator_key variable scoping in CLI display logic
- **ConfigManager AttributeError**: Fixed incorrect usage of `config.get()` instead of proper ConfigManager methods
  - In CLI: Use `config_dict.get()` on dictionary returned by `config_manager.get_config()`
  - In agent_utils: Use `config_manager.get_language()` instead of `config.get("language")`
- **Tool name localization**: Tool names are translated in CLI interface based on i18n files
  - Added translations for common tools: `get_global_news_openai` → `获取全球新闻`
  - Complete list of tool translations in `tradingagents/i18n/locales/zh-CN.json`
- **Report section localization**: Fixed missing translations for report sections and headers
  - `report.sections.trading_plan` → `交易团队计划`
  - Added `report.headers` section for section titles in final reports
  - Updated CLI to use translated headers instead of hardcoded English text
- **OpenAI API compatibility**: Fixed AttributeError in OpenAI functions
  - Corrected `client.responses.create()` to `client.chat.completions.create()`
  - Fixed `response.output_text` to `response.choices[0].message.content`
  - Added error handling for API calls
- **Researcher agent localization**: Fixed English content in bull/bear researcher outputs
  - Updated researcher agents to use i18n system with `_("agents.bull_researcher.role")`
  - Fixed "Bull Researcher Analysis" → `牛市研究员分析` header translations
  - Fixed "Bear Researcher Analysis" → `熊市研究员分析` header translations
  - Ensured LLM responses are generated in Chinese instead of English
- **Dynamic language-aware prompts**: All agent prompts now respect i18n configuration
  - Bull/Bear researchers: Dynamic Chinese/English prompts based on `get_locale()`
  - Trader agent: Language-aware system prompts and transaction proposals
  - Research manager: Localized decision-making prompts
  - Prompts automatically switch between languages based on config.json language setting
- **Complete role title localization**: Fixed all remaining English role titles
  - "Research Manager Decision" → `研究经理决策`
  - Added translations for all risk analyst roles and decisions
  - All agent titles and section headers now properly localized
- **Risk management team i18n**: All risk analysts now support dynamic language prompts
  - **激进分析师**: Language-aware prompts for high-risk advocacy
  - **保守分析师**: Localized prompts for conservative risk analysis
  - **中性分析师**: Balanced perspective prompts in user's language
  - **风险管理经理**: Portfolio management decision prompts with i18n support
  - All risk management LLM responses now generated in configured language