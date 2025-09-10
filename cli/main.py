from typing import Optional
import datetime
import typer
from pathlib import Path
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.markdown import Markdown
from rich.layout import Layout
from rich.text import Text
from rich.live import Live
from rich.table import Table
from collections import deque
import time
from rich.tree import Tree
from rich import box
from rich.align import Align
from rich.rule import Rule

from tradingagents.config_manager import get_config
from tradingagents.utils.dependency_checker import DependencyChecker

def get_translated_status(status: str) -> str:
    """Get translated status text."""
    return _(f"status.{status}")
from tradingagents.i18n import _, init_i18n, get_i18n_manager
from cli.models import AnalystType
from cli.utils import *

console = Console()

# Initialize i18n system
config_manager = get_config()
config_dict = config_manager.get_config()
language = config_dict.get("language", "en-US")
init_i18n(locale_dir="./tradingagents/i18n/locales", default_locale=language)

app = typer.Typer(
    name=_("app.name"),
    help=_("app.description"),
    add_completion=True,  # Enable shell completion
)


# Create a deque to store recent messages with a maximum length
class MessageBuffer:
    def __init__(self, max_length=100):
        self.messages = deque(maxlen=max_length)
        self.tool_calls = deque(maxlen=max_length)
        self.current_report = None
        self.final_report = None  # Store the complete final report
        self.agent_status = {
            # Analyst Team
            _("analyst_types.market"): "pending",
            _("analyst_types.social"): "pending",
            _("analyst_types.news"): "pending",
            _("analyst_types.fundamentals"): "pending",
            # Research Team
            _("researcher.bull"): "pending",
            _("researcher.bear"): "pending",
            _("researcher.manager"): "pending",
            # Trading Team
            _("ui.trader"): "pending",
            # Risk Management Team
            _("agents.risk_analyst.risky"): "pending",
            _("agents.risk_analyst.neutral"): "pending",
            _("agents.risk_analyst.safe"): "pending",
            # Portfolio Management Team
            _("agents.risk_analyst.portfolio_manager"): "pending",
        }
        self.current_agent = None
        self.report_sections = {
            "market_report": None,
            "sentiment_report": None,
            "news_report": None,
            "fundamentals_report": None,
            "investment_plan": None,
            "trader_investment_plan": None,
            "final_trade_decision": None,
        }

    def add_message(self, message_type, content):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, message_type, content))

    def add_tool_call(self, tool_name, args):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.tool_calls.append((timestamp, tool_name, args))

    def update_agent_status(self, agent, status):
        if agent in self.agent_status:
            self.agent_status[agent] = status
            self.current_agent = agent

    def update_report_section(self, section_name, content):
        if section_name in self.report_sections:
            self.report_sections[section_name] = content
            self._update_current_report()

    def _update_current_report(self):
        # For the panel display, only show the most recently updated section
        latest_section = None
        latest_content = None

        # Find the most recently updated section
        for section, content in self.report_sections.items():
            if content is not None:
                latest_section = section
                latest_content = content
               
        if latest_section and latest_content:
            # Format the current section for display with translated titles
            section_title_keys = {
                "market_report": "report.sections.market_analysis",
                "sentiment_report": "report.sections.social_sentiment",
                "news_report": "report.sections.news_analysis",
                "fundamentals_report": "report.sections.fundamentals_analysis",
                "investment_plan": "report.sections.investment_plan",
                "trader_investment_plan": "report.sections.trading_plan",
                "final_trade_decision": "report.sections.final_decision",
            }
            section_title = _(section_title_keys[latest_section])
            self.current_report = (
                f"### {section_title}\n{latest_content}"
            )

        # Update the final complete report
        self._update_final_report()

    def _update_final_report(self):
        report_parts = []

        # Analyst Team Reports
        if any(
            self.report_sections[section]
            for section in [
                "market_report",
                "sentiment_report",
                "news_report",
                "fundamentals_report",
            ]
        ):
            report_parts.append(f"## {_('report.headers.analyst_team_reports')}")
            if self.report_sections["market_report"]:
                report_parts.append(
                    f"### {_('report.headers.market_analysis')}\n{self.report_sections['market_report']}"
                )
            if self.report_sections["sentiment_report"]:
                report_parts.append(
                    f"### {_('report.headers.social_sentiment')}\n{self.report_sections['sentiment_report']}"
                )
            if self.report_sections["news_report"]:
                report_parts.append(
                    f"### {_('report.headers.news_analysis')}\n{self.report_sections['news_report']}"
                )
            if self.report_sections["fundamentals_report"]:
                report_parts.append(
                    f"### {_('report.headers.fundamentals_analysis')}\n{self.report_sections['fundamentals_report']}"
                )

        # Research Team Reports
        if self.report_sections["investment_plan"]:
            report_parts.append(f"## {_('report.headers.research_team_decision')}")
            report_parts.append(f"{self.report_sections['investment_plan']}")

        # Trading Team Reports
        if self.report_sections["trader_investment_plan"]:
            report_parts.append(f"## {_('report.headers.trading_team_plan')}")
            report_parts.append(f"{self.report_sections['trader_investment_plan']}")

        # Portfolio Management Decision
        if self.report_sections["final_trade_decision"]:
            report_parts.append(f"## {_('report.headers.portfolio_management_decision')}")
            report_parts.append(f"{self.report_sections['final_trade_decision']}")

        self.final_report = "\n\n".join(report_parts) if report_parts else None


message_buffer = MessageBuffer()


def create_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="footer", size=3),
    )
    layout["main"].split_column(
        Layout(name="upper", ratio=3), Layout(name="analysis", ratio=5)
    )
    layout["upper"].split_row(
        Layout(name="progress", ratio=2), Layout(name="messages", ratio=3)
    )
    return layout


def update_display(layout, spinner_text=None):
    # Header with welcome message
    layout["header"].update(
        Panel(
            f"[bold green]{_('cli.welcome.title')}[/bold green]\n"
            f"[dim]© [Tauric Research](https://github.com/TauricResearch)[/dim]",
            title=_("cli.welcome.title"),
            border_style="green",
            padding=(1, 2),
            expand=True,
        )
    )

    # Progress panel showing agent status
    progress_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        box=box.SIMPLE_HEAD,  # Use simple header with horizontal lines
        title=None,  # Remove the redundant Progress title
        padding=(0, 2),  # Add horizontal padding
        expand=True,  # Make table expand to fill available space
    )
    progress_table.add_column(_("ui.table_headers.team"), style="cyan", justify="center", width=20)
    progress_table.add_column(_("ui.table_headers.agent"), style="green", justify="center", width=20)
    progress_table.add_column(_("ui.table_headers.status"), style="yellow", justify="center", width=20)

    # Group agents by team
    teams = {
        _("team.analyst"): [
            _("analyst_types.market"),
            _("analyst_types.social"),
            _("analyst_types.news"),
            _("analyst_types.fundamentals"),
        ],
        _("team.research"): [_("researcher.bull"), _("researcher.bear"), _("researcher.manager")],
        _("team.trading"): [_("ui.trader")],
        _("team.risk_management"): [
            _("agents.risk_analyst.risky"), 
            _("agents.risk_analyst.neutral"), 
            _("agents.risk_analyst.safe")
        ],
        _("team.portfolio_management"): [_("agents.risk_analyst.portfolio_manager")],
    }

    for team, agents in teams.items():
        # Add first agent with team name
        first_agent = agents[0]
        status = message_buffer.agent_status[first_agent]
        if status == "in_progress":
            spinner = Spinner(
                "dots", text=f"[blue]{_('status.in_progress')}[/blue]", style="bold cyan"
            )
            status_cell = spinner
        else:
            status_color = {
                "pending": "yellow",
                "completed": "green",
                "error": "red",
            }.get(status, "white")
            # Use translated status
            translated_status = get_translated_status(status)
            status_cell = f"[{status_color}]{translated_status}[/{status_color}]"
        progress_table.add_row(team, first_agent, status_cell)

        # Add remaining agents in team
        for agent in agents[1:]:
            status = message_buffer.agent_status[agent]
            if status == "in_progress":
                spinner = Spinner(
                    "dots", text=f"[blue]{_('status.in_progress')}[/blue]", style="bold cyan"
                )
                status_cell = spinner
            else:
                status_color = {
                    "pending": "yellow",
                    "completed": "green",
                    "error": "red",
                }.get(status, "white")
                # Use translated status
                translated_status = get_translated_status(status)
                status_cell = f"[{status_color}]{translated_status}[/{status_color}]"
            progress_table.add_row("", agent, status_cell)

        # Add horizontal line after each team
        progress_table.add_row("─" * 20, "─" * 20, "─" * 20, style="dim")

    layout["progress"].update(
        Panel(progress_table, title=_("ui.progress"), border_style="cyan", padding=(1, 2))
    )

    # Messages panel showing recent messages and tool calls
    messages_table = Table(
        show_header=True,
        header_style="bold magenta",
        show_footer=False,
        expand=True,  # Make table expand to fill available space
        box=box.MINIMAL,  # Use minimal box style for a lighter look
        show_lines=True,  # Keep horizontal lines
        padding=(0, 1),  # Add some padding between columns
    )
    messages_table.add_column(_("ui.table_headers.time"), style="cyan", width=8, justify="center")
    messages_table.add_column(_("ui.table_headers.type"), style="green", width=10, justify="center")
    messages_table.add_column(
        _("ui.table_headers.content"), style="white", no_wrap=False, ratio=1
    )  # Make content column expand

    # Combine tool calls and messages
    all_messages = []

    # Add tool calls
    for timestamp, tool_name, args in message_buffer.tool_calls:
        # Format tool call args for better display
        if isinstance(args, dict):
            # Format dictionary args with translated parameter names
            translated_args = []
            for k, v in args.items():
                # Try to translate parameter name
                param_key = f"ui.tool_params.{k}"
                translated_param = _(param_key)
                
                # If no translation found for basic param, try indicators subkey
                indicator_key = f"ui.tool_params.indicators.{k}"
                if translated_param == param_key:
                    translated_param = _(indicator_key)
                
                # If still no translation found, use original key
                if translated_param == indicator_key:
                    translated_param = k
                
                translated_args.append(f"{translated_param}: {v}")
            
            args_str = ", ".join(translated_args)
            if len(args_str) > 80:
                args_str = args_str[:77] + "..."
            # Translate tool name if available
            translated_tool_name = _(f"ui.tool_names.{tool_name}")
            if translated_tool_name == f"ui.tool_names.{tool_name}":
                translated_tool_name = tool_name
            tool_content = f"{translated_tool_name}: {args_str}"
        elif isinstance(args, str) and len(args) > 80:
            args = args[:77] + "..."
            # Translate tool name if available
            translated_tool_name = _(f"ui.tool_names.{tool_name}")
            if translated_tool_name == f"ui.tool_names.{tool_name}":
                translated_tool_name = tool_name
            tool_content = f"{translated_tool_name}: {args}"
        else:
            # Translate tool name if available
            translated_tool_name = _(f"ui.tool_names.{tool_name}")
            if translated_tool_name == f"ui.tool_names.{tool_name}":
                translated_tool_name = tool_name
            tool_content = f"{translated_tool_name}: {args}"
        all_messages.append((timestamp, _("ui.tool"), tool_content))

    # Add regular messages
    for timestamp, msg_type, content in message_buffer.messages:
        # Convert content to string if it's not already
        content_str = content
        if isinstance(content, list):
            # Handle list of content blocks (Anthropic format)
            text_parts = []
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text_parts.append(item.get('text', ''))
                    elif item.get('type') == 'tool_use':
                        text_parts.append(f"[{_('ui.tool')}: {item.get('name', 'unknown')}]")
                else:
                    text_parts.append(str(item))
            content_str = ' '.join(text_parts)
        elif not isinstance(content_str, str):
            content_str = str(content)
            
        # Truncate message content if too long
        if len(content_str) > 200:
            content_str = content_str[:197] + "..."
        all_messages.append((timestamp, msg_type, content_str))

    # Sort by timestamp
    all_messages.sort(key=lambda x: x[0])

    # Calculate how many messages we can show based on available space
    # Start with a reasonable number and adjust based on content length
    max_messages = 12  # Increased from 8 to better fill the space

    # Get the last N messages that will fit in the panel
    recent_messages = all_messages[-max_messages:]

    # Add messages to table
    for timestamp, msg_type, content in recent_messages:
        # Format content with word wrapping
        wrapped_content = Text(content, overflow="fold")
        messages_table.add_row(timestamp, msg_type, wrapped_content)

    if spinner_text:
        messages_table.add_row("", _("ui.spinner"), spinner_text)

    # Add a footer to indicate if messages were truncated
    if len(all_messages) > max_messages:
        messages_table.footer = (
            f"[dim]Showing last {max_messages} of {len(all_messages)} messages[/dim]"
        )

    layout["messages"].update(
        Panel(
            messages_table,
            title=_("ui.messages_tools"),
            border_style="blue",
            padding=(1, 2),
        )
    )

    # Analysis panel showing current report
    if message_buffer.current_report:
        layout["analysis"].update(
            Panel(
                Markdown(message_buffer.current_report),
                title=_("ui.current_report"),
                border_style="green",
                padding=(1, 2),
            )
        )
    else:
        layout["analysis"].update(
            Panel(
                f"[italic]{_('ui.waiting_for_report')}[/italic]",
                title=_("ui.current_report"),
                border_style="green",
                padding=(1, 2),
            )
        )

    # Footer with statistics
    tool_calls_count = len(message_buffer.tool_calls)
    llm_calls_count = sum(
        1 for _, msg_type, _ in message_buffer.messages if msg_type == "Reasoning"
    )
    reports_count = sum(
        1 for content in message_buffer.report_sections.values() if content is not None
    )

    stats_table = Table(show_header=False, box=None, padding=(0, 2), expand=True)
    stats_table.add_column("Stats", justify="center")
    stats_table.add_row(
        _("ui.stats.format", 
          tool_calls=f"{_('ui.stats.tool_calls')}: {tool_calls_count}", 
          llm_calls=f"{_('ui.stats.llm_calls')}: {llm_calls_count}", 
          reports=f"{_('ui.stats.generated_reports')}: {reports_count}")
    )

    layout["footer"].update(Panel(stats_table, border_style="grey50"))


def get_user_selections():
    """Get all user selections before starting the analysis display."""
    # Display ASCII art welcome message
    with open("./cli/static/welcome.txt", "r") as f:
        welcome_ascii = f.read()

    # Create welcome box content
    welcome_content = f"{welcome_ascii}\n"
    welcome_content += f"[bold green]{_('app.name')}: {_('app.description')} - CLI[/bold green]\n\n"
    welcome_content += f"[bold]{_('cli.welcome.workflow_title')}[/bold]\n"
    welcome_content += f"{_('cli.welcome.workflow_steps')}\n\n"
    welcome_content += (
        "[dim]Built by [Tauric Research](https://github.com/TauricResearch)[/dim]"
    )

    # Create and center the welcome box
    welcome_box = Panel(
        welcome_content,
        border_style="green",
        padding=(1, 2),
        title=_("cli.welcome.title"),
        subtitle=_("app.description"),
    )
    console.print(Align.center(welcome_box))
    console.print()  # Add a blank line after the welcome box

    # Create a boxed questionnaire for each step
    def create_question_box(title, prompt, default=None):
        box_content = f"[bold]{title}[/bold]\n"
        box_content += f"[dim]{prompt}[/dim]"
        if default:
            box_content += f"\n[dim]Default: {default}[/dim]"
        return Panel(box_content, border_style="blue", padding=(1, 2))

    # Step 1: Ticker symbol
    console.print(
        create_question_box(
            _("cli.step1.title"), _("cli.step1.prompt"), "SPY"
        )
    )
    selected_ticker = get_ticker()

    # Step 2: Analysis date
    default_date = datetime.datetime.now().strftime("%Y-%m-%d")
    console.print(
        create_question_box(
            _("cli.step2.title"),
            _("cli.step2.prompt"),
            default_date,
        )
    )
    analysis_date = get_analysis_date()

    # Step 3: Select analysts
    console.print(
        create_question_box(
            _("cli.step3.title"), _("cli.step3.prompt")
        )
    )
    selected_analysts = select_analysts()
    console.print(
        f"[green]{_('cli.selected_analysts')}:[/green] {', '.join(get_analyst_display_name(analyst) for analyst in selected_analysts)}"
    )

    # Step 4: Research depth
    console.print(
        create_question_box(
            _("cli.step4.title"), _("cli.step4.prompt")
        )
    )
    selected_research_depth = select_research_depth()

    # Step 5: OpenAI backend
    console.print(
        create_question_box(
            _("cli.step5.title"), _("cli.step5.prompt")
        )
    )
    selected_llm_provider, backend_url = select_llm_provider()
    
    # Step 6: Thinking agents
    console.print(
        create_question_box(
            _("cli.step6.title"), _("cli.step6.prompt")
        )
    )
    selected_shallow_thinker = select_shallow_thinking_agent(selected_llm_provider)
    selected_deep_thinker = select_deep_thinking_agent(selected_llm_provider)

    return {
        "ticker": selected_ticker,
        "analysis_date": analysis_date,
        "analysts": selected_analysts,
        "research_depth": selected_research_depth,
        "llm_provider": selected_llm_provider.lower(),
        "backend_url": backend_url,
        "shallow_thinker": selected_shallow_thinker,
        "deep_thinker": selected_deep_thinker,
    }


def get_ticker():
    """Get ticker symbol from user input."""
    return typer.prompt("", default="SPY")


def get_analysis_date():
    """Get the analysis date from user input."""
    while True:
        date_str = typer.prompt(
            "", default=datetime.datetime.now().strftime("%Y-%m-%d")
        )
        try:
            # Validate date format and ensure it's not in the future
            analysis_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            if analysis_date.date() > datetime.datetime.now().date():
                console.print(f"[red]{_('error.date_in_future')}[/red]")
                continue
            return date_str
        except ValueError:
            console.print(
                f"[red]{_('error.invalid_date_format')}[/red]"
            )


def display_complete_report(final_state):
    """Display the complete analysis report with team-based panels."""
    console.print(f"\n[bold green]{_('report.complete_title')}[/bold green]\n")

    # I. Analyst Team Reports
    analyst_reports = []

    # Market Analyst Report
    if final_state.get("market_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["market_report"]),
                title=_("report.sections.market_analysis"),
                border_style="blue",
                padding=(1, 2),
            )
        )

    # Social Analyst Report
    if final_state.get("sentiment_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["sentiment_report"]),
                title=_("report.sections.social_sentiment"),
                border_style="blue",
                padding=(1, 2),
            )
        )

    # News Analyst Report
    if final_state.get("news_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["news_report"]),
                title=_("report.sections.news_analysis"),
                border_style="blue",
                padding=(1, 2),
            )
        )

    # Fundamentals Analyst Report
    if final_state.get("fundamentals_report"):
        analyst_reports.append(
            Panel(
                Markdown(final_state["fundamentals_report"]),
                title=_("report.sections.fundamentals_analysis"),
                border_style="blue",
                padding=(1, 2),
            )
        )

    if analyst_reports:
        console.print(
            Panel(
                Columns(analyst_reports, equal=True, expand=True),
                title=_("report.sections.analyst_team_reports"),
                border_style="cyan",
                padding=(1, 2),
            )
        )

    # II. Research Team Reports
    if final_state.get("investment_debate_state"):
        research_reports = []
        debate_state = final_state["investment_debate_state"]

        # Bull Researcher Analysis
        if debate_state.get("bull_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bull_history"]),
                    title=_("researcher.bull"),
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Bear Researcher Analysis
        if debate_state.get("bear_history"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["bear_history"]),
                    title=_("researcher.bear"),
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Research Manager Decision
        if debate_state.get("judge_decision"):
            research_reports.append(
                Panel(
                    Markdown(debate_state["judge_decision"]),
                    title=_("researcher.manager"),
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if research_reports:
            console.print(
                Panel(
                    Columns(research_reports, equal=True, expand=True),
                    title=_("report.sections.research_team_decision"),
                    border_style="magenta",
                    padding=(1, 2),
                )
            )

    # III. Trading Team Reports
    if final_state.get("trader_investment_plan"):
        console.print(
            Panel(
                Panel(
                    Markdown(final_state["trader_investment_plan"]),
                    title=_("agents.trader.role"),
                    border_style="blue",
                    padding=(1, 2),
                ),
                title=_("report.sections.trading_team_plan"),
                border_style="yellow",
                padding=(1, 2),
            )
        )

    # IV. Risk Management Team Reports
    if final_state.get("risk_debate_state"):
        risk_reports = []
        risk_state = final_state["risk_debate_state"]

        # Aggressive (Risky) Analyst Analysis
        if risk_state.get("risky_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["risky_history"]),
                    title=_("agents.risk_analyst.risky"),
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Conservative (Safe) Analyst Analysis
        if risk_state.get("safe_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["safe_history"]),
                    title=_("agents.risk_analyst.safe"),
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Neutral Analyst Analysis
        if risk_state.get("neutral_history"):
            risk_reports.append(
                Panel(
                    Markdown(risk_state["neutral_history"]),
                    title=_("agents.risk_analyst.neutral"),
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        if risk_reports:
            console.print(
                Panel(
                    Columns(risk_reports, equal=True, expand=True),
                    title=_("report.sections.risk_management_decision"),
                    border_style="red",
                    padding=(1, 2),
                )
            )

        # V. Portfolio Manager Decision
        if risk_state.get("judge_decision"):
            console.print(
                Panel(
                    Panel(
                        Markdown(risk_state["judge_decision"]),
                        title=_("agents.risk_analyst.portfolio_manager"),
                        border_style="blue",
                        padding=(1, 2),
                    ),
                    title=_("report.sections.portfolio_manager_decision"),
                    border_style="green",
                    padding=(1, 2),
                )
            )


def update_research_team_status(status):
    """Update status for all research team members and trader."""
    research_team = [_("researcher.bull"), _("researcher.bear"), _("researcher.manager"), _("agents.trader.role")]
    for agent in research_team:
        message_buffer.update_agent_status(agent, status)

def extract_content_string(content):
    """Extract string content from various message formats."""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Handle Anthropic's list format
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    text_parts.append(f"[{_('ui.tool')}: {item.get('name', 'unknown')}]")
            else:
                text_parts.append(str(item))
        return ' '.join(text_parts)
    else:
        return str(content)

def run_analysis():
    # First get all user selections
    selections = get_user_selections()

    # Create config with selected research depth
    from tradingagents.config_manager import get_default_config_dict
    config = get_default_config_dict()
    config["max_debate_rounds"] = selections["research_depth"]
    config["max_risk_discuss_rounds"] = selections["research_depth"]
    config["quick_think_llm"] = selections["shallow_thinker"]
    config["deep_think_llm"] = selections["deep_thinker"]
    config["backend_url"] = selections["backend_url"]
    config["llm_provider"] = selections["llm_provider"].lower()

    # Initialize the graph (delayed import to avoid packaging issues)
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        graph = TradingAgentsGraph(
            [analyst.value for analyst in selections["analysts"]], config=config, debug=True
        )
    except ImportError as e:
        console.print(f"\n[red]❌ {_('error.import_failed', module='TradingAgentsGraph', error=e)}[/red]")
        console.print("[yellow]This may be due to dependency issues. Please check your environment.[/yellow]")
        return

    # Create result directory
    results_dir = Path(config["results_dir"]) / selections["ticker"] / selections["analysis_date"]
    results_dir.mkdir(parents=True, exist_ok=True)
    report_dir = results_dir / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    log_file = results_dir / "message_tool.log"
    log_file.touch(exist_ok=True)

    def save_message_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, message_type, content = obj.messages[-1]
            content = content.replace("\n", " ")  # Replace newlines with spaces
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [{message_type}] {content}\n")
        return wrapper
    
    def save_tool_call_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            timestamp, tool_name, args = obj.tool_calls[-1]
            args_str = ", ".join(f"{k}={v}" for k, v in args.items())
            with open(log_file, "a") as f:
                f.write(f"{timestamp} [Tool Call] {tool_name}({args_str})\n")
        return wrapper

    def save_report_section_decorator(obj, func_name):
        func = getattr(obj, func_name)
        @wraps(func)
        def wrapper(section_name, content):
            func(section_name, content)
            if section_name in obj.report_sections and obj.report_sections[section_name] is not None:
                content = obj.report_sections[section_name]
                if content:
                    file_name = f"{section_name}.md"
                    with open(report_dir / file_name, "w") as f:
                        f.write(content)
        return wrapper

    message_buffer.add_message = save_message_decorator(message_buffer, "add_message")
    message_buffer.add_tool_call = save_tool_call_decorator(message_buffer, "add_tool_call")
    message_buffer.update_report_section = save_report_section_decorator(message_buffer, "update_report_section")

    # Now start the display layout
    layout = create_layout()

    with Live(layout, refresh_per_second=4) as live:
        # Initial display
        update_display(layout)

        # Add initial messages
        message_buffer.add_message(_("ui.system"), f"{_('system.selected_ticker', ticker=selections['ticker'])}")
        message_buffer.add_message(
            _("ui.system"), f"{_('system.analysis_date', date=selections['analysis_date'])}"
        )
        message_buffer.add_message(
            _("ui.system"),
            f"{_('system.selected_analysts', analysts=', '.join(get_analyst_display_name(analyst) for analyst in selections['analysts']))}",
        )
        update_display(layout)

        # Reset agent statuses
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "pending")

        # Reset report sections
        for section in message_buffer.report_sections:
            message_buffer.report_sections[section] = None
        message_buffer.current_report = None
        message_buffer.final_report = None

        # Update agent status to in_progress for the first analyst
        first_analyst = f"{selections['analysts'][0].value} {_('ui.analyst')}"
        message_buffer.update_agent_status(first_analyst, "in_progress")
        update_display(layout)

        # Create spinner text
        spinner_text = (
            f"{_('ui.analyzing', ticker=selections['ticker'], date=selections['analysis_date'])}..."
        )
        update_display(layout, spinner_text)

        # Initialize state and get graph args
        init_agent_state = graph.propagator.create_initial_state(
            selections["ticker"], selections["analysis_date"]
        )
        args = graph.propagator.get_graph_args()

        # Stream the analysis
        trace = []
        for chunk in graph.graph.stream(init_agent_state, **args):
            if len(chunk["messages"]) > 0:
                # Get the last message from the chunk
                last_message = chunk["messages"][-1]

                # Extract message content and type
                if hasattr(last_message, "content"):
                    content = extract_content_string(last_message.content)  # Use the helper function
                    msg_type = _("ui.reasoning")
                else:
                    content = str(last_message)
                    msg_type = _("ui.system")

                # Translate error messages if needed
                if content.startswith("Error:"):
                    content = content.replace("Error:", _("error.general_error"))
                elif content.startswith("AttributeError:"):
                    content = content.replace("AttributeError:", _("error.attribute_error"))
                elif content.startswith("TypeError:"):
                    content = content.replace("TypeError:", _("error.type_error"))
                elif content.startswith("NameError:"):
                    content = content.replace("NameError:", _("error.name_error"))
                elif content.startswith("RuntimeError:"):
                    content = content.replace("RuntimeError:", _("error.runtime_error"))
                
                # Translate common error messages
                content = content.replace("Please fix your mistakes.", _("error.fix_mistakes"))

                # Add message to buffer
                message_buffer.add_message(msg_type, content)                

                # If it's a tool call, add it to tool calls
                if hasattr(last_message, "tool_calls"):
                    for tool_call in last_message.tool_calls:
                        # Handle both dictionary and object tool calls
                        if isinstance(tool_call, dict):
                            message_buffer.add_tool_call(
                                tool_call["name"], tool_call["args"]
                            )
                        else:
                            message_buffer.add_tool_call(tool_call.name, tool_call.args)

                # Update reports and agent status based on chunk content
                # Analyst Team Reports
                if "market_report" in chunk and chunk["market_report"]:
                    message_buffer.update_report_section(
                        "market_report", chunk["market_report"]
                    )
                    message_buffer.update_agent_status(_("analyst_types.market"), "completed")
                    # Set next analyst to in_progress
                    if "social" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            _("analyst_types.social"), "in_progress"
                        )

                if "sentiment_report" in chunk and chunk["sentiment_report"]:
                    message_buffer.update_report_section(
                        "sentiment_report", chunk["sentiment_report"]
                    )
                    message_buffer.update_agent_status(_("analyst_types.social"), "completed")
                    # Set next analyst to in_progress
                    if "news" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            _("analyst_types.news"), "in_progress"
                        )

                if "news_report" in chunk and chunk["news_report"]:
                    message_buffer.update_report_section(
                        "news_report", chunk["news_report"]
                    )
                    message_buffer.update_agent_status(_("analyst_types.news"), "completed")
                    # Set next analyst to in_progress
                    if "fundamentals" in selections["analysts"]:
                        message_buffer.update_agent_status(
                            _("analyst_types.fundamentals"), "in_progress"
                        )

                if "fundamentals_report" in chunk and chunk["fundamentals_report"]:
                    message_buffer.update_report_section(
                        "fundamentals_report", chunk["fundamentals_report"]
                    )
                    message_buffer.update_agent_status(
                        _("analyst_types.fundamentals"), "completed"
                    )
                    # Set all research team members to in_progress
                    update_research_team_status("in_progress")

                # Research Team - Handle Investment Debate State
                if (
                    "investment_debate_state" in chunk
                    and chunk["investment_debate_state"]
                ):
                    debate_state = chunk["investment_debate_state"]

                    # Update Bull Researcher status and report
                    if "bull_history" in debate_state and debate_state["bull_history"]:
                        # Keep all research team members in progress
                        update_research_team_status("in_progress")
                        # Extract latest bull response
                        bull_responses = debate_state["bull_history"].split("\n")
                        latest_bull = bull_responses[-1] if bull_responses else ""
                        if latest_bull:
                            message_buffer.add_message(_("ui.reasoning"), latest_bull)
                            # Update research report with bull's latest analysis
                            message_buffer.update_report_section(
                                "investment_plan",
                                f"### {_('researcher.bull_analysis')}\n{latest_bull}",
                            )

                    # Update Bear Researcher status and report
                    if "bear_history" in debate_state and debate_state["bear_history"]:
                        # Keep all research team members in progress
                        update_research_team_status("in_progress")
                        # Extract latest bear response
                        bear_responses = debate_state["bear_history"].split("\n")
                        latest_bear = bear_responses[-1] if bear_responses else ""
                        if latest_bear:
                            message_buffer.add_message(_("ui.reasoning"), latest_bear)
                            # Update research report with bear's latest analysis
                            message_buffer.update_report_section(
                                "investment_plan",
                                f"{message_buffer.report_sections['investment_plan']}\n\n### {_('researcher.bear_analysis')}\n{latest_bear}",
                            )

                    # Update Research Manager status and final decision
                    if (
                        "judge_decision" in debate_state
                        and debate_state["judge_decision"]
                    ):
                        # Keep all research team members in progress until final decision
                        update_research_team_status("in_progress")
                        message_buffer.add_message(
                            _("ui.reasoning"),
                            f"Research Manager: {debate_state['judge_decision']}",
                        )
                        # Update research report with final decision
                        message_buffer.update_report_section(
                            "investment_plan",
                            f"{message_buffer.report_sections['investment_plan']}\n\n### {_('researcher.manager_decision')}\n{debate_state['judge_decision']}",
                        )
                        # Mark all research team members as completed
                        update_research_team_status("completed")
                        # Set first risk analyst to in_progress
                        message_buffer.update_agent_status(
                            _("agents.risk_analyst.risky"), "in_progress"
                        )

                # Trading Team
                if (
                    "trader_investment_plan" in chunk
                    and chunk["trader_investment_plan"]
                ):
                    message_buffer.update_report_section(
                        "trader_investment_plan", chunk["trader_investment_plan"]
                    )
                    # Set first risk analyst to in_progress
                    message_buffer.update_agent_status(_("agents.risk_analyst.risky"), "in_progress")

                # Risk Management Team - Handle Risk Debate State
                if "risk_debate_state" in chunk and chunk["risk_debate_state"]:
                    risk_state = chunk["risk_debate_state"]

                    # Update Risky Analyst status and report
                    if (
                        "current_risky_response" in risk_state
                        and risk_state["current_risky_response"]
                    ):
                        message_buffer.update_agent_status(
                            _("agents.risk_analyst.risky"), "in_progress"
                        )
                        message_buffer.add_message(
                            _("ui.reasoning"),
                            f"{_('agents.risk_analyst.risky')}: {risk_state['current_risky_response']}",
                        )
                        # Update risk report with risky analyst's latest analysis only
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### {_('agents.risk_analyst.risky')} {_('report.analysis')}\n{risk_state['current_risky_response']}",
                        )

                    # Update Safe Analyst status and report
                    if (
                        "current_safe_response" in risk_state
                        and risk_state["current_safe_response"]
                    ):
                        message_buffer.update_agent_status(
                            _("agents.risk_analyst.safe"), "in_progress"
                        )
                        message_buffer.add_message(
                            _("ui.reasoning"),
                            f"{_('agents.risk_analyst.safe')}: {risk_state['current_safe_response']}",
                        )
                        # Update risk report with safe analyst's latest analysis only
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### {_('agents.risk_analyst.safe')} {_('report.analysis')}\n{risk_state['current_safe_response']}",
                        )

                    # Update Neutral Analyst status and report
                    if (
                        "current_neutral_response" in risk_state
                        and risk_state["current_neutral_response"]
                    ):
                        message_buffer.update_agent_status(
                            _("agents.risk_analyst.neutral"), "in_progress"
                        )
                        message_buffer.add_message(
                            _("ui.reasoning"),
                            f"{_('agents.risk_analyst.neutral')}: {risk_state['current_neutral_response']}",
                        )
                        # Update risk report with neutral analyst's latest analysis only
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### {_('agents.risk_analyst.neutral')} {_('report.analysis')}\n{risk_state['current_neutral_response']}",
                        )

                    # Update Portfolio Manager status and final decision
                    if "judge_decision" in risk_state and risk_state["judge_decision"]:
                        message_buffer.update_agent_status(
                            _("agents.risk_analyst.portfolio_manager"), "in_progress"
                        )
                        message_buffer.add_message(
                            _("ui.reasoning"),
                            f"{_('agents.risk_analyst.portfolio_manager')}: {risk_state['judge_decision']}",
                        )
                        # Update risk report with final decision only
                        message_buffer.update_report_section(
                            "final_trade_decision",
                            f"### {_('agents.risk_analyst.portfolio_manager')} {_('report.decision')}\n{risk_state['judge_decision']}",
                        )
                        # Mark risk analysts as completed
                        message_buffer.update_agent_status(_("agents.risk_analyst.risky"), "completed")
                        message_buffer.update_agent_status(_("agents.risk_analyst.safe"), "completed")
                        message_buffer.update_agent_status(
                            _("agents.risk_analyst.neutral"), "completed"
                        )
                        message_buffer.update_agent_status(
                            _("agents.risk_analyst.portfolio_manager"), "completed"
                        )

                # Update the display
                update_display(layout)

            trace.append(chunk)

        # Get final state and decision
        final_state = trace[-1]
        decision = graph.process_signal(final_state["final_trade_decision"])

        # Update all agent statuses to completed
        for agent in message_buffer.agent_status:
            message_buffer.update_agent_status(agent, "completed")

        message_buffer.add_message(
            _("ui.analysis"), f"{_('system.completed', date=selections['analysis_date'])}"
        )

        # Update final report sections
        for section in message_buffer.report_sections.keys():
            if section in final_state:
                message_buffer.update_report_section(section, final_state[section])

        # Display the complete final report
        display_complete_report(final_state)

        update_display(layout)


@app.command()
def analyze():
    run_analysis()


def check_dependencies():
    """Check dependencies before starting the CLI."""
    try:
        # Quick check of critical packages
        critical_packages = ['packaging', 'certifi', 'requests', 'langchain']
        missing_packages = []
        
        for package in critical_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            console.print(f"\n[red]❌ {_('error.missing_dependencies', dependencies=', '.join(missing_packages))}[/red]")
            console.print(f"[yellow]{_('dependency.check_running')}[/yellow]")
            DependencyChecker.print_dependency_report()
            return False
        
        return True
    except Exception as e:
        console.print(f"[red]❌ {_('error.dependency_check_failed', error=e)}[/red]")
        return False


if __name__ == "__main__":
    if check_dependencies():
        app()
