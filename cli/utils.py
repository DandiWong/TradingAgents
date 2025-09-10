import questionary
from typing import List, Optional, Tuple, Dict
from rich.console import Console

from cli.models import AnalystType
from tradingagents.config_manager import get_config

console = Console()


def _get_fallback_shallow_models() -> Dict[str, List[Tuple[str, str]]]:
    """Get fallback shallow thinking models for each provider."""
    return {
        "openai": [("Quick Think: gpt-4o-mini", "gpt-4o-mini")],
        "anthropic": [("Quick Think: claude-3-5-haiku-latest", "claude-3-5-haiku-latest")],
        "google": [("Quick Think: gemini-2.0-flash-lite", "gemini-2.0-flash-lite")],
        "openrouter": [("Quick Think: meta-llama/llama-3.3-8b-instruct:free", "meta-llama/llama-3.3-8b-instruct:free")],
        "kimi (moonshot)": [("Quick Think: moonshot-v1-8k", "moonshot-v1-8k")],
        "zhipu ai": [("Quick Think: glm-4-flash", "glm-4-flash")],
        "deepseek": [("Quick Think: deepseek-chat", "deepseek-chat")],
        "ollama": [("Quick Think: llama3.1", "llama3.1")],
    }


def _get_fallback_deep_models() -> Dict[str, List[Tuple[str, str]]]:
    """Get fallback deep thinking models for each provider."""
    return {
        "openai": [("Deep Think: o4-mini", "o4-mini")],
        "anthropic": [("Deep Think: claude-3-5-sonnet-latest", "claude-3-5-sonnet-latest")],
        "google": [("Deep Think: gemini-2.5-pro-preview-06-05", "gemini-2.5-pro-preview-06-05")],
        "openrouter": [("Deep Think: deepseek/deepseek-chat-v3-0324:free", "deepseek/deepseek-chat-v3-0324:free")],
        "kimi (moonshot)": [("Deep Think: moonshot-v1-32k", "moonshot-v1-32k")],
        "zhipu ai": [("Deep Think: glm-4-plus", "glm-4-plus")],
        "deepseek": [("Deep Think: deepseek-coder", "deepseek-coder")],
        "ollama": [("Deep Think: llama3.1", "llama3.1")],
    }

ANALYST_ORDER = [
    ("Market Analyst", AnalystType.MARKET),
    ("Social Media Analyst", AnalystType.SOCIAL),
    ("News Analyst", AnalystType.NEWS),
    ("Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "Enter the ticker symbol to analyze:",
        validate=lambda x: len(x.strip()) > 0 or "Please enter a valid ticker symbol.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print("\n[red]No ticker symbol provided. Exiting...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "Enter the analysis date (YYYY-MM-DD):",
        validate=lambda x: validate_date(x.strip())
        or "Please enter a valid date in YYYY-MM-DD format.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print("\n[red]No date provided. Exiting...[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = questionary.checkbox(
        "Select Your [Analysts Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in ANALYST_ORDER
        ],
        instruction="\n- Press Space to select/unselect analysts\n- Press 'a' to select/unselect all\n- Press Enter when done",
        validate=lambda x: len(x) > 0 or "You must select at least one analyst.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        console.print("\n[red]No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("Shallow - Quick research, few debate and strategy discussion rounds", 1),
        ("Medium - Middle ground, moderate debate rounds and strategy discussion", 3),
        ("Deep - Comprehensive research, in depth debate and strategy discussion", 5),
    ]

    choice = questionary.select(
        "Select Your [Research Depth]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No research depth selected. Exiting...[/red]")
        exit(1)

    return choice


def select_shallow_thinking_agent(provider) -> str:
    """Select shallow thinking llm engine using an interactive selection."""
    config_manager = get_config()
    
    # Get available models from config
    provider_config = config_manager.get_provider_config(provider.lower())
    available_models = provider_config.get("models", {})
    
    # If no models configured, use fallback options
    if not available_models:
        SHALLOW_AGENT_OPTIONS = _get_fallback_shallow_models()
        model_options = SHALLOW_AGENT_OPTIONS.get(provider.lower(), [])
    else:
        # Create options from configured models
        quick_think_model = available_models.get("quick_think", "")
        model_options = [(f"Quick Think Model: {quick_think_model}", quick_think_model)]
        
        # Add other available models
        for model_type, model_name in available_models.items():
            if model_type != "quick_think" and model_name:
                model_options.append((f"Alternative: {model_name}", model_name))
    
    # If still no options, use fallback
    if not model_options:
        SHALLOW_AGENT_OPTIONS = _get_fallback_shallow_models()
        model_options = SHALLOW_AGENT_OPTIONS.get(provider.lower(), [("Default Model", "gpt-4o-mini")])

    choice = questionary.select(
        "Select Your [Quick-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in model_options
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(
            "\n[red]No shallow thinking llm engine selected. Exiting...[/red]"
        )
        exit(1)

    # Save the selected model configuration
    config_manager.set_model_config(provider.lower(), "quick_think", choice)
    config_manager.save_config()

    return choice


def select_deep_thinking_agent(provider) -> str:
    """Select deep thinking llm engine using an interactive selection."""
    config_manager = get_config()
    
    # Get available models from config
    provider_config = config_manager.get_provider_config(provider.lower())
    available_models = provider_config.get("models", {})
    
    # If no models configured, use fallback options
    if not available_models:
        DEEP_AGENT_OPTIONS = _get_fallback_deep_models()
        model_options = DEEP_AGENT_OPTIONS.get(provider.lower(), [])
    else:
        # Create options from configured models
        deep_think_model = available_models.get("deep_think", "")
        model_options = [(f"Deep Think Model: {deep_think_model}", deep_think_model)]
        
        # Add other available models
        for model_type, model_name in available_models.items():
            if model_type != "deep_think" and model_name:
                model_options.append((f"Alternative: {model_name}", model_name))
    
    # If still no options, use fallback
    if not model_options:
        DEEP_AGENT_OPTIONS = _get_fallback_deep_models()
        model_options = DEEP_AGENT_OPTIONS.get(provider.lower(), [("Default Model", "gpt-4o")])
    
    choice = questionary.select(
        "Select Your [Deep-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in model_options
        ],
        instruction="\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print("\n[red]No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    # Save the selected model configuration
    config_manager.set_model_config(provider.lower(), "deep_think", choice)
    config_manager.save_config()

    return choice

def select_llm_provider() -> tuple[str, str]:
    """Select the LLM provider using interactive selection."""
    config_manager = get_config()
    providers = config_manager.get_available_providers()
    
    # Check API key availability and create choices with indicators
    choices = []
    
    for provider_name, provider_config in providers.items():
        display_name = provider_name.title()
        url = provider_config.get("base_url", "")
        has_api_key = bool(provider_config.get("api_key", ""))
        
        # Add visual indicator for API key status
        if has_api_key:
            indicator = "🔑"  # Has API key
            choice_text = f"{display_name} {indicator}"
        else:
            indicator = "🔒"  # No API key configured
            choice_text = f"[dim]{display_name} {indicator}[/dim]"
        
        choices.append(questionary.Choice(choice_text, value=(provider_name, url)))
    
    choice = questionary.select(
        "Select your LLM Provider:",
        choices=choices,
        instruction="\n- 🔑 = API key configured  🔒 = No API key configured\n- Use arrow keys to navigate\n- Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()
    
    if choice is None:
        console.print("\n[red]no LLM provider selected. Exiting...[/red]")
        exit(1)
    
    display_name, url = choice
    print(f"You selected: {display_name}\tURL: {url}")
    
    # Set as active provider
    config_manager.set_active_provider(display_name)
    config_manager.save_config()
    
    return display_name, url
