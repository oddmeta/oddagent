# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: tool_llm.py 
@info: LLM工具
"""
import requests
import urllib3

from oddagent.config_loader import config
from oddagent.odd_agent_logger import logger
from oddagent.logic.odd_agent_error import EM_ERR_LLM_APIKEY_ERROR, EM_ERR_LLM_CONNECTION_ERROR, EM_ERR_LLM_TIMEOUT, OddException, odd_err_desc

# 禁用SSL证书验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def llm_chat(message, chat_history=None):
    """
    请求chatGPT函数，支持聊天记录
    :param message: 要发送的消息
    :param chat_history: 聊天记录
    :return: chatGPT回复, 错误码
    """
    headers = {
        "Authorization": f"Bearer {config.API_KEY}",
        "Content-Type": "application/json",
    }

    error = 0

    # 构建消息列表
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    
    # 添加聊天记录（如果提供）
    if chat_history:
        # 限制聊天记录数量
        limited_history = chat_history[-config.LLM_MAX_HISTORY_MESSAGE:]
        for msg in limited_history:
            messages.append(msg)
    
    # 添加当前消息
    messages.append({"role": "user", "content": f"{message}"})

    # 关闭思考模式，对qwen3-0.6b模型无效，需要在chat_template中设置
    # data = {
    #     "model": config.MODEL,
    #     "messages": messages,
    #     "enable_thinking": False
    # }
    # data = {
    #     "model": config.MODEL,
    #     "messages": messages,
    #     "extra_body":{"chat_template_kwargs": {"enable_thinking": False}}
    # }

    data = {
        "model": config.MODEL,
        "messages": messages,
        "temperature": config.LLM_TEMPERATURE,
        "chat_template_kwargs": {"enable_thinking": False}
    }

    if config.LLM_FORCE_NO_THINK:
        data["chat_template_kwargs"] = {"enable_thinking": False} # 关闭思考模式，对qwen3-0.6b模型无效，需要在chat_template中设置
        data["enable_thinking"] =  False  # 兼容qwen3-0.6b, qwen3-30b-a3b，不确定是否可以兼容Qwen3全系
    
    try:
        logger.debug(f'=================================LLM输入: {data}')
        response = requests.post(config.GPT_URL, headers=headers, json=data, verify=False)
        if response.status_code == 200:
            logger.debug(f'=================================LLM输出: {response.json()}')
            answer = response.json()["choices"][0]["message"]['content']
            logger.debug('--------------------------------------------------------------------')
            return answer, error
        else:
            logger.error(f"调用大模型接口失败，请检查API_KEY是否配置正确\n=================================Error: {response.status_code}, {response.text}")
            # raise OddException(EM_ERR_LLM_APIKEY_ERROR, odd_err_desc(EM_ERR_LLM_APIKEY_ERROR))
            return None, EM_ERR_LLM_APIKEY_ERROR
    except requests.RequestException as e:
        logger.error(f"调用大模型接口失败，请检查网络连接\n=================================Request error: {e}")
        # raise OddException(EM_ERR_LLM_TIMEOUT, odd_err_desc(EM_ERR_LLM_TIMEOUT))
        return None, EM_ERR_LLM_TIMEOUT
    except Exception as e:
        logger.error(f"调用大模型接口失败，请检查网络连接\n=================================Error: {e}")
        # raise OddException(EM_ERR_LLM_CONNECTION_ERROR, odd_err_desc(EM_ERR_LLM_CONNECTION_ERROR))
        return None, EM_ERR_LLM_CONNECTION_ERROR

