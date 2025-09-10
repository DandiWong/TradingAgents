from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.i18n import _


def create_market_analyst(llm, toolkit):

    def market_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [
                toolkit.get_YFin_data_online,
                toolkit.get_stockstats_indicators_report_online,
            ]
        else:
            tools = [
                toolkit.get_YFin_data,
                toolkit.get_stockstats_indicators_report,
            ]

        system_message = (
            _("agents.market_analyst.role") + "\n\n" +
            _("agents.market_analyst.indicators_description") + "\n\n" +
            _("agents.market_analyst.select_indicators_instruction") + "\n\n" +
            _("agents.market_analyst.report_instruction")
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    _("agents.system.base_instruction") +
                    " You have access to the following tools: {tool_names}.\n{system_message}" +
                    _("agents.system.reference_info", current_date=current_date, ticker=ticker)
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
