# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: tool_datetime_utils.py 
@info: 日期时间工具
"""

from datetime import datetime, timedelta

def tool_get_current_time():
    """
    获取当前时间。

    :return: 当前时间的格式为YYYY-MM-DD HH:MM:SS。

    # 使用示例
    # current_time = tool_get_current_time()
    # print("当前时间:", current_time)
    """
    current_time = datetime.now()
    return current_time.strftime("%Y-%m-%d %H:%M:%S")

def tool_get_current_date():
    """
    获取当前日期。

    :return: 当前日期的格式为YYYY-MM-DD。

    # 使用示例
    # current_date = tool_get_current_date()
    # print("当前日期:", current_date)
    """
    current_date = datetime.now()
    return current_date.strftime("%Y-%m-%d")

def tool_get_current_and_future_dates(days=7):
    """
    计算当前日期和未来指定天数后的日期。

    :param days: 从当前日期起的天数，默认为7天。
    :return: 当前日期和未来日期的字符串（格式：YYYY-MM-DD）。

    # 使用示例
    # current_date, future_date = tool_get_current_and_future_dates()
    # print("当前日期:", current_date)
    # print("7天后日期:", future_date)
    """
    current_date = datetime.now()
    future_date = current_date + timedelta(days=days)

    return current_date.strftime("%Y-%m-%d"), future_date.strftime("%Y-%m-%d")


