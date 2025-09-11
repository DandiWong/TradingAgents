from langchain_core.messages import AIMessage
import time
import json
from tradingagents.i18n import _, get_locale


def create_bull_researcher(llm, memory):
    def bull_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

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
        
        system_role = _("agents.bull_researcher.role")
        
        if current_locale.startswith("zh"):
            # 中文提示词
            focus_areas = f"""
{_("agents.bull_researcher.focus_areas.growth")} 突出公司的市场机会、收入预测和可扩展性。
{_("agents.bull_researcher.focus_areas.advantages")} 强调独特产品、强势品牌或主导市场地位等因素。
{_("agents.bull_researcher.focus_areas.indicators")} 使用财务健康状况、行业趋势和最新正面新闻作为证据。
{_("agents.bull_researcher.focus_areas.counterpoints")} 用具体数据和合理推理批判性分析熊市论点，彻底解决担忧并说明为什么牛市观点更有说服力。
{_("agents.bull_researcher.focus_areas.engagement")} 以对话风格呈现您的论点，直接与熊市分析师的观点互动，有效辩论而不仅仅是列出数据。
"""

            prompt = f"""{system_role}

重点关注领域：{focus_areas}

可用资源：
市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务新闻：{news_report}
公司基本面报告：{fundamentals_report}
辩论对话历史：{history}
最后的熊市论点：{current_response}
类似情况的反思和经验教训：{past_memory_str}

使用这些信息提出令人信服的牛市论点，反驳熊市担忧，并进行动态辩论以展示牛市立场的优势。您还必须处理反思并从过去的经验和错误中学习。
"""
        else:
            # 英文提示词
            focus_areas = f"""
{_("agents.bull_researcher.focus_areas.growth")} Highlight the company's market opportunities, revenue projections, and scalability.
{_("agents.bull_researcher.focus_areas.advantages")} Emphasize factors like unique products, strong branding, or dominant market positioning.
{_("agents.bull_researcher.focus_areas.indicators")} Use financial health, industry trends, and recent positive news as evidence.
{_("agents.bull_researcher.focus_areas.counterpoints")} Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
{_("agents.bull_researcher.focus_areas.engagement")} Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.
"""

            prompt = f"""{system_role}

Key points to focus on:{focus_areas}

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}

Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""

        response = llm.invoke(prompt)

        argument = f"{_('team.roles.bull_researcher')}: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
