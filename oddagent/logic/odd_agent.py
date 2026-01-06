# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: odd_agent.py 
@info: Odd Agent
"""

import json
import re

from oddagent.tools.tool_processor_impl import ToolProcessorImpl
from oddagent.tools.tool_llm import llm_chat
from oddagent.tools import tool_prompts
from oddagent.modules.module_tool import get_slot_parameters_from_tool
from oddagent.odd_agent_logger import logger
from oddagent.config_loader import config
from oddagent.logic.odd_agent_error import odd_err_desc, EM_ERR_INTENT_RECOGNITION_EXCEPTION, EM_ERR_INTENT_RECOGNITION_NO_TOOL, EM_ERR_INTENT_RECOGNITION_NO_TOOL2, EM_ERR_API_INVOKE_EXCEPTION

NO_TOOL_RESPONSE = config.NO_TOOL_RESPONSE

class OddAgent:
    def __init__(self, tool_templates: dict):
        self.tool_templates: dict = tool_templates      # 工具配置
        self.current_purpose: str = ''                  # 当前工具的名称
        self.last_recognized_tool: str = ''             # 记录上次识别到的工具
        self.processors = {}                            # 工具处理器
        self.tool_slots = {}                            # 每个工具的槽位数据
        self.chat_history = []                          # 添加聊天记录存储
        self.is_slot_filling = False                    # 标记是否正在补槽阶段

    def update_global_variants(self, global_variants):
        """
        更新全局变量。比如创建会议后，平台会返回一个confid，需要将其存储到全局变量中。
        :param global_variants: 全局变量
        """
        logger.error(f"更新全局变量：{global_variants}")
        
        for key, value in global_variants.items():
            logger.debug(f"更新全局变量到tool_templates：{key} = {value}")
            if key in self.tool_templates:
                self.tool_templates[key] = value

    @staticmethod
    def load_tool_processor(self, tool_config):
        """
        加载工具配置
        :param tool_config: 工具配置
        :return: 工具处理器
        """
        try:
            return ToolProcessorImpl(tool_config)
        except (ImportError, AttributeError, KeyError):
            raise ImportError(f"未找到工具处理器 tool_config: {tool_config}")

    def recognize_intent(self, user_input):
        """
        识别用户意图
        :param user_input: 用户输入
        :return: 处理结果
        """
        purpose_options = {}
        purpose_description = {}
        index = 1

        logger.debug(f"工具配置: {self.tool_templates}") 

        try:
            for template_key, template_info in self.tool_templates.items():
                purpose_options[str(index)] = template_key
                if isinstance(template_info, dict) and "description" in template_info:
                    purpose_description[str(index)] = template_info["description"]
                    index += 1
                else:
                    # 如果不是字典或没有description键，使用默认值或跳过
                    logger.warning(f"工具配置格式异常: {template_key}")

            options_prompt = "\n".join([f"{key}. {value} - 请回复{key}" for key, value in purpose_description.items()])
            options_prompt += "\n0. 无工具/无法判断/没有符合的选项 - 请回复0"

            # 发送选项给AI，带上聊天记录
            last_tool_info = f"上次识别到的工具：{self.last_recognized_tool}" if self.last_recognized_tool else "上次识别到的工具：无"
            user_choice, error = llm_chat(
                f"有下面多种工具，需要你根据用户输入进行判断，以最新的聊天记录为准，只答选项\n{last_tool_info}\n{options_prompt}\n用户输入：{user_input}\n请回复序号：", 
                self.chat_history
            )

            logger.debug(f'llm_chat response, error: {error}, purpose_options: {purpose_options}, user_choice: {user_choice}')

            if error:
                logger.error(f"LLM错误：{error}")
                return {'err_code': error, 'msg': odd_err_desc(error)}

            if user_choice is None:
                # 默认选择无工具
                user_choices = ['0']
            else:
                user_choices = self._extract_continuous_digits(user_choice)

            # 根据用户选择获取对应工具
            if user_choices and user_choices[0] != '0':
                # 可以判断工具，更新当前工具
                new_purpose = purpose_options[user_choices[0]]
                if new_purpose != self.current_purpose:
                    # 工具发生变化，重置补槽状态
                    self.current_purpose = new_purpose
                    self.last_recognized_tool = new_purpose  # 更新上次识别到的工具
                    self.is_slot_filling = False
                    # 清除之前的处理器
                    if new_purpose in self.processors:
                        del self.processors[new_purpose]
                logger.info(f"用户选择了工具：{self.tool_templates[self.current_purpose]['name']}")
                return {'err_code': 0, 'msg': '识别意图成功', 'tool_name': self.tool_templates[self.current_purpose]['name']}
            else:
                # 用户选择了"无工具/无法判断"
                if self.current_purpose and self.is_slot_filling:
                    logger.warning(f"无法判断意图，保留当前工具：{self.tool_templates[self.current_purpose]['name']}")
                    return {'err_code': 0, 'msg': odd_err_desc(EM_ERR_INTENT_RECOGNITION_NO_TOOL2), 'status': EM_ERR_INTENT_RECOGNITION_NO_TOOL2, 'tool_name': self.tool_templates[self.current_purpose]['name'], 'content': NO_TOOL_RESPONSE}
                else:
                    # 没有当前工具或不在补槽阶段，清空工具状态
                    self.current_purpose = ''
                    self.last_recognized_tool = ''  # 清除上次识别到的工具记录
                    self.is_slot_filling = False
                    logger.info("无法识别用户意图, 没有当前工具或不在补槽阶段，清空工具状态")
                    return {'err_code': EM_ERR_INTENT_RECOGNITION_NO_TOOL, 'msg': odd_err_desc(EM_ERR_INTENT_RECOGNITION_NO_TOOL), 'status': EM_ERR_INTENT_RECOGNITION_NO_TOOL, 'content': NO_TOOL_RESPONSE}

        except Exception as e:
            logger.error(f"识别用户意图时出错：{e}")
            return {'err_code': EM_ERR_INTENT_RECOGNITION_EXCEPTION, 'msg': odd_err_desc(EM_ERR_INTENT_RECOGNITION_EXCEPTION)}

    def load_processor(self, tool_name):
        """
        获取工具处理器
        :param tool_name: 工具名称
        :return: 工具处理器
        """
        if tool_name in self.processors:
            return self.processors[tool_name]

        tool_config = self.tool_templates.get(tool_name)
        if not tool_config:
            raise ValueError(f"未找到名为{tool_name}的工具配置")

        # 初始化槽位数据
        if tool_name not in self.tool_slots:
            self.tool_slots[tool_name] = get_slot_parameters_from_tool(tool_config["parameters"])

        # 将槽位数据传递给ToolProcessorImpl
        processor_class = self.load_tool_processor(self, tool_config)
        processor_class.slot = self.tool_slots[tool_name]
        self.processors[tool_name] = processor_class
        
        return self.processors[tool_name]

    def reset_current_tool(self):
        """清除当前工具，用于工具处理完成后"""

        # FIXME 已知chat_history没有正常清除，需要检查一下哪儿逻辑需要修改
        self.chat_history.clear()

        self.current_purpose = ''
        self.last_recognized_tool = ''
        self.is_slot_filling = False

        self.processors.clear()

        logger.info("工具处理完成，已清除当前工具")

    def generate_default_response(self, user_input):
        """
        生成无工具识别时的AI回复
        :param user_input: 用户输入
        :return: 默认回复
        """
        logger.debug(f'generate_default_response: {user_input}, tool_templates: {self.tool_templates}')

        purpose_description = {}
        index = 1
        
        for template_key, template_info in self.tool_templates.items():
            if isinstance(template_info, dict) and "description" in template_info:
                purpose_description[str(index)] = template_info["description"]
                index += 1
            else:
                # 如果不是字典或没有description键，使用默认值或跳过
                logger.warning(f"工具配置格式异常: {template_key}")
        options_prompt = "\n".join([f"{key}. {value}" for key, value in purpose_description.items()])
        options_prompt += "\n0. 无工具/无法判断"

        prompt = tool_prompts.PROMPT_NO_TOOL_RESPONSE.format(user_input, options_prompt)
        response, err_code = llm_chat(prompt, self.chat_history)

        if err_code != 0:
            logger.error(f"调用LLM API时出现错误：{err_code}")
            response = {"err_code": err_code, "msg": odd_err_desc(err_code), "data": "default_response"}

        return response if response else NO_TOOL_RESPONSE

    def is_tool_switched(self, user_input):
        """
        检测用户是否有切换工具的意图
        :param user_input: 用户的输入
        :return: 是否切换工具的意图, 错误码
        """
        if not self.current_purpose:
            return False
        
        current_tool_name = self.tool_templates[self.current_purpose]['name']
        last_tool_name = self.tool_templates[self.last_recognized_tool]['name'] if self.last_recognized_tool else "无"
        
        prompt = tool_prompts.PROMPT_DETECT_INTENT_SWITCH.format(
            current_tool_name, 
            #last_tool_name, 
            user_input
        )
        
        response, error = llm_chat(prompt, self.chat_history)
        logger.debug(f'is_tool_switched: {prompt}, response: {response}, error: {error}')
        if error:
            logger.error(f"LLM聊天错误: {error}")
            return False, error
        
        # 提取数字回复
        digits = self._extract_continuous_digits(response)
        if digits and digits[0] == '1':
            logger.info(f"检测到用户意图切换工具：{current_tool_name}")
            return True, error
        
        return False, error

    def check_response_finished(self, response):
        """
        检查用户输入是否完成
        :param user_input: 用户输入
        :return: 是否完成
        """
        logger.debug(f"check_response_finished: config.API_FORCE_ONESHOT={config.API_FORCE_ONESHOT}, response={type(response)}={response}")

        if config.API_FORCE_ONESHOT == 1:
            self.reset_current_tool()
            return True
        else:
            if type(response) == str:
                response = response.strip()
                try:
                    json_obj = json.loads(response)
                    response = json_obj
                except json.JSONDecodeError:
                    logger.error(f"无法解析为JSON: {response}")
                    return False
                # if not response.startswith("请问") and not response.startswith("抱歉，无法找到工具"):
                #     self.reset_current_tool()
                #     return True
            elif type(response) == dict:
                response = response
            else:
                logger.error(f"未知的响应类型: {type(response)}")
                return False
            
            # 如果 LLM 请求失败，会返回错误码，这里处理
            if "err_code" in response:
                if response.get("err_code") == 200 or response.get("err_code") == 0:
                    # 根据 tool_config 检查返回的json里是否每个required的slot都已经有值
                    tool_config = self.tool_templates[self.current_purpose]

                    logger.debug(f"工具: {self.current_purpose}, 检查必填槽位 for: {tool_config}")
                    ''''
                    {
                        'tool_name': 'INSTANT_MEETING', 
                        'name': '创建会议', 
                        'description': '立即创建会议。', 
                        'parameters': [
                            {'name': 'meeting_name', 'desc': '会议名称', 'type': 'string', 'required': True}, 
                            {'name': 'meeting_side', 'desc': '会议方/所属部门', 'type': 'string', 'required': False}
                        ], 
                        'enabled': True, 
                        'example': "输入：江苏省公安厅创建公安会议\n答：{ 'meeting_name': '公安会议', 'meeting_side': '江苏省公安厅' }"
                    }
                    '''

                    # 检查必填槽位
                    required_slots = [slot for slot in tool_config["parameters"] if slot.get("required", False)]

                    logger.debug(f"工具: {self.current_purpose}, 必填槽位: {required_slots}")
                    # required_slots: [{'name': 'meeting_name', 'desc': '会议名称', 'type': 'string', 'required': True}]
                    # 错误的response: {'err_code': 0, 'msg': 'success', 'data': '{"intent": "创建会议", "slots": [{"name": "meeting_name", "desc": "会议名称", "value": ""}, {"name": "meeting_side", "desc": "会议方/所属部门", "value": ""}]}'}
                    # 正确的response: {'err_code': 0, 'tool_name': 'SILENCE', 'message': '假装 [SILENCE] API调用成功', 'slots': {'enable': 0}, 'data': '假装 [SILENCE] API调用成功'}
                    is_required_slot_fullfilled = False

                    if len(required_slots) == 0:
                        is_required_slot_fullfilled = True
                        logger.debug(f"工具: {self.current_purpose}, 没有必填槽位")
                        return True
                    else:
                        is_required_slot_fullfilled = False

                        for slot in required_slots:
                            # 注意：如果slot的value为空字符串，或者是数字0，也需要返回true，因此暂时先判断LLM有没有返回这个slot，而不判断value
                            # {
                            #     'err_code': 0, 
                            #     'tool_name': 'SILENCE', 
                            #     'message': '[SILENCE] API调用成功', 
                            #     'slots': 
                            #     {
                            #         'enabled': 0
                            #     }, 
                            #     'data': '[模拟API模式] 假装成功！'
                            # }
                            param_slot_name = slot["name"]
                            param_slot = response.get("slots", {}).get(param_slot_name, "NA")

                            logger.debug(f"工具: {self.current_purpose}, 检查必填槽位 {param_slot_name} in response: {response}, param_slot: {param_slot}")

                            try:
                                # if response.get("slots", {}).get(param_slot_name) and response["slots"][param_slot_name]]:
                                if param_slot != "NA" :
                                    logger.debug(f"工具: {self.current_purpose}, 必填槽位 {param_slot_name} 已填，值为: {param_slot}")
                                    is_required_slot_fullfilled = True
                                else:
                                    # 缺少必填槽位
                                    logger.warning(f"工具: {self.current_purpose}, 缺少必填槽位 {param_slot_name}")
                                    return False
                                
                            except (KeyError, TypeError) as e:
                                logger.error(f"检查response槽位时出错: {e}, response: {response}")
                                return False
                            except Exception as e:
                                logger.error(f"检查response槽位时出错: {e}, response: {response}")
                                return False
                    
                    if is_required_slot_fullfilled:
                        logger.debug(f"工具: {self.current_purpose}, 必填槽位全部已填")
                        # self.reset_current_tool()
                        return True
                    else:
                        logger.warning(f"工具: {self.current_purpose}, 必填槽位未填")
                        return False
                else:
                    logger.warning(f"工具 {self.current_purpose} 返回错误码 {response.get('err_code')}:{EM_ERR_API_INVOKE_EXCEPTION}")
                    if response.get("err_code") == EM_ERR_API_INVOKE_EXCEPTION:
                        logger.warning(f"工具: {self.current_purpose}, API调用异常")
                        return True
                    return False
            return False

    def _compose_result(self, user_input, tool_name, response):
        result = {
                    "err_code": 0, 
                    "msg": response.get("message", "success"), 
                    "data": 
                    {
                        "answer": 
                        {
                            "err_code": 0, 
                            "tool_name": tool_name,
                            "data": "用户输入: {}".format(user_input), 
                            "message": response.get("message", "success")
                        }
                    }
        }

        return result
    
    def _is_terminate_command(self, user_input: str):
        """
        判断用户输入是否是退出对话命令
        FIXME 将退出对话命令放到配置文件中，会导致与一些命令词冲突（如：退出会议），暂时先挫一点这么写死，有空再来思考方案。
        :param user_input: 用户输入
        :return: 是否是退出对话命令
        """
        terminate_commands = ["再见", "拜拜", "退出对话", "结束对话"]
        return any(cmd in user_input for cmd in terminate_commands)

    def process_mcp_chat(self, messages, is_stream=False):
        """
        处理MCP格式的聊天请求
        :param messages: MCP格式的消息列表
        :param is_stream: 是否是流式响应
        :return: MCP格式的响应
        """
        # 获取最后一条用户消息
        user_input = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_input = msg.get('content')
                break
        
        if not user_input:
            return {"error": "No user message found"}
            
        # 使用现有的聊天处理逻辑
        response = self.process_oddagent_chat(user_input)
        
        # 转换为MCP兼容的格式
        return response

    def process_oddagent_chat(self, user_input: str, api_mode:int = 0):
        """
        处理OddAgent聊天
        :param user_input: 用户输入
        :return: 处理结果
        """
        logger.debug("==============================================================")
        logger.debug("==============================================================")
        logger.debug(f"process_oddagent_chat: {user_input}, self.current_purpose: {self.current_purpose}, api_mode: {api_mode}")
        logger.debug("==============================================================")
        logger.debug("==============================================================")

        # 添加用户输入到聊天记录
        self._save_chat_history(role="user", msg=user_input)

        # 优先处理退出对话服务
        is_terminate_command = self._is_terminate_command(user_input)
        if is_terminate_command:
            self.current_purpose = "chat_terminate"
            logger.info(f"用户请求退出对话")
            result = self._compose_result(user_input, "chat_terminate", {"err_code": 0, "msg": "已退出对话"})
            self._save_chat_history(role="assistant", msg="已退出对话")
            self.reset_current_tool()
            return result

        result = {}
        is_multi_round = False # 是否当前user_input是否是多轮交互

        # 如果没有当前工具，尝试识别意图
        if not self.current_purpose:
            result = self.recognize_intent(user_input)
        else:
            is_multi_round = True

        # 如果识别失败，返回错误码，并将聊天记录保存下来
        if "err_code" in result and result.get("err_code") != 0:
            result = {"err_code": result.get("err_code"), "msg": odd_err_desc(result.get("err_code")), "data": "用户输入: {}".format(user_input)}
            err_code = result.get("err_code")
            if err_code == EM_ERR_INTENT_RECOGNITION_NO_TOOL:
                self._save_chat_history(role="assistant", msg=NO_TOOL_RESPONSE)
                return result
            elif err_code == EM_ERR_INTENT_RECOGNITION_NO_TOOL2:
                self._save_chat_history(role="assistant", msg=NO_TOOL_RESPONSE)
                return result
        
            return result
        
        if not self.current_purpose:
            response = self.generate_default_response(user_input)
            logger.warning(f"没有工具，生成回复: {response}")
            # self.chat_history.append({"role": "assistant", "content": response.get("data", NO_TOOL_RESPONSE)})
            self._save_chat_history(role="assistant", msg=NO_TOOL_RESPONSE)

            return response

        # 有工具，标记为补槽阶段
        self.is_slot_filling = True
        logger.info(f'current_purpose: {self.current_purpose}')

        # 检测用户是否有切换工具的意图
        response = {}
        is_tool_switched = False

        # FIXME 暂时禁用切换工具。
        # 多轮交互场景下，现有架构会由于输入user_input无法带上前面的聊天记录，导致切换工具检测出错。
        # 因此，在多轮交互场景下，不检测切换工具意图。
        if not is_multi_round and self.current_purpose:
            is_tool_switched, error = self.is_tool_switched(user_input)

            # 优先处理退出对话服务
            if self.current_purpose == "chat_terminate":
                logger.info(f"用户请求退出对话")
                result = self._compose_result(user_input, "chat_terminate", result)
                self._save_chat_history(role="assistant", msg="已退出对话")
                self.reset_current_tool()
                # {'err_code': 0, 'tool_name': 'chat_terminate', 'message': '[chat_terminate] API调用成功', 'slots': {}, 'data': '[模拟API模式] 假装成功！'}
                return result

        if is_tool_switched:
            logger.warn(f"用户切换工具")
            # 重置当前工具（清除历史聊天记录），重新识别意图
            self.reset_current_tool()
            is_multi_round = False

            result = self.recognize_intent(user_input)
            if result.get("err_code") != 0:
                # # 移除最后一个用户输入
                # if len(self.chat_history) > 0:
                #     try:
                #         self.chat_history.pop()
                #     except IndexError:
                #         # 如果仍然发生IndexError，记录日志但不中断程序
                #         logger.warning("尝试从空的chat_history列表中弹出元素")

                result = {"err_code": result.get("err_code"), "msg": odd_err_desc(result.get("err_code")), "data": "用户输入: {}".format(user_input)}
                return result
            
            # 如果重新识别到工具，继续处理；否则生成无工具回复
            if self.current_purpose:
                processor: ToolProcessorImpl = self.load_processor(self.current_purpose)
                response = processor.process(user_input, self.chat_history, api_mode)
                finished = self.check_response_finished(response)
                if finished:
                    self.reset_current_tool()
            else:
                response = self.generate_default_response(user_input)
        else:
            logger.debug(f"用户未切换工具")
            response = {}
            if self.current_purpose in self.tool_templates:
                processor = self.load_processor(self.current_purpose)
                response = processor.process(user_input, self.chat_history, api_mode)

                finished = self.check_response_finished(response)
                if finished:
                    self.reset_current_tool()
                else:
                    self._save_chat_history(role="assistant", msg=response.get("data", NO_TOOL_RESPONSE))
                
            else:
                # 工具不存在，生成无工具回复的情况
                response = self.generate_default_response(user_input)

        # 添加助手回复到聊天记录
        '''
        qwen3-0.6b大模型异常未实际解析意图示例
        {
            'id': 'chatcmpl-b479f2b5f015442ca567be8c141ebf4d', 
            'object': 'chat.completion', 
            'created': 1763434328, 
            'model': 'qwen3-0.6b', 
            'choices': [
                {
                    'index': 0, 
                    'message': {
                        'role': 'assistant', 
                        'content': '您好，我是一个会议助手，请问您有什么会议业务需要处理吗？', 
                        'refusal': None, 
                        'annotations': None, 
                        'audio': None, 
                        'function_call': None, 
                        'tool_calls': [], 
                        'reasoning_content': None
                    }, 
                    'logprobs': None, 
                    'finish_reason': 'stop', 
                    'stop_reason': None, 
                    'token_ids': None
                }
            ], 
            'service_tier': None, 
            'system_fingerprint': None, 
            'usage': {
                'prompt_tokens': 243, 'total_tokens': 263, 'completion_tokens': 20, 'prompt_tokens_details': None
            }, 
            'prompt_logprobs':None, 'prompt_token_ids': None, 
            'kv_transfer_params': None
        }
        '''
        
        return response
    
    def _save_chat_history(self, role, msg):
        self.chat_history.append({"role": role, "content": msg})
        self.chat_history = self.chat_history[-config.LLM_MAX_HISTORY_MESSAGE:]
        logger.info(f"chat_history len={len(self.chat_history)}: content={self.chat_history}")

    def _extract_continuous_digits(self,text):
        # 使用正则表达式找到所有连续的数字
        continuous_digits = re.findall(r'\d+', text)
        return continuous_digits