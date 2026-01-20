# -*- coding: utf-8 -*-

import threading
import time

from oddagent.config_loader import config
from oddagent.odd_agent_logger import logger
from oddagent.tools.tool_executer_meeting import MeetingConfig, MeetingExecuter

class OddAgentScheduler(threading.Thread):
    """
    Odd Agent Scheduler
    定时任务：
    1. 检查登录状态
    2. 检查会议是否过期
    3. 检查会议是否结束
    4. 检查会议是否开始
    5. 检查会议是否正在进行
    6. 检查会议是否即将开始
    7. 检查会议是否即将结束
    8. 同步会议成员列表
    """
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()
        self.meeting_assistant = MeetingExecuter(meeting_config=MeetingConfig())
        pass

    def run(self):
        while not self._stop_event.is_set():
            if config.API_FAKE_API_RESULT == 0:
                # 1. 检查登录状态
                if not self.meeting_assistant.is_login():
                    logger.info("登录状态失效，重新登录")
                    self.meeting_assistant.login()
                    logger.debug("登录成功")
            time.sleep(1)

    def stop(self):
        # 设置停止标志，通知线程退出循环
        self._stop_event.set()