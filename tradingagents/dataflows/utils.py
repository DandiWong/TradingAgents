import os
import json
import pandas as pd
from datetime import date, timedelta, datetime
from typing import Annotated

# Import i18n support
try:
    from ..i18n import _
    from ..config_manager import ConfigManager
except ImportError:
    # Fallback if i18n is not available
    def _(key: str, **kwargs) -> str:
        return key.format(**kwargs) if kwargs else key

SavePathType = Annotated[str, "File path to save data. If None, data is not saved."]

def save_output(data: pd.DataFrame, tag: str, save_path: SavePathType = None) -> None:
    if save_path:
        data.to_csv(save_path)
        # Initialize i18n if available
        try:
            config_manager = ConfigManager()
            current_locale = config_manager.get_locale()
            from ..i18n import set_locale
            set_locale(current_locale)
        except:
            pass
        print(_("dataflow.tag_saved", tag=tag, path=save_path))


def get_current_date():
    return date.today().strftime("%Y-%m-%d")


def decorate_all_methods(decorator):
    def class_decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            if callable(attr_value):
                setattr(cls, attr_name, decorator(attr_value))
        return cls

    return class_decorator


def get_next_weekday(date):

    if not isinstance(date, datetime):
        date = datetime.strptime(date, "%Y-%m-%d")

    if date.weekday() >= 5:
        days_to_add = 7 - date.weekday()
        next_weekday = date + timedelta(days=days_to_add)
        return next_weekday
    else:
        return date
