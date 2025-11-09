# -*- coding: utf-8 -*-

import json
import requests

from tools import tool_prompts
from tools.tool_executer import ToolExecuter 
from tools.tool_template_utils import get_slot_parameters_from_tool, llm_chat, get_dynamic_example
from odd_agent_logger import logger
import odd_agent_config as config
from logic.api_request_composer import api_request_composer
from logic.api_response_paser import api_response_parser

class ToolExecuterImpl(ToolExecuter):
    def __init__(self, tool_config):
        parameters = tool_config["parameters"]
        self.tool_config = tool_config
        self.tool_name = tool_config["name"]
        self.slot_template = get_slot_parameters_from_tool(parameters)
        self.slot_dynamic_example = get_dynamic_example(tool_config)
        self.slot = get_slot_parameters_from_tool(parameters)
        self.tool_prompts = tool_prompts
        self.tool_api_url = tool_config.get("tool_api_url", "")
        self.tool_api_method = tool_config.get("tool_api_method", "POST")

    def execute(self, slots_data):
        """
        处理用户输入，更新槽位，检查完整性，以及与用户交互
        :param slots_data: 槽位数据
        :return: 处理结果
        """

        logger.debug(f'工具名称：{self.tool_name}, 槽位数据：{slots_data}')

        try:
            logger.debug(f"工具名称: {self.tool_name}")
            logger.debug(f"工具参数: {json.dumps(slots_data, ensure_ascii=False)}")

            if config.API_FAKE_API_RESULT:
                result = {
                    "code": 200, 
                    "message": f"假装 [{self.tool_name}] API调用成功", 
                    "data": 
                    {
                        "result": "成功", 
                        "message": f"假装 [{self.tool_name}] API调用成功"
                    }
                }
            else:

                api_url, headers, content = api_request_composer(self.tool_name, self.tool_config, slots_data)

                # 发送POST请求，直接发送扁平化的slots_data
                logger.debug(f"调用工具API: {api_url}, headers: {headers}, method: {self.tool_api_method}, 请求体: {json.dumps(content, ensure_ascii=False)}")

                response = requests.post(
                    api_url, 
                    headers=headers, 
                    json=content, 
                    timeout=config.API_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                else:
                    logger.error(f"API调用失败，状态码: {response.status_code}")
                    return {"error": f"API调用失败，状态码: {response.status_code}"}

            logger.debug(f"            API调用响应: {json.dumps(result, ensure_ascii=False)}")

            return result

        except requests.RequestException as e:
            logger.error(f"API请求异常: {e}")
            return {"error": f"API请求异常: {e}"}
        except Exception as e:
            logger.error(f"处理API响应时出错: {e}")
            return {"error": f"处理API响应时出错: {e}"}


    def execute_result_parser(self, api_result, chat_history=None):
        """
        TODO: 有些工具的API返回结果里可能会带上一些额外的信息，比如创建会议成功后台返回的会议ID，或者创建会议失败的错误码。

        处理API结果，通过AI生成用户友好的回复

        :param api_result: API返回的结果
        :param chat_history: 聊天记录
        :return: 处理后的用户友好回复
        """
        try:
            # 只取data部分发给AI
            data_part = api_result.get("data", api_result)
            prompt = config.API_RESULT_PROMPT.format(api_result=json.dumps(data_part, ensure_ascii=False))
            
            # 调用AI处理结果
            result = llm_chat(prompt, None, chat_history)
            
            if result:
                return result
            else:
                logger.error("处理API结果时出错: %s", e)
                return "抱歉，处理结果时出现错误，请稍后重试。"
                
        except Exception as e:
            logger.error(f"处理API结果时出错: {e}")
            return "抱歉，处理结果时出现错误，请稍后重试。"
