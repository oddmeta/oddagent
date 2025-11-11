# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: tool_template_utils.py 
@info: 工具模版工具
"""

import glob
import json
import re
import requests
import urllib3
import odd_agent_config as config
from odd_agent_logger import logger

# 禁用SSL证书验证警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def load_tool_templates(file_path):
    """
    从本地tool_templates.json文件加载工具配置

    :param file_path: tool_templates.json文件路径
    :return: 包含所有工具配置的字典
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def load_all_tool_config():
    """
    从本地tool_templates.json文件加载工具配置
    特殊处理global_variants通用字段，将其合并到每个工具的parameters中
    """
    all_tool_configs = {}

    # 搜索目录下的所有json文件
    for file_path in glob.glob("modules/**/*.json", recursive=True):
        # logger.info(f"加载工具配置: {file_path}")
        current_config = load_tool_templates(file_path)
        
        # 提取全局变量
        global_variants = current_config.get('global_variants', [])
        # logger.debug(f"全局变量: {global_variants}")
        # 处理工具列表
        agent_tool_list = current_config.get('agent_tool_list', [])
        # logger.debug(f"工具列表: {agent_tool_list}")
        
        for tool in agent_tool_list:
            tool_name = tool.get('tool_name')
            if tool_name and tool_name not in all_tool_configs:
                # 复制工具的parameters
                tool_parameters = tool.get('parameters', []).copy()
                
                # FIXME 科达会议平台API接口、参数、响应格式变来变去不统一，导致全局变量有点问题，暂时禁用。将global_variants合并到parameters前面
                # merged_parameters = global_variants.copy() + tool_parameters
                merged_parameters = tool_parameters

                # 构建工具配置，添加tool_name字段
                all_tool_configs[tool_name] = {
                    "tool_name": tool_name,  # 添加英文工具名称
                    "name": tool.get('name', ''),
                    "description": tool.get('description', ''),
                    "parameters": merged_parameters,
                    "enabled": tool.get('enabled', False),
                    "example": tool.get('example', '')
                }

        # 处理其他非agent_tool_list和global_variants的配置项
        for key, value in current_config.items():
            if key not in ['global_variants', 'agent_tool_list'] and key not in all_tool_configs:
                # 为其他配置项也添加tool_name字段
                if isinstance(value, dict):
                    value['tool_name'] = key
                all_tool_configs[key] = value

    return all_tool_configs

def llm_chat(message, user_input, chat_history=None):
    """
    请求chatGPT函数，支持聊天记录
    :param message: 要发送的消息
    :param user_input: 用户输入
    :param chat_history: 聊天记录
    :return: chatGPT回复
    """
    # logger.debug('--------------------------------------------------------------------')
    # if config.DEBUG:
    #     logger.debug(f'prompt输入: {message}')
    # elif user_input:
    #     logger.debug(f'用户输入: {user_input}')  
    # logger.debug('----------------------------------')
    
    headers = {
        "Authorization": f"Bearer {config.API_KEY}",
        "Content-Type": "application/json",
    }

    # 构建消息列表
    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    
    # 添加聊天记录（如果提供）
    if chat_history:
        # 限制聊天记录数量
        limited_history = chat_history[-config.CHAT_HISTORY_COUNT:]
        for msg in limited_history:
            messages.append(msg)
    
    # 添加当前消息
    messages.append({"role": "user", "content": f"{message}"})

    data = {
        "model": config.MODEL,
        "messages": messages,
        "enable_thinking": False
    }

    try:
        # logger.debug(f'=================================LLM输入: {data}')
        response = requests.post(config.GPT_URL, headers=headers, json=data, verify=False)
        if response.status_code == 200:
            logger.debug(f'=================================LLM输出: {response.json()}')
            answer = response.json()["choices"][0]["message"]['content']
            logger.debug('--------------------------------------------------------------------')
            return answer
        else:
            logger.error(f"调用大模型接口失败，请检查API_KEY是否配置正确\n=================================Error: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"调用大模型接口失败，请检查网络连接\n=================================Request error: {e}")
        return None


def is_slot_fully_filled(json_data):
    """
    检查槽位是否完整填充
    :param json_data: 槽位参数JSON数据
    :return: 如果所有槽位都已填充，返回True；否则返回False
    """
    # 遍历JSON数据中的每个元素
    for item in json_data:
        # 检查value字段是否为空字符串
        if item.get('value') == '':
            return False  # 如果发现空字符串，返回False
    return True  # 如果所有value字段都非空，返回True


def get_slot_parameters_from_tool(parameters):
    """
    从工具配置中获取槽位参数
    :param parameters: 工具配置中的参数列表
    :return: 包含槽位参数的JSON数据列表
    """
    output_data = []
    for item in parameters:
        new_item = {"name": item["name"], "desc": item["desc"], "type": item["type"], "value": ""}
        output_data.append(new_item)
    return output_data

def get_dynamic_example(tool_config):
    """
    从工具配置中获取动态示例
    """
    if 'example' in tool_config and tool_config['example'] != '':
        return tool_config['example']
    else:
        return "JSON：[{'name': 'phone', 'desc': '需要查询的手机号', 'value': ''}, {'name': 'month', 'desc': '查询的月份，格式为yyyy-MM', 'value': ''} ]\n输入：帮我查一下18724011022在2024年7月的流量\n答：{ 'phone': '18724011022', 'month': '2024-07' }"

def get_slot_update_json(slot):
    """
    从槽位参数中获取更新JSON
    """
    output_data = []
    for item in slot:
        new_item = {"name": item["name"], "desc": item["desc"], "value": item["value"]}
        output_data.append(new_item)
    return output_data


def get_slot_query_user_json(slot):
    """
    从槽位参数中获取查询用户JSON
    """
    output_data = []
    for item in slot:
        if not item["value"]:
            new_item = {"name": item["name"], "desc": item["desc"], "value":  item["value"]}
            output_data.append(new_item)
    return output_data


def update_slot(json_data, dict_target):
    """
    更新槽位slot参数
    """
    # 遍历JSON数据中的每个元素
    for item in json_data:
        # 检查item是否包含必要的字段
        if not isinstance(item, dict) or 'name' not in item or 'value' not in item:
            continue
        # 检查value字段是否为空字符串
        if item['value'] != '':
            for target in dict_target:
                if target['name'] == item['name']:
                    target['value'] = item.get('value')
                    break


def format_name_value_for_logging(json_data):
    """
    抽取参数名称和value值
    """
    log_strings = []
    for item in json_data:
        name = item.get('name', 'Unknown name')  # 获取name，如果不存在则使用'Unknown name'
        value = item.get('value', 'N/A')  # 获取value，如果不存在则使用'N/A'
        log_string = f"name: {name}, Value: {value}"
        log_strings.append(log_string)
    return '\n'.join(log_strings)


def try_load_json_from_string(input_string):
    """
    JSON抽取函数
    返回包含JSON对象的列表
    """
    try:
        # 正则表达式假设JSON对象由花括号括起来
        matches = re.findall(r'\{.*?\}', input_string, re.DOTALL)

        # 验证找到的每个匹配项是否为有效的JSON
        valid_jsons = []
        for match in matches:
            try:
                json_obj = json.loads(match)
                valid_jsons.append(json_obj)
            except json.JSONDecodeError:
                try:
                    valid_jsons.append(fix_json(match))
                except json.JSONDecodeError:
                    continue
                continue

        return valid_jsons
    except Exception as e:
        print(f"Error occurred: {e}")
        return []

def fix_json(bad_json):
    """
    修复JSON字符串中的错误
    """
    # 首先，用双引号替换掉所有的单引号
    fixed_json = bad_json.replace("'", '"')
    try:
        # 然后尝试解析
        return json.loads(fixed_json)
    except json.JSONDecodeError:
        # 如果解析失败，打印错误信息，但不会崩溃
        logger.error("给定的字符串不是有效的 JSON 格式。")

