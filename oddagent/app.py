# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: main_server.py 
@info: 消息模版
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
import werkzeug.utils
from datetime import timedelta
import signal
import sys
import argparse

from oddagent.config_loader import ConfigLoader
from oddagent.logic.schedule_task import OddAgentScheduler
from oddagent.logic.odd_agent_error import OddException, odd_exception_handler

# 创建命令行参数解析器
import argparse
import sys
from oddagent.config_loader import ConfigLoader, config

# 添加命令行参数解析
parser = argparse.ArgumentParser(description='OddAgent 服务启动脚本')
parser.add_argument('-c', '--config', type=str, help='指定配置文件路径')
args = parser.parse_args()

# 如果指定了配置文件，重新加载配置
if args.config:
    # 替换全局配置对象
    sys.modules['oddagent.config_loader'].config = ConfigLoader.load_config(args.config)

# 导入其他模块（必须在配置加载后进行）
from flask import Flask
from werkzeug.utils import import_string
from werkzeug.serving import run_simple
import threading
import signal
from datetime import timedelta

# 全局保存线程引用
schedule_task = None

def signal_handler(sig, frame):
    """处理终止信号，确保线程正确停止"""
    print("收到终止信号，正在停止服务...")
    
    # 停止调度线程
    if schedule_task:
        schedule_task.stop()  # 假设我们已经实现了stop方法
        schedule_task.join(timeout=5)  # 等待线程结束，最多等待5秒
        print("调度线程已停止")
    
    sys.exit(0)

# 注册信号处理
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# register blueprints
def register_blueprints(new_app, path):
    for name in werkzeug.utils.find_modules(path):
        m = werkzeug.utils.import_string(name)
        new_app.register_blueprint(m.bp)
    new_app.errorhandler(OddException)(odd_exception_handler)

    return new_app

app = Flask(__name__, static_url_path='')
register_blueprints(app, 'oddagent.router')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# 使用配置文件中的CORS设置
CORS(app, origins="*", supports_credentials=True)

def main():
    global schedule_task

    print("===================================================================")
    asciiart = r"""
 OOO   dddd   dddd   M   M  eeeee  ttttt   aaaaa
O   O  d   d  d   d  MM MM  e        t    a     a
O   O  d   d  d   d  M M M  eeee     t    aaaaaaa
O   O  d   d  d   d  M   M  e        t    a     a
 OOO   dddd   dddd   M   M  eeeee    t    a     a

 ⭐️ Open Source: https://github.com/oddmeta/oddagent
 📖 Documentation: https://docs.oddmeta.net/
        """

    print(asciiart)
    print("===================================================================")
    print(f"http://{config.BACKEND_HOST}:{config.BACKEND_PORT}")

    # 创建并启动调度线程
    schedule_task = OddAgentScheduler()
    schedule_task.start()
    print("调度线程已启动")
    
    try:
        # 启动Flask应用
        app.run(
            host=config.BACKEND_HOST,
            port=config.BACKEND_PORT,
            debug=config.DEBUG
        )
    except Exception as e:
        print(f"应用发生错误: {e}")
    finally:
        # 确保线程停止
        if schedule_task and schedule_task.is_alive():
            schedule_task.stop()
            schedule_task.join(timeout=3)

