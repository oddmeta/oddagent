# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: logger.py 
@info: 日志配置
"""

import logging
from logging import handlers

from oddagent.config_loader import config


def _logging():
    FORMAT = "%(asctime)s %(levelname)s %(filename)s:%(lineno)s (%(process)s-%(thread)s) - %(message)s "
    DATE = '%Y-%m-%d %H:%M:%S'

    format = logging.Formatter(FORMAT, DATE)

    import os
    if not os.path.exists(config.LOG_PATH):
        os.makedirs(config.LOG_PATH)

    logfile = config.LOG_PATH + config.LOG_FILE
    
    log = logging.getLogger(logfile)

    th = handlers.TimedRotatingFileHandler(filename=logfile, when='MIDNIGHT', backupCount=10, encoding='utf-8', delay=True)
    th.setFormatter(format)
    log.addHandler(th)

    stdout = logging.StreamHandler()
    stdout.setFormatter(format)
    log.addHandler(stdout)

    if config.DEBUG:
        # 移除重复添加的StreamHandler
        enableProtoPrint = False
        if enableProtoPrint:
            log.setLevel(logging.DEBUG)

    log.setLevel(config.LOG_LEVEL)
    
    return log


logger = _logging()