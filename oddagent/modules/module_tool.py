# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: module_tool_config.py 
@info: 智能体模块配置工具
"""
import os
import json
import re
import importlib.util
import glob

from oddagent.config_loader import config
from oddagent.odd_agent_logger import logger
from oddagent.modules.generate_testset import process_json_py_file

def load_tool_templates(file_path):
    """
    从本地tool_templates.json文件加载工具配置

    :param file_path: tool_templates.json文件路径
    :return: 包含所有工具配置的字典
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_tool_config(tool_config_file, config_file_ext: str = "_config.py"):
    """
    从本地Python文件加载工具配置
    特殊处理global_variants通用字段，将其合并到每个工具的parameters中
    """
    all_tool_configs = {}
    
    # 判断是否为Python文件
    if tool_config_file.endswith(config_file_ext):
        # 使用importlib动态导入Python模块
        module_name = os.path.splitext(os.path.basename(tool_config_file))[0]
        
        # 构建模块路径
        spec = importlib.util.spec_from_file_location(module_name, tool_config_file)
        if spec:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 假设模块中有一个名为tool_config的字典变量
            if hasattr(module, 'tool_config'):
                current_config = module.tool_config
            else:
                # 如果没有tool_config变量，尝试获取agent_tool_list和global_variants
                current_config = {}
                if hasattr(module, 'agent_tool_list'):
                    current_config['agent_tool_list'] = module.agent_tool_list
                if hasattr(module, 'global_variants'):
                    current_config['global_variants'] = module.global_variants
    else:
        # 保持原有逻辑，处理JSON文件
        current_config = load_tool_templates(tool_config_file)
    
    # 提取全局变量
    global_variants = current_config.get('global_variants', [])
    agent_tool_list = current_config.get('agent_tool_list', [])
    
    # 后续处理逻辑保持不变
    for tool in agent_tool_list:
        tool_name = tool.get('tool_name')
        enabled = tool.get('enabled', False)

        if not enabled:
            continue

        if tool_name and tool_name not in all_tool_configs:
            # 复制工具的parameters
            tool_parameters = tool.get('parameters', []).copy()
            
            # 使用tool_parameters而不是合并global_variants
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
    
    return all_tool_configs

def load_all_tool_config(config_file_ext: str = "_config.py"):
    """
    从本地文件加载工具配置
    特殊处理global_variants通用字段，将其合并到每个工具的parameters中
    """
    all_tool_configs = {}

    if config.TOOL_CONFIG_FILE == "*":
        # 搜索目录下的所有*.json.py文件
        for file_path in glob.glob(f"modules/**/*{config_file_ext}", recursive=True):
            # 排除__init__.py等非配置文件
            if not os.path.basename(file_path).startswith("__"):
                logger.info(f"加载工具配置: {file_path}")
                tool_config = load_tool_config(file_path, config_file_ext)
                all_tool_configs.update(tool_config)
    else:
        # 检查文件是否存在
        if not os.path.exists(config.TOOL_CONFIG_FILE):
            raise FileNotFoundError(f"工具配置文件{config.TOOL_CONFIG_FILE}不存在")
        
        all_tool_configs = load_tool_config(config.TOOL_CONFIG_FILE)

    # logger.debug(f"加载工具配置: {all_tool_configs}")

    return all_tool_configs

def load_tool_config_json(tool_config_file):
    """
    从本地tool_templates.json文件加载工具配置
    特殊处理global_variants通用字段，将其合并到每个工具的parameters中
    """
    all_tool_configs = {}
    current_config = load_tool_templates(tool_config_file)
    
    # 提取全局变量
    global_variants = current_config.get('global_variants', [])
    agent_tool_list = current_config.get('agent_tool_list', [])
    
    for tool in agent_tool_list:
        tool_name = tool.get('tool_name')
        enabled = tool.get('enabled', False)

        if not enabled:
            continue

        if tool_name and tool_name not in all_tool_configs:
            # 复制工具的parameters
            tool_parameters = tool.get('parameters', []).copy()
            
            # FIXME 会议平台API接口、参数、响应格式变来变去不统一，导致全局变量有点问题，暂时禁用。将global_variants合并到parameters前面
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
    # for key, value in current_config.items():
    #     if key not in ['global_variants', 'agent_tool_list'] and key not in all_tool_configs:
    #         # 为其他配置项也添加tool_name字段
    #         if isinstance(value, dict):
    #             value['tool_name'] = key
    #         all_tool_configs[key] = value

    return all_tool_configs

def load_all_tool_config_json():
    """
    从本地tool_templates.json文件加载工具配置
    特殊处理global_variants通用字段，将其合并到每个工具的parameters中
    """
    all_tool_configs = {}

    if config.TOOL_CONFIG_FILE == "*":
        # 搜索目录下的所有json文件
        for file_path in glob.glob("modules/**/*.json", recursive=True):
            # logger.info(f"加载工具配置: {file_path}")
            tool_config += load_tool_config_json(file_path)
    else:
        # 检查文件是否存在
        import os
        if not os.path.exists(config.TOOL_CONFIG_FILE):
            raise FileNotFoundError(f"工具配置文件{config.TOOL_CONFIG_FILE}不存在")

        all_tool_configs = load_tool_config_json(config.TOOL_CONFIG_FILE)

    logger.info(f"加载工具配置: {all_tool_configs}")

    return all_tool_configs


def is_slot_fully_filled(json_data):
    """
    检查槽位是否完整填充
    FIXME 暂未检查判断 required 字段是否为True，若为False，则槽位非必须填充
    :param json_data: 槽位参数JSON数据
    :return: 如果所有槽位都已填充，返回True；否则返回False
    """
    # 遍历JSON数据中的每个元素
    for item in json_data:
        # 检查value字段是否为空字符串
        if item.get('required', False) and item.get('value') == '':
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
        new_item = {"name": item["name"], "desc": item["desc"], "type": item["type"], "value": "", "required": item.get("required", False)}
        output_data.append(new_item)
    return output_data

def get_dynamic_example(tool_config):
    """
    从工具配置中获取输入输出的示例
    """
    if 'example' in tool_config and tool_config['example'] != '':
        return tool_config['example']
    else:
        # FIXME 给一个默认的示例？？？
        return "N/A"

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
        else:
            logger.warning(f"槽位参数 {item['name']} 的值为空字符串，LLM未解析出槽位值")
            for target in dict_target:
                if target['name'] == item['name']:
                    target['value'] = ""
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

    """
    qwen3-30b-a3b-instruct-2507格式一：
    {'choices': [{'finish_reason': 'stop', 'index': 0, 'message': {'content': '```json\n{"name": "enable", "desc": "静音开关：1表示关闭麦克风（静音），0表示开启麦克风（开麦）", "value": 1}\n```', 'role': 'assistant'}}], 'created': 1763542334, 'id': 'chatcmpl-31d41660-1da4-4b73-bf34-1d3802133e55', 'model': 'qwen3-30b-a3b-instruct-2507', 'object': 'chat.completion', 'usage': {'completion_tokens': 43, 'prompt_tokens': 277, 'total_tokens': 320}}
    """

    """
    qwen3-30b-a3b-instruct-2507格式二：
    {'choices': [{'finish_reason': 'stop', 'index': 0, 'message': {'content': '{"enable": 0}', 'role': 'assistant'}}], 'created': 1763541944, 'id': 'chatcmpl-34f2da20-bfa9-4df3-99ca-7b330987650c', 'model': 'qwen3-30b-a3b-instruct-2507', 'object': 'chat.completion', 'usage': {'completion_tokens': 6, 'prompt_tokens': 247, 'total_tokens': 253}}
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

def load_skills():
    """加载技能"""

    skill_list = []

    # 查找所有.json结尾的文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_files = []

    if config.TOOL_CONFIG_FILE == "*":
        for file_path in glob.glob(f"**/{config.TOOL_CONFIG_FILE}{config.TOOL_CONFIG_FILE_EXT}", recursive=True):
            # 排除__init__.py等非配置文件
            if not os.path.basename(file_path).startswith("__"):
                file_path = os.path.join(current_dir, file_path)
                print(f"处理文件: {file_path}")
                json_files.append(file_path)
    else:
        json_files = [config.TOOL_CONFIG_FILE]

    if not json_files:
        logger.error(f"当前路径：{current_dir}， 没有找到.json结尾的文件")
        return {"agent_tool_list": []}
    
    print(f"找到 {len(json_files)} 个.json文件")
    print("==================================================================")

    # 处理每个文件
    for file_path in json_files:
        print("------------------------------------------------------------------")
        print(f"处理文件: {file_path}")
        print("------------------------------------------------------------------")
        
        # 处理每个文件
        processed_tools = process_json_py_file(file_path)
        
        if processed_tools:
            # 生成输出文件名（将.json改为.json）
            output_filename = os.path.basename(file_path)
            
            # 保存为JSON文件
            result = {
                "file_name": output_filename,
                "agent_tool_list": processed_tools
            }
            skill_list.append(result)
            
            print(f"已保存处理后的文件: {output_filename}")
            print(f"处理了 {len(processed_tools)} 个工具项")
        else:
            print(f"文件 {file_path} 处理失败")

        print("------------------------------------------------------------------")
    
    print("所有文件处理完成")

    return skill_list