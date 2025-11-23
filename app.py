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

import odd_agent_config as config
from logic.schedule_task import OddAgentScheduler

import signal
import sys

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

class CodeException(Exception):

    def __init__(self, error_code, error_desc):
        super().__init__()
        self.error_code = error_code
        self.error_desc = error_desc

    def __str__(self):
        return "%d - %s" % (self.error_code, self.error_desc)

    def __unicode__(self):
        return u"%d - %s" % (self.error_code, self.error_desc)

class Result:
    def __init__(self):
        self._result = {}

    def set_code(self, error_code):
        self._result['error_code'] = error_code

    def set_msg(self, error_desc):
        self._result['error_desc'] = error_desc

    def set_data(self, data):
        self._result['data'] = data

    @property
    def result(self):
        return self._result


def from_exc(exc):
    r = Result()
    r.set_code(exc.error_code)
    r.set_msg(exc.error_desc)
    return r.result

class ResultException(CodeException):
    """异常返回"""
    def __init__(self, error_code, error_desc):
        super(ResultException, self).__init__(error_code, error_desc)
def handler(exc):
    return jsonify(from_exc(exc))

# register blueprints
def register_blueprints(new_app, path):
    for name in werkzeug.utils.find_modules(path):
        m = werkzeug.utils.import_string(name)
        new_app.register_blueprint(m.bp)
    new_app.errorhandler(CodeException)(handler)
    return new_app

app = Flask(__name__, static_url_path='')
register_blueprints(app, 'router')
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

if __name__ == '__main__':
    main()
