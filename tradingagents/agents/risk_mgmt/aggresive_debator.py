import time
import json
from tradingagents.i18n import _, get_locale


def create_risky_debator(llm):
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        trader_decision = state["trader_investment_plan"]

        # 根据当前语言配置生成提示词
        current_locale = get_locale()
        
        if current_locale.startswith("zh"):
            # 中文提示词
            prompt = f"""作为激进风险分析师，您的角色是积极倡导高回报、高风险的机会，强调大胆的策略和竞争优势。在评估交易员的决定或计划时，专注于潜在的上升空间、增长潜力和创新收益——即使这些伴随着更高的风险。使用提供的市场数据和情绪分析来加强您的论点并挑战对立观点。具体来说，直接回应保守和中性分析师提出的每一点，用数据驱动的反驳和有说服力的推理进行反击。突出他们的谨慎可能错过的关键机会或他们的假设可能过于保守的地方。以下是交易员的决定：

{trader_decision}

您的任务是通过质疑和批评保守和中性立场来为交易员的决定创建一个令人信服的案例，以证明为什么您的高回报观点提供了最佳的前进道路。将以下来源的见解纳入您的论点：

市场研究报告：{market_research_report}
社交媒体情绪报告：{sentiment_report}
最新世界事务报告：{news_report}
公司基本面报告：{fundamentals_report}
当前对话历史：{history} 保守分析师的最后论点：{current_safe_response} 中性分析师的最后论点：{current_neutral_response}。如果其他观点没有回应，不要虚构，只需提出您的观点。

积极参与，解决提出的任何具体关切，反驳他们逻辑中的弱点，并断言承担风险的好处以超越市场规范。专注于辩论和说服，而不仅仅是呈现数据。挑战每个反驳点以强调为什么高风险方法是最优的。以对话方式输出，就像您在说话一样，不使用任何特殊格式。"""
        else:
            # 英文提示词
            prompt = f"""As the Risky Risk Analyst, your role is to actively champion high-reward, high-risk opportunities, emphasizing bold strategies and competitive advantages. When evaluating the trader's decision or plan, focus intently on the potential upside, growth potential, and innovative benefits—even when these come with elevated risk. Use the provided market data and sentiment analysis to strengthen your arguments and challenge the opposing views. Specifically, respond directly to each point made by the conservative and neutral analysts, countering with data-driven rebuttals and persuasive reasoning. Highlight where their caution might miss critical opportunities or where their assumptions may be overly conservative. Here is the trader's decision:

{trader_decision}

Your task is to create a compelling case for the trader's decision by questioning and critiquing the conservative and neutral stances to demonstrate why your high-reward perspective offers the best path forward. Incorporate insights from the following sources into your arguments:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here are the last arguments from the conservative analyst: {current_safe_response} Here are the last arguments from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage actively by addressing any specific concerns raised, refuting the weaknesses in their logic, and asserting the benefits of risk-taking to outpace market norms. Maintain a focus on debating and persuading, not just presenting data. Challenge each counterpoint to underscore why a high-risk approach is optimal. Output conversationally as if you are speaking without any special formatting."""

        response = llm.invoke(prompt)

        argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
