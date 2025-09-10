"""
国际化(i18n)模块 - TradingAgents

提供完整的多语言支持，包括用户界面、错误消息、代理系统消息等的翻译管理。
"""

import json
import os
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging


class I18nManager:
    """国际化管理器 - 处理应用程序的多语言支持"""
    
    def __init__(self, locale_dir: Optional[str] = None, default_locale: str = "en-US"):
        """
        初始化i18n管理器
        
        Args:
            locale_dir: 语言文件目录路径
            default_locale: 默认语言
        """
        self.locale_dir = Path(locale_dir) if locale_dir else Path(__file__).parent / "locales"
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations = {}
        self.fallback_translations = {}
        
        # 确保语言文件目录存在
        self.locale_dir.mkdir(exist_ok=True)
        
        # 加载翻译
        self._load_translations()
    
    def _load_translations(self):
        """加载所有翻译文件"""
        try:
            # 加载默认语言（英语）
            default_file = self.locale_dir / f"{self.default_locale}.json"
            if default_file.exists():
                with open(default_file, 'r', encoding='utf-8') as f:
                    self.fallback_translations = json.load(f)
            
            # 加载当前语言
            current_file = self.locale_dir / f"{self.current_locale}.json"
            if current_file.exists():
                with open(current_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            else:
                self.translations = self.fallback_translations.copy()
                
        except Exception as e:
            logging.error(f"Failed to load translations: {e}")
            self.translations = self.fallback_translations.copy()
    
    def set_locale(self, locale: str):
        """
        设置当前语言
        
        Args:
            locale: 语言代码 (如 "zh-CN", "en-US")
        """
        if locale != self.current_locale:
            self.current_locale = locale
            self._load_translations()
    
    def get_locale(self) -> str:
        """获取当前语言"""
        return self.current_locale
    
    def get_available_locales(self) -> list:
        """获取可用的语言列表"""
        locales = []
        if self.locale_dir.exists():
            for file in self.locale_dir.glob("*.json"):
                locales.append(file.stem)
        return sorted(locales)
    
    def translate(self, key: str, **kwargs) -> str:
        """
        翻译文本
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        # 尝试从当前语言获取翻译
        translation = self._get_nested_value(self.translations, key)
        
        # 如果当前语言没有翻译，尝试从默认语言获取
        if translation is None:
            translation = self._get_nested_value(self.fallback_translations, key)
        
        # 如果都没有翻译，返回键名
        if translation is None:
            translation = key
        
        # 格式化文本
        try:
            return translation.format(**kwargs) if kwargs else translation
        except (KeyError, ValueError):
            return translation
    
    def _get_nested_value(self, data: Dict, key: str) -> Optional[str]:
        """获取嵌套字典中的值"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current if isinstance(current, str) else None
    
    def ngettext(self, singular: str, plural: str, count: int, **kwargs) -> str:
        """
        处理复数形式的翻译
        
        Args:
            singular: 单数形式
            plural: 复数形式
            count: 数量
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        key = singular if count == 1 else plural
        translation = self.translate(key, count=count, **kwargs)
        return translation


# 全局i18n管理器实例
_i18n_manager = None


def init_i18n(locale_dir: Optional[str] = None, default_locale: str = "en-US") -> I18nManager:
    """初始化全局i18n管理器"""
    global _i18n_manager
    _i18n_manager = I18nManager(locale_dir, default_locale)
    return _i18n_manager


def get_i18n_manager() -> I18nManager:
    """获取全局i18n管理器"""
    global _i18n_manager
    if _i18n_manager is None:
        _i18n_manager = init_i18n()
    return _i18n_manager


def _(key: str, **kwargs) -> str:
    """
    翻译函数的简写形式
    
    Args:
        key: 翻译键
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    return get_i18n_manager().translate(key, **kwargs)


def ngettext(singular: str, plural: str, count: int, **kwargs) -> str:
    """
    处理复数形式的翻译函数
    
    Args:
        singular: 单数形式
        plural: 复数形式
        count: 数量
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    return get_i18n_manager().ngettext(singular, plural, count, **kwargs)


def set_locale(locale: str):
    """设置当前语言"""
    get_i18n_manager().set_locale(locale)


def get_locale() -> str:
    """获取当前语言"""
    return get_i18n_manager().get_locale()


def get_available_locales() -> list:
    """获取可用的语言列表"""
    return get_i18n_manager().get_available_locales()