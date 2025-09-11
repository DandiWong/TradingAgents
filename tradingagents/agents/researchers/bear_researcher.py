from langchain_core.messages import AIMessage
import time
import json
from tradingagents.i18n import _, get_locale


def create_bear_researcher(llm, memory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

        current_response = investment_debate_state.get("current_response", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        # 根据当前语言配置生成提示词
        current_locale = get_locale()
        
        system_role = _("agents.bear_researcher.role")
        
        if current_locale.startswith("zh"):
            # 中文提示词
            focus_areas = f"""
{_("agents.bear_researcher.focus_areas.risks")} 突出市场饱和、财务不稳定或宏观经济威胁等可能阻碍股票表现的因素。
{_("agents.bear_researcher.focus_areas.weaknesses")} 强调市场地位较弱、创新下降或竞争对手威胁等弱点。
{_("agents.bear_researcher.focus_areas.concerns")} 使用财务数据、市场趋势或最新不利新闻的证据来支持您的立场。
{_("agents.bear_researcher.focus_areas.bull_counterpoints")} 用具体数据和合理推理批判性分析牛市论点，暴露弱点或过度乐观的假设。
{_("agents.bear_researcher.focus_areas.engagement")} 以对话风格呈现您的论点，直接与牛市分析师的观点互动，有效辩论而不仅仅是列出事实。
"""

            prompt = f"""{system_role}

重点关注领域：{focus_areas}

可用资源：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论对话历史：{history}
最后的牛市论点：{current_response}
类似情况的反思和经验教训：{past_memory_str}

使用这些信息提出令人信服的熊市论点，反驳牛市主张，并进行动态辩论以展示投资该股票的风险和弱点。您还必须处理反思并从过去的经验和错误中学习。
"""
        else:
            # 英文提示词
            focus_areas = f"""
{_("agents.bear_researcher.focus_areas.risks")} Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder the stock's performance.
{_("agents.bear_researcher.focus_areas.weaknesses")} Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors.
{_("agents.bear_researcher.focus_areas.concerns")} Use evidence from financial data, market trends, or recent adverse news to support your position.
{_("agents.bear_researcher.focus_areas.bull_counterpoints")} Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
{_("agents.bear_researcher.focus_areas.engagement")} Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.
"""

            prompt = f"""{system_role}

Key points to focus on:{focus_areas}

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the stock. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
