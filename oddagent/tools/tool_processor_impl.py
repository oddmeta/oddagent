# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: tool_processor_impl.py 
@info: 工具处理器实现
"""

import json

from oddagent.tools import tool_prompts
from oddagent.tools.tool_processor import ToolProcessor
from oddagent.tools.tool_executer_impl import ToolExecuterImpl

from oddagent.modules.module_tool import get_slot_parameters_from_tool, update_slot, format_name_value_for_logging, is_slot_fully_filled, \
     try_load_json_from_string, get_dynamic_example, get_slot_query_user_json, get_slot_update_json
from oddagent.tools.tool_datetime_utils import tool_get_current_date, tool_get_current_time
from oddagent.tools.tool_llm import llm_chat
from oddagent.odd_agent_logger import logger
from oddagent.config_loader import config
from oddagent.logic.odd_agent_error import EM_ERR_INTENT_RECOGNITION_API_CONNECTION_ERROR, EM_ERR_INTENT_RECOGNITION_NO_TOOL3, odd_err_desc, OddException

class ToolProcessorImpl(ToolProcessor):
    def __init__(self, tool_config):
        parameters = tool_config["parameters"]
        self.tool_config = tool_config
        self.tool = tool_config["tool_name"]
        self.tool_name = tool_config["name"]
        self.description = tool_config["description"]
        self.slot_template = get_slot_parameters_from_tool(parameters)
        self.slot_dynamic_example = get_dynamic_example(tool_config)
        self.slot = get_slot_parameters_from_tool(parameters)
        self.tool_prompts = tool_prompts
        self.tool_api_url = tool_config.get("tool_api_url", "")
        self.tool_api_method = tool_config.get("tool_api_method", "POST")
        self.tool_api_headers = tool_config.get("tool_api_headers", {}) # TODO 暂未配置文件中读取，后续从配置文件中读取
        self.tool_executer = ToolExecuterImpl(tool_config)

    def process(self, user_input, context, api_mode):
        """
        处理用户输入，更新槽位，检查完整性，以及与用户交互
        :param user_input: 用户的输入
        :param context: 对话的上下文
        :return: 处理结果
        """
        logger.debug(f'用户输入：{user_input}, self.slot_template: {self.slot_template}， self.slot_dynamic_example: {self.slot_dynamic_example}')

        # 检查当前工具是否有槽位需要填充
        if len(self.slot_template) == 0:
            return self.process_complete_data(context, api_mode)

        # 先检查本次用户输入是否有信息补充，保存补充后的结果   编写程序进行字符串value值diff对比，判断是否有更新
        slots_str = json.dumps(get_slot_update_json(self.slot_template), ensure_ascii=False)

        if config.LLM_TYPE == "qwen2.5-0.5b-instruct":
            message = tool_prompts.PROMPT_SLOT_UPDATE.format(self.tool_name, 
                                                            tool_get_current_date(), 
                                                            self.slot_dynamic_example, 
                                                            user_input)
        else:
            message = tool_prompts.PROMPT_SLOT_UPDATE_QWEN3.format(self.tool_name, 
                                                            tool_get_current_date(), 
                                                            slots_str, 
                                                            self.slot_dynamic_example, 
                                                            user_input)

        # message = tool_prompts.PROMPT_SLOT_UPDATE_QWEN3.format(self.tool_name, 
        #                                                 tool_get_current_date(), 
        #                                                 self.slot_dynamic_example, 
        #                                                 slots_str, 
        #                                                 user_input)

        new_info_json_raw, result = llm_chat(message, context)

        if result != 0:
            logger.error(f"调用LLM API时出现错误：{result}")
            result = {"err_code": result, "msg": odd_err_desc(result), "data": "slot_update"}
            return result
        
        # 每个大模型返回的json数据结构，每个大模型返回的json数据结构不同，需要根据实际情况处理
        # 例如：qwen3-30b-a3b-instruct-2507格式一：{'choices': [{'finish_reason': 'stop', 'index': 0, 'message': {'content': '```json\n{"name": "enable", "desc": "静音开关：1表示关闭麦克风（静音），0表示开启麦克风（开麦）", "value": 1}\n```', 'role': 'assistant'}}], 'created': 1763542334, 'id': 'chatcmpl-31d41660-1da4-4b73-bf34-1d3802133e55', 'model': 'qwen3-30b-a3b-instruct-2507', 'object': 'chat.completion', 'usage': {'completion_tokens': 43, 'prompt_tokens': 277, 'total_tokens': 320}}
        new_info_json = try_load_json_from_string(new_info_json_raw)
        
        current_values = []
        if new_info_json and isinstance(new_info_json[0], dict) and not ('name' in new_info_json[0] and 'value' in new_info_json[0]):
            flat = new_info_json[0]
            current_values = [{"name": k, "value": v} for k, v in flat.items()]
        else:
            current_values = new_info_json

        logger.debug(f'new_info_json_raw: {new_info_json_raw}')
        logger.debug(f'current_values: {current_values}')
        logger.debug(f'slot update before: {self.slot}')
        update_slot(current_values, self.slot)
        logger.debug(f'slot update after: {self.slot}')

        if is_slot_fully_filled(self.slot):
            return self.process_complete_data(context, api_mode)
        else:
            return self.process_more_slot_data(user_input, context)

    def process_complete_data(self, context, api_mode):
        """
        处理完整的数据，调用工具API，生成用户友好的回复
        :param context: 对话的上下文
        :return: 处理结果
        """
        logger.debug(f'process_complete_data: 工具名称={self.tool_name}')
        logger.debug(format_name_value_for_logging(self.slot))
        
        # 获取工具名称
        tool_name = self._get_tool_name()
        if not tool_name:
            logger.error(f"无法找到工具 '{self.tool_name}' 的配置信息。")
            result = {"err_code": EM_ERR_INTENT_RECOGNITION_NO_TOOL3, "msg": odd_err_desc(EM_ERR_INTENT_RECOGNITION_NO_TOOL3), "data": "slot_update"}
            return result
        
        # 准备槽位数据，使用英文键名
        slots_data = {}
        for slot in self.slot:
            if slot['value'] != "":
                slot_key = self._get_slot_key(slot['name'])
                if slot_key:
                    slots_data[slot_key] = slot['value']
        logger.debug(f'slots_data: {slots_data}')
        
        ## 当前session的数据已经保存到slots_data中，清除保存在self.slot中的value值，避免后续重复使用
        for slot in self.slot:
            slot['value'] = ""

        # 调用工具API
        try:
            api_result = self.tool_executer.execute(slots_data=slots_data, api_mode=api_mode)
            logger.debug(f'API结果: {api_result}')
            # 处理API结果
            if "error" in api_result:
                logger.error(f"调用API时出现错误：{api_result['error']}")
                result = {"err_code": EM_ERR_INTENT_RECOGNITION_API_CONNECTION_ERROR, "msg": odd_err_desc(EM_ERR_INTENT_RECOGNITION_API_CONNECTION_ERROR), "data": f"error: {EM_ERR_INTENT_RECOGNITION_API_CONNECTION_ERROR}"}
                return result
            
            if config.API_PRETTY_RSP:
                # 通过AI处理API结果，生成用户友好的回复
                user_friendly_response = self.tool_executer.execute_result_parser(api_result, context)
                logger.debug(f'用户friendly_response: {user_friendly_response}')
            else:
                # user_friendly_response = {"answer": api_result}
                user_friendly_response = api_result

            # result = {"err_code": 0, "msg": "success", "data": user_friendly_response}
            result = user_friendly_response
            logger.debug(f'process_complete_data: 返回结果: {result}')

        except OddException as e:
            logger.error(f"调用工具API时出现错误：{e}")
            result = {"err_code": e.err_code, "msg": e.message, "data": "调用工具API时出现错误：" + e.message}
            return result

        return result

    def process_more_slot_data(self, user_input, context):
        """
        处理缺失的数据，请求用户填写缺失的数据
        :param user_input: 用户的输入
        :param context: 对话的上下文
        :return: 处理结果
        """
        logger.debug(f'process_more_slot_data: 工具名称={self.tool_name}')
        
        slots_str = json.dumps(get_slot_query_user_json(self.slot), ensure_ascii=False)
        # message = tool_prompts.PROMPT_QUERY_SLOT.format(self.tool, self.tool_name, self.description, slots_str, self.slot_template, user_input)
        message = tool_prompts.PROMPT_QUERY_SLOT_USER.format(self.tool, self.tool_name, self.description, slots_str, self.slot_template, user_input)

        result, err_code = llm_chat(message, context)

        if err_code != 0:
            logger.error(f"调用LLM API时出现错误：{err_code}")
            result = {"err_code": err_code, "tool_name": self.tool, "msg": odd_err_desc(err_code), "data": "slot_query"}
            return result
        
        result = {"err_code": 0, "tool_name": self.tool, "msg": "success", "data": result}
        logger.debug(f'process_more_slot_data: 响应结果: {result}')

        return result

    def _get_tool_name(self):
        """
        根据工具配置获取工具的英文键名
        :return: 工具的英文键名
        """
        # 直接从tool_config中获取tool_name字段
        return self.tool_config.get('tool_name')
    
    def _get_slot_key(self, slot_name):
        """
        直接使用参数的name字段作为键名
        :param slot_name: 参数的中文名称
        :return: 参数的英文键名
        """
        # 查找对应的参数配置
        for param in self.tool_config.get("parameters", []):
            if param.get("name") == slot_name:
                return param.get("name")
        
        # 如果找不到配置，直接返回原名称
        return slot_name
