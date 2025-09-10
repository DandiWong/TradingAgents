import functools
import time
import json
from tradingagents.i18n import _


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
        from tradingagents.i18n import get_locale
        current_locale = get_locale()
        
        system_role = _("agents.trader.role")
        plan_intro = _("agents.trader.plan_intro").format(company_name=company_name)
        
        if current_locale.startswith("zh"):
            # 中文提示词
            context = {
                "role": "user",
                "content": f"{plan_intro}\n\n建议的投资计划：{investment_plan}\n\n利用这些见解做出明智和战略性的决定。",
            }

            messages = [
                {
                    "role": "system",
                    "content": f"""{system_role} 根据您的分析，提供买入、卖出或持有的具体建议。以坚定的决定结束，并始终以"最终交易提案：**买入/持有/卖出**"结束您的回应以确认您的建议。不要忘记利用过去决策的经验教训来从错误中学习。以下是您在类似情况下交易的一些反思和经验教训：{past_memory_str}""",
                },
                context,
            ]
        else:
            # 英文提示词
            context = {
                "role": "user",
                "content": f"Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. Use this plan as a foundation for evaluating your next trading decision.\n\nProposed Investment Plan: {investment_plan}\n\nLeverage these insights to make an informed and strategic decision.",
            }

            messages = [
                {
                    "role": "system",
                    "content": f"""{system_role} Based on your analysis, provide a specific recommendation to buy, sell, or hold. End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. Do not forget to utilize lessons from past decisions to learn from your mistakes. Here is some reflections from similar situations you traded in and the lessons learned: {past_memory_str}""",
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
