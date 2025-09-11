<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
  <br>
  <a href="https://github.com/TauricResearch/" target="_blank"><img alt="Community" src="https://img.shields.io/badge/Join_GitHub_Community-TauricResearch-14C290?logo=discourse"/></a>
</div>

<div align="center">
  <!-- Keep these links. Translations will automatically update with the README. -->
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=de">Deutsch</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=es">Español</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=fr">français</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ja">日本語</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ko">한국어</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=pt">Português</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=ru">Русский</a> | 
  <a href="https://www.readme-i18n.com/TauricResearch/TradingAgents?lang=zh">中文</a>
</div>

---

# TradingAgents: Multi-Agents LLM Financial Trading Framework 

> 🎉 **TradingAgents** officially released! We have received numerous inquiries about the work, and we would like to express our thanks for the enthusiasm in our community.
>
> So we decided to fully open-source the framework. Looking forward to building impactful projects with you!

<div align="center">
<a href="https://www.star-history.com/#TauricResearch/TradingAgents&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" />
   <img alt="TradingAgents Star History" src="https://api.star-history.com/svg?repos=TauricResearch/TradingAgents&type=Date" style="width: 80%; height: auto;" />
 </picture>
</a>
</div>

<div align="center">

🚀 [TradingAgents](#tradingagents-framework) | ⚡ [Installation & CLI](#installation-and-cli) | 🎬 [Demo](https://www.youtube.com/watch?v=90gr5lwjIho) | 📦 [Package Usage](#tradingagents-package) | 🤝 [Contributing](#contributing) | 📄 [Citation](#citation)

</div>

## TradingAgents Framework

TradingAgents is a multi-agent trading framework that mirrors the dynamics of real-world trading firms. By deploying specialized LLM-powered agents: from fundamental analysts, sentiment experts, and technical analysts, to trader, risk management team, the platform collaboratively evaluates market conditions and informs trading decisions. Moreover, these agents engage in dynamic discussions to pinpoint the optimal strategy.

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents framework is designed for research purposes. Trading performance may vary based on many factors, including the chosen backbone language models, model temperature, trading periods, the quality of data, and other non-deterministic factors. [It is not intended as financial, investment, or trading advice.](https://tauric.ai/disclaimer/)

Our framework decomposes complex trading tasks into specialized roles. This ensures the system achieves a robust, scalable approach to market analysis and decision-making.

### Analyst Team
- Fundamentals Analyst: Evaluates company financials and performance metrics, identifying intrinsic values and potential red flags.
- Sentiment Analyst: Analyzes social media and public sentiment using sentiment scoring algorithms to gauge short-term market mood.
- News Analyst: Monitors global news and macroeconomic indicators, interpreting the impact of events on market conditions.
- Technical Analyst: Utilizes technical indicators (like MACD and RSI) to detect trading patterns and forecast price movements.

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### Researcher Team
- Comprises both bullish and bearish researchers who critically assess the insights provided by the Analyst Team. Through structured debates, they balance potential gains against inherent risks.

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Trader Agent
- Composes reports from the analysts and researchers to make informed trading decisions. It determines the timing and magnitude of trades based on comprehensive market insights.

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

### Risk Management and Portfolio Manager
- Continuously evaluates portfolio risk by assessing market volatility, liquidity, and other risk factors. The risk management team evaluates and adjusts trading strategies, providing assessment reports to the Portfolio Manager for final decision.
- The Portfolio Manager approves/rejects the transaction proposal. If approved, the order will be sent to the simulated exchange and executed.

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## Installation and CLI

### Installation

Clone TradingAgents:
```bash
git clone https://github.com/TauricResearch/TradingAgents.git
cd TradingAgents
```

Create a virtual environment in any of your favorite environment managers:
If you have not install miniconda/anaconda, you can just skip this.
```bash
conda create -n tradingagents python=3.13
conda activate tradingagents
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### Initial Setup

TradingAgents now uses a configuration-based approach for API keys and settings. No environment variables are required.

1. **Copy the example configuration:**
```bash
cp config.example.json config.json
```

2. **Configure your API keys in `config.json`:**
```json
{
  "llm_providers": {
    "openai": {
      "api_key": "your-openai-api-key-here"
    },
    "anthropic": {
      "api_key": "your-anthropic-api-key-here"
    }
  }
}
```

3. **Launch the CLI to complete setup:**
```bash
python -m cli.main
```

The CLI will guide you through selecting providers and models, with visual indicators showing which providers have API keys configured.

### CLI Usage

You can also try out the CLI directly by running:
```bash
python -m cli.main
```
You will see a screen where you can select your desired tickers, date, LLMs, research depth, etc.

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

An interface will appear showing results as they load, letting you track the agent's progress as it runs.

<p align="center">
  <img src="assets/cli/cli_news.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

<p align="center">
  <img src="assets/cli/cli_transaction.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

## TradingAgents Package

### Implementation Details

We built TradingAgents with LangGraph to ensure flexibility and modularity. We utilize `o1-preview` and `gpt-4o` as our deep thinking and fast thinking LLMs for our experiments. However, for testing purposes, we recommend you use `o4-mini` and `gpt-4.1-mini` to save on costs as our framework makes **lots of** API calls.

### Python Usage

To use TradingAgents inside your code, you can import the `tradingagents` module and initialize a `TradingAgentsGraph()` object. The `.propagate()` function will return a decision. You can run `main.py`, here's also a quick example:

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.config_manager import get_config

# Get configuration from JSON file
config_manager = get_config()
config = config_manager.get_config()

ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

You can also adjust the default configuration to set your own choice of LLMs, debate rounds, etc.

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.config_manager import get_config

# Get configuration from JSON file
config_manager = get_config()
config = config_manager.get_config()

# Create a custom config
config["deep_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["quick_think_llm"] = "gpt-4.1-nano"  # Use a different model
config["max_debate_rounds"] = 1  # Increase debate rounds
config["online_tools"] = True # Use online tools or cached data

# Initialize with custom config
ta = TradingAgentsGraph(debug=True, config=config)

# forward propagate
_, decision = ta.propagate("NVDA", "2024-05-10")
print(decision)
```

> For `online_tools`, we recommend enabling them for experimentation, as they provide access to real-time data. The agents' offline tools rely on cached data from our **Tauric TradingDB**, a curated dataset we use for backtesting. We're currently in the process of refining this dataset, and we plan to release it soon alongside our upcoming projects. Stay tuned!

## Configuration

TradingAgents uses a comprehensive JSON-based configuration system for managing LLM providers, API keys, project settings, and internationalization. The configuration is stored in `config.json` in the project root.

### Configuration Structure

The configuration file contains the following sections:

- **project_settings**: Project directories and paths
- **llm_providers**: Available LLM providers with their models and API keys
- **active_provider**: Currently selected LLM provider
- **debate_settings**: Agent debate and discussion parameters
- **tool_settings**: Tool usage preferences
- **embedding_settings**: Embedding configuration for memory
- **language**: Interface language setting

### LLM Provider Configuration

#### OpenAI
```json
{
  "llm_providers": {
    "openai": {
      "models": {
        "quick_think": "gpt-4o-mini",
        "deep_think": "gpt-4o"
      },
      "base_url": "https://api.openai.com/v1",
      "api_key": "your-openai-api-key-here",
      "description": "Original OpenAI models"
    }
  }
}
```

#### Anthropic
```json
{
  "llm_providers": {
    "anthropic": {
      "models": {
        "quick_think": "claude-sonnet-4",
        "deep_think": "claude-opus-4"
      },
      "base_url": "https://api.anthropic.com/",
      "api_key": "your-anthropic-api-key-here",
      "description": "Anthropic Claude models"
    }
  }
}
```

#### Google
```json
{
  "llm_providers": {
    "google": {
      "models": {
        "quick_think": "gemini-2.5-flash",
        "deep_think": "gemini-2.5-pro"
      },
      "base_url": "https://generativelanguage.googleapis.com/v1",
      "api_key": "your-google-api-key-here",
      "description": "Google Gemini models"
    }
  }
}
```

#### OpenRouter (Multi-provider Aggregator)
```json
{
  "llm_providers": {
    "openrouter": {
      "models": {
        "quick_think": "z-ai/glm-4.5-air:free",
        "deep_think": "deepseek/deepseek-chat-v3.1:free"
      },
      "base_url": "https://openrouter.ai/api/v1",
      "api_key": "your-openrouter-api-key-here",
      "description": "Aggregator service with multiple model providers"
    }
  }
}
```

#### Chinese Models
```json
{
  "llm_providers": {
    "kimi": {
      "models": {
        "quick_think": "kimi-k2-0905-preview",
        "deep_think": "kimi-k2-0905-preview"
      },
      "base_url": "https://api.moonshot.cn/v1",
      "api_key": "your-moonshot-api-key-here",
      "description": "Chinese AI models with strong multilingual capabilities"
    },
    "zhipu": {
      "models": {
        "quick_think": "glm-4.5-air",
        "deep_think": "glm-4.5"
      },
      "base_url": "https://open.bigmodel.cn/api/paas/v4",
      "api_key": "your-zhipu-api-key-here",
      "description": "Developer of GLM series models"
    },
    "deepseek": {
      "models": {
        "quick_think": "deepseek-chat",
        "deep_think": "deepseek-reasoner"
      },
      "base_url": "https://api.deepseek.com/v1",
      "api_key": "your-deepseek-api-key-here",
      "description": "Advanced reasoning models"
    }
  }
}
```

#### Local Models (Ollama)
```json
{
  "llm_providers": {
    "ollama": {
      "models": {
        "quick_think": "llama3.1",
        "deep_think": "llama3.1"
      },
      "base_url": "http://localhost:11434/v1",
      "api_key": "",
      "description": "Local models (no API key required)"
    }
  }
}
```

### Internationalization Configuration

TradingAgents supports multiple languages for the interface. Set your preferred language in the configuration:

```json
{
  "language": "zh-CN"  // Options: "en-US" (English), "zh-CN" (Chinese)
}
```

#### Available Languages
- **en-US**: English (default)
- **zh-CN**: Simplified Chinese

When set to Chinese, all interface elements, prompts, and agent communications will be in Chinese, providing a fully localized experience.

### Financial Data Configuration

For financial data, TradingAgents uses FinnHub API. Configure it in the `llm_providers` section:

```json
{
  "llm_providers": {
    "finnhub": {
      "api_key": "your-finnhub-api-key-here"
    }
  }
}
```

### CLI Configuration

Use the interactive CLI to configure providers and models:

```bash
# Launch the interactive CLI
python -m cli.main

# The CLI will show available providers with visual indicators:
# 🔑 = API key configured  🔒 = No API key configured

# Navigate through the setup process:
# 1. Select your LLM provider
# 2. Choose quick think and deep think models
# 3. Configure other settings as needed
```

### Configuration File Template

See `config.example.json` for a complete template with all available options. You can copy it to `config.json` and customize as needed.

### Model Recommendations

For cost-effective testing:
- **Quick Thinking**: `gpt-4o-mini`, `claude-3-5-haiku-latest`, `gemini-2.0-flash-lite`
- **Deep Thinking**: `gpt-4o`, `claude-3-5-sonnet-latest`, `gemini-2.5-pro`

For production use:
- **Quick Thinking**: `gpt-4o`, `claude-3-5-sonnet-latest`
- **Deep Thinking**: `o1-preview`, `claude-3-opus-latest`, `gemini-2.5-pro`

## Contributing

We welcome contributions from the community! Whether it's fixing a bug, improving documentation, or suggesting a new feature, your input helps make this project better. If you are interested in this line of research, please consider joining our open-source financial AI research community [Tauric Research](https://tauric.ai/).

## Citation

Please reference our work if you find *TradingAgents* provides you with some help :)

```
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```
