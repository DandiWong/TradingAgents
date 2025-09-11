import functools
import time
import json
from tradingagents.i18n import _, get_locale


def create_trader(llm, memory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "No past memories found."

        # 根据当前语言配置生成提示词
        current_locale = get_locale()
        
        system_role = _("agents.trader.role")
        plan_intro = _("agents.trader.plan_intro").format(company_name=company_name)
        
        if current_locale.startswith("zh"):
            # 中文提示词
            context_content = _("agents.trader.context_content", investment_plan=investment_plan)
            system_instruction = _("agents.trader.system_instruction", past_memory_str=past_memory_str)
            context = {
                "role": "user",
                "content": f"{plan_intro}\n\n{context_content}",
            }

            messages = [
                {
                    "role": "system",
                    "content": f"{system_role} {system_instruction}",
                },
                context,
            ]
        else:
            # 英文提示词
            context_content = _("agents.trader.context_content", company_name=company_name, investment_plan=investment_plan)
            system_instruction = _("agents.trader.system_instruction", past_memory_str=past_memory_str)
            context = {
                "role": "user",
                "content": context_content,
            }

            messages = [
                {
                    "role": "system",
                    "content": f"{system_role} {system_instruction}",
                },
                context,
            ]

        result = llm.invoke(messages)

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
