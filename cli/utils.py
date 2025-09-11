import questionary
from typing import List, Optional, Tuple, Dict, Any
from rich.console import Console

from cli.models import AnalystType
from tradingagents.config_manager import get_config
from tradingagents.i18n import _, init_i18n

# Create a custom checkbox function with i18n support
def localized_checkbox(
    message: str,
    choices: List[questionary.Choice],
    instruction: Optional[str] = None,
    validate: Optional[callable] = None,
    style: Optional[questionary.Style] = None,
) -> questionary.Question:
    """Create a localized checkbox prompt with translated 'done' text."""
    
    # Import required modules
    from prompt_toolkit.application import Application
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.keys import Keys
    from prompt_toolkit.styles import Style
    from questionary.prompts.common import Choice, InquirerControl, Separator
    from questionary.prompts.common import create_inquirer_layout
    from questionary.constants import DEFAULT_QUESTION_PREFIX, DEFAULT_SELECTED_POINTER
    from questionary.question import Question
    from questionary.utils import used_kwargs
    
    # Get translation for 'done' and 'selections'
    done_text = _("cli.done")
    selections_text = _("cli.selections")
    
    # Create the InquirerControl (same as original)
    ic = InquirerControl(
        choices,
        None,  # default
        pointer=DEFAULT_SELECTED_POINTER,
        initial_choice=None,
        show_description=True,
    )
    
    def get_prompt_tokens():
        tokens = []
        tokens.append(("class:qmark", DEFAULT_QUESTION_PREFIX))
        tokens.append(("class:question", " {} ".format(message)))
        
        if ic.is_answered:
            nbr_selected = len(ic.selected_options)
            if nbr_selected == 0:
                tokens.append(("class:answer", done_text))
            elif nbr_selected == 1:
                if isinstance(ic.get_selected_values()[0].title, list):
                    ts = ic.get_selected_values()[0].title
                    tokens.append(
                        (
                            "class:answer",
                            "".join([token[1] for token in ts]),
                        )
                    )
                else:
                    tokens.append(
                        (
                            "class:answer",
                            "[{}]".format(ic.get_selected_values()[0].title),
                        )
                    )
            else:
                # Use translated format: "done (2 selections)"
                tokens.append(
                    ("class:answer", f"{done_text} ({nbr_selected} {selections_text})")
                )
        else:
            if instruction is not None:
                tokens.append(("class:instruction", instruction))
            else:
                tokens.append(
                    (
                        "class:instruction",
                        "(Use arrow keys to move, "
                        "<space> to select, "
                        "<a> to toggle, "
                        "<i> to invert)",
                    )
                )
        return tokens
    
    def get_selected_values() -> List[Any]:
        return [c.value for c in ic.get_selected_values()]
    
    def perform_validation(selected_values: List[str]) -> bool:
        if validate is None:
            return True
        verdict = validate(selected_values)
        valid = verdict is True
        
        if not valid:
            if verdict is False:
                from questionary.constants import INVALID_INPUT
                error_text = INVALID_INPUT
            else:
                error_text = str(verdict)
            
            from prompt_toolkit.formatted_text import FormattedText
            error_message = FormattedText([("class:validation-toolbar", error_text)])
        
        ic.error_message = (
            error_message if not valid and ic.submission_attempted else None
        )
        
        return valid
    
    # Create layout and bindings (simplified version)
    layout = create_inquirer_layout(ic, get_prompt_tokens)
    
    bindings = KeyBindings()
    
    @bindings.add(Keys.ControlQ, eager=True)
    @bindings.add(Keys.ControlC, eager=True)
    def _exit(event):
        event.app.exit(exception=KeyboardInterrupt, style="class:aborting")
    
    @bindings.add(" ", eager=True)
    def toggle(_event):
        pointed_choice = ic.get_pointed_at().value
        if pointed_choice in ic.selected_options:
            ic.selected_options.remove(pointed_choice)
        else:
            ic.selected_options.append(pointed_choice)
        perform_validation(get_selected_values())
    
    @bindings.add("a", eager=True)
    def all(_event):
        all_selected = True
        for c in ic.choices:
            if (
                not isinstance(c, Separator)
                and c.value not in ic.selected_options
                and not c.disabled
            ):
                ic.selected_options.append(c.value)
                all_selected = False
        if all_selected:
            ic.selected_options = []
        perform_validation(get_selected_values())
    
    @bindings.add("i", eager=True)
    def invert(_event):
        inverted_selection = [
            c.value
            for c in ic.choices
            if not isinstance(c, Separator)
            and c.value not in ic.selected_options
            and not c.disabled
        ]
        ic.selected_options = inverted_selection
        perform_validation(get_selected_values())
    
    def move_cursor_down(event):
        ic.select_next()
        while not ic.is_selection_valid():
            ic.select_next()
    
    def move_cursor_up(event):
        ic.select_previous()
        while not ic.is_selection_valid():
            ic.select_previous()
    
    bindings.add(Keys.Down, eager=True)(move_cursor_down)
    bindings.add(Keys.Up, eager=True)(move_cursor_up)
    bindings.add("j", eager=True)(move_cursor_down)
    bindings.add("k", eager=True)(move_cursor_up)
    
    @bindings.add(Keys.ControlM, eager=True)
    def set_answer(event):
        selected_values = get_selected_values()
        ic.submission_attempted = True
        
        if perform_validation(selected_values):
            ic.is_answered = True
            event.app.exit(result=selected_values)
    
    @bindings.add(Keys.Any)
    def other(_event):
        """Disallow inserting other text."""
    
    return Question(
        Application(
            layout=layout,
            key_bindings=bindings,
            style=style or questionary.constants.DEFAULT_STYLE,
            **used_kwargs({}, Application.__init__),
        )
    )

console = Console()


def _get_fallback_shallow_models() -> Dict[str, List[Tuple[str, str]]]:
    """Get fallback shallow thinking models for each provider."""
    return {
        "openai": [("快速思考: gpt-4o-mini", "gpt-4o-mini")],
        "anthropic": [("快速思考: claude-3-5-haiku-latest", "claude-3-5-haiku-latest")],
        "google": [("快速思考: gemini-2.0-flash-lite", "gemini-2.0-flash-lite")],
        "openrouter": [("快速思考: meta-llama/llama-3.3-8b-instruct:free", "meta-llama/llama-3.3-8b-instruct:free")],
        "kimi (moonshot)": [("快速思考: moonshot-v1-8k", "moonshot-v1-8k")],
        "zhipu ai": [("快速思考: glm-4-flash", "glm-4-flash")],
        "deepseek": [("快速思考: deepseek-chat", "deepseek-chat")],
        "ollama": [("快速思考: llama3.1", "llama3.1")],
    }


def _get_fallback_deep_models() -> Dict[str, List[Tuple[str, str]]]:
    """Get fallback deep thinking models for each provider."""
    return {
        "openai": [("深度思考: o4-mini", "o4-mini")],
        "anthropic": [("深度思考: claude-3-5-sonnet-latest", "claude-3-5-sonnet-latest")],
        "google": [("深度思考: gemini-2.5-pro-preview-06-05", "gemini-2.5-pro-preview-06-05")],
        "openrouter": [("深度思考: deepseek/deepseek-chat-v3-0324:free", "deepseek/deepseek-chat-v3-0324:free")],
        "kimi (moonshot)": [("深度思考: moonshot-v1-32k", "moonshot-v1-32k")],
        "zhipu ai": [("深度思考: glm-4-plus", "glm-4-plus")],
        "deepseek": [("深度思考: deepseek-coder", "deepseek-coder")],
        "ollama": [("深度思考: llama3.1", "llama3.1")],
    }

def get_analyst_order():
    """Get analyst options with translations."""
    return [
        (_("analyst_types.market"), AnalystType.MARKET),
        (_("analyst_types.social"), AnalystType.SOCIAL),
        (_("analyst_types.news"), AnalystType.NEWS),
        (_("analyst_types.fundamentals"), AnalystType.FUNDAMENTALS),
    ]


def get_analyst_display_name(analyst_type: AnalystType) -> str:
    """Get translated display name for analyst type."""
    analyst_names = {
        AnalystType.MARKET: _("analyst_types.market"),
        AnalystType.SOCIAL: _("analyst_types.social"),
        AnalystType.NEWS: _("analyst_types.news"),
        AnalystType.FUNDAMENTALS: _("analyst_types.fundamentals"),
    }
    return analyst_names.get(analyst_type, analyst_type.value)

# Keep the old name for backward compatibility
ANALYST_ORDER = get_analyst_order()


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        _("cli.enter_ticker"),
        validate=lambda x: len(x.strip()) > 0 or _("cli.invalid_ticker"),
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        console.print(f"\n[red]{_('error.no_ticker')}[/red]")
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
        _("cli.enter_date"),
        validate=lambda x: validate_date(x.strip())
        or _("cli.invalid_date"),
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        console.print(f"\n[red]{_('error.no_date')}[/red]")
        exit(1)

    return date.strip()


def select_analysts() -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""
    choices = localized_checkbox(
        _("cli.select_analysts"),
        choices=[
            questionary.Choice(display, value=value) for display, value in get_analyst_order()
        ],
        instruction=_("cli.analysts_instruction"),
        validate=lambda x: len(x) > 0 or _("cli.must_select_analyst"),
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
        console.print(f"\n[red]{_('error.no_analysts')}[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        (_("cli.research_depth.shallow"), 1),
        (_("cli.research_depth.medium"), 3),
        (_("cli.research_depth.deep"), 5),
    ]

    # Get translations with fallback
    select_text = _("cli.select_research_depth")
    nav_text = _("cli.navigation_instruction")
    
    # Ensure translations are working
    if select_text == "cli.select_research_depth":
        select_text = "选择您的 [研究深度]："
    if nav_text == "cli.navigation_instruction":
        nav_text = "- 使用方向键导航\n- 按回车键选择"
    
    choice = questionary.select(
        select_text,
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction=nav_text,
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(f"\n[red]{_('error.no_research_depth')}[/red]")
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
        model_options = [(f"{_('cli.model_selection.quick_think_model')}: {quick_think_model}", quick_think_model)]
        
        # Add other available models
        for model_type, model_name in available_models.items():
            if model_type != "quick_think" and model_name:
                model_options.append((f"{_('cli.model_selection.alternative')}: {model_name}", model_name))
    
    # If still no options, use fallback
    if not model_options:
        SHALLOW_AGENT_OPTIONS = _get_fallback_shallow_models()
        model_options = SHALLOW_AGENT_OPTIONS.get(provider.lower(), [(_("cli.model_selection.default_model"), "gpt-4o-mini")])

    # Get translations with fallback
    select_text = _("cli.select_shallow_thinking")
    nav_text = _("cli.navigation_instruction")
    
    # Ensure translations are working
    if select_text == "cli.select_shallow_thinking":
        select_text = "选择您的 [快速思考 LLM 引擎]："
    if nav_text == "cli.navigation_instruction":
        nav_text = "- 使用方向键导航\n- 按回车键选择"
    
    choice = questionary.select(
        select_text,
        choices=[
            questionary.Choice(display, value=value)
            for display, value in model_options
        ],
        instruction=nav_text,
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
            f"\n[red]{_('error.no_shallow_thinking')}[/red]"
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
        model_options = [(f"{_('cli.model_selection.deep_think_model')}: {deep_think_model}", deep_think_model)]
        
        # Add other available models
        for model_type, model_name in available_models.items():
            if model_type != "deep_think" and model_name:
                model_options.append((f"{_('cli.model_selection.alternative')}: {model_name}", model_name))
    
    # If still no options, use fallback
    if not model_options:
        DEEP_AGENT_OPTIONS = _get_fallback_deep_models()
        model_options = DEEP_AGENT_OPTIONS.get(provider.lower(), [(_("cli.model_selection.default_model"), "gpt-4o")])
    
    # Get translations with fallback
    select_text = _("cli.select_deep_thinking")
    nav_text = _("cli.navigation_instruction")
    
    # Ensure translations are working
    if select_text == "cli.select_deep_thinking":
        select_text = "选择您的 [深度思考 LLM 引擎]："
    if nav_text == "cli.navigation_instruction":
        nav_text = "- 使用方向键导航\n- 按回车键选择"
    
    choice = questionary.select(
        select_text,
        choices=[
            questionary.Choice(display, value=value)
            for display, value in model_options
        ],
        instruction=nav_text,
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(f"\n[red]{_('error.no_deep_thinking')}[/red]")
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
        _("cli.select_llm_provider"),
        choices=choices,
        instruction=_("cli.provider_instruction"),
        style=questionary.Style(
            [
                ("selected", "fg:magenta noinherit"),
                ("highlighted", "fg:magenta noinherit"),
                ("pointer", "fg:magenta noinherit"),
            ]
        ),
    ).ask()
    
    if choice is None:
        console.print(f"\n[red]{_('error.no_llm_provider')}[/red]")
        exit(1)
    
    display_name, url = choice
    print(f"{_('cli.selected_provider')}: {display_name}\tURL: {url}")
    
    # Set as active provider
    config_manager.set_active_provider(display_name)
    config_manager.save_config()
    
    return display_name, url
