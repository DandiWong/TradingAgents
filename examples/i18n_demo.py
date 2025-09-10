#!/usr/bin/env python3
"""
TradingAgents 动态语言切换演示

这个示例展示了如何在TradingAgents中使用动态语言切换功能。
所有的提示词、错误消息、UI文本都会根据配置文件中的语言设置自动切换。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.i18n import _, set_locale, get_locale
from tradingagents.config_manager import ConfigManager

def demo_language_switching():
    """演示动态语言切换功能"""
    
    print("TradingAgents 动态语言切换演示")
    print("=" * 50)
    
    # 1. 基于配置文件的自动语言设置
    config_manager = ConfigManager()
    current_locale = config_manager.get_locale()
    set_locale(current_locale)
    
    print(f"配置文件中的语言设置: {current_locale}")
    print(f"应用名称: {_('app.name')}")
    print(f"应用描述: {_('app.description')}")
    print()
    
    # 2. 演示代理提示词的语言切换
    print("代理提示词语言切换演示:")
    print("-" * 30)
    
    # 市场分析师提示词
    market_analyst_role = _('agents.market_analyst.role')
    print(f"市场分析师角色 ({get_locale()}): {market_analyst_role[:100]}...")
    print()
    
    # 3. 演示错误消息的语言切换
    print("错误消息语言切换演示:")
    print("-" * 30)
    
    error_msg = _('error.missing_dependencies', packages='numpy, pandas, yfinance')
    print(f"依赖错误 ({get_locale()}): {error_msg}")
    
    config_error = _('config.load_warning', path='/path/to/config.json', error='文件不存在')
    print(f"配置错误 ({get_locale()}): {config_error}")
    print()
    
    # 4. 演示工具名称的语言切换
    print("工具名称语言切换演示:")
    print("-" * 30)
    
    tool_names = [
        'ui.tool_names.get_YFin_data',
        'ui.tool_names.get_google_news',
        'ui.tool_names.get_reddit_data_online',
        'ui.tool_names.get_stockstats_indicators_report_online'
    ]
    
    for tool_key in tool_names:
        tool_name = _(tool_key)
        print(f"  • {tool_name}")
    
    print()
    print("演示完成！")
    print()
    print("使用方法:")
    print("1. 在 config.json 中设置 'language': 'zh-CN' 或 'en-US'")
    print("2. 所有代理提示词、错误消息、UI文本会自动切换语言")
    print("3. 支持的语言: 中文(zh-CN), 英文(en-US)")

if __name__ == "__main__":
    demo_language_switching()