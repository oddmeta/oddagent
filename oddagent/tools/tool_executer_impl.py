# -*- coding: utf-8 -*-

import json
import requests

from oddagent.tools import tool_prompts
from oddagent.tools.tool_executer import ToolExecuter 
from oddagent.tools.tool_llm import  llm_chat
from oddagent.modules.module_tool import get_slot_parameters_from_tool, get_dynamic_example
from oddagent.odd_agent_logger import logger
from oddagent.config_loader import config
from oddagent.logic.api_request_composer import api_request_composer

from oddagent.tools.tool_executer_meeting import MeetingExecuter, MeetingConfig

from oddagent.logic.odd_agent_error import EM_ERR_SLOT_PARSE_INVALID_SLOT_NAME, EM_ERR_SLOT_PARSE_EXCEPTION, EM_ERR_API_INVOKE_EXCEPTION
from oddagent.logic.odd_agent_error import OddException, odd_err_desc

class ToolExecuterImpl(ToolExecuter):
    def __init__(self, tool_config):
        parameters = tool_config["parameters"]
        self.tool_config = tool_config
        self.tool_name = tool_config["tool_name"]
        self.name = tool_config["name"]
        self.slot_template = get_slot_parameters_from_tool(parameters)
        self.slot_dynamic_example = get_dynamic_example(tool_config)
        self.slot = get_slot_parameters_from_tool(parameters)
        self.tool_prompts = tool_prompts
        self.tool_api_url = tool_config.get("tool_api_url", "")
        self.tool_api_method = tool_config.get("tool_api_method", "POST")

        # 会议处理器
        self.meeting_executer = MeetingExecuter(meeting_config=MeetingConfig())

    def execute(self, slots_data, api_mode : int = 1):
        """
        处理用户输入，更新槽位，检查完整性，以及与用户交互
        :param slots_data: 槽位数据
        :return: 处理结果
        """

        logger.debug(f'工具名称：{self.tool_name}, 槽位数据：{slots_data}, api_mode: {api_mode}')

        # cython不支持match case，重写为if else
        # match config.API_FAKE_API_RESULT:
        if api_mode == 0:
            try:
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
                    result = {"error": f"API调用失败，状态码: {response.status_code}"}
                    logger.error(f"{result}")
            except requests.RequestException as e:
                result = {"error": f"API请求异常: {e}"}
                logger.error(f"{result}")
            except Exception as e:
                result = {"error": f"处理API响应时出错: {e}"}
                logger.error(f"{result}")
            logger.debug(f"API调用响应: {json.dumps(result, ensure_ascii=False)}")
            return result
        elif api_mode == 1:
            result = {
                "err_code": 0, 
                "tool_name": self.tool_name, 
                "message": f"[{self.tool_name}] API调用成功", 
                "slots": slots_data,
                "data": "[模拟API模式] 假装成功！"
            }

            return result
        elif api_mode == 2:
            if self.tool_name == "meeting_create":
                meeting_name = slots_data["meeting_name"]
                if not meeting_name:
                    raise OddException(EM_ERR_API_INVOKE_EXCEPTION, "会议名称不能为空")
                result = self.meeting_executer.create_conference(name=meeting_name)
                # ✅ 创建会议 成功 json响应: 
                # {"success": 1, "description": "操作成功", "conf_id": "0050137", "meeting_id": "87496f6f64de4febb0b2460c577762b3", "machine_room_moid": "7b010e6a-7689-11f0-9a30-00141027aef9"}
                conf_id = result.get("conf_id")
                if not conf_id:
                    raise OddException(EM_ERR_API_INVOKE_EXCEPTION, "创建会议失败")
                
                logger.info(result)

                # 保存会议ID
                self.meeting_executer.meeting_config.set_confid(conf_id)

                logger.debug("保存会议ID：%s" % self.meeting_executer.meeting_config.CONF_ID)

                result = {
                    "err_code": 0, 
                    "tool_name": self.tool_name, 
                    "message": f"[{self.tool_name}] API调用成功", 
                    "slots": slots_data,
                    "data": result
                }

                return result
            elif self.tool_name == "meeting_invite":
                # 如果会议不存在，返回错误
                conf_id = self.meeting_executer.meeting_config.get_confid()
                if not conf_id:
                    logger.warning(f"self.meeting_executer.meeting_config:{self.meeting_executer.meeting_config.dump()}")
                    raise OddException(EM_ERR_API_INVOKE_EXCEPTION, "请先创建会议")

                # 获取终端信息
                invitees =slots_data["invitees"]
                # 参会人列表，逗号分隔
                invitees_list = invitees.split(",")
                logger.debug(f"[会议ID: {conf_id}] 参会人列表: {invitees_list}")

                # 检查输入
                if len(invitees_list) > 1:
                    result = {"success": 0, "message": f"本demo的API暂只支持一次邀请一个人入会，但是您输入了多个参会人：{invitees_list}"}
                    return result
                
                # 查询参会人信息
                result = self.meeting_executer.search_accounts_by_alias(invitees_list[0])
                invitee_info = result.get("accounts")
                
                if len(invitee_info) > 1:
                    # TODO 存在多个参会人时，应将整个列表返回给前端，让用户自己选择第几个参会人邀请入会
                    invitee_info = invitee_info[0]
                elif len(invitee_info) == 0:
                    # TODO 找不到参会人时，应返回错误信息给前端
                    invitee_info = None
                    result = {"success": 1, "message": f"邀请参会人{invitee_info}成功"}
                    logger.error(f"{result}")

                else:
                    invitee_info = invitee_info[0]

                    # 参会人信息: 
                    # [
                    #     {
                    #         'account': 'wgh1', 
                    #         'account_type': 0, 
                    #         'enable': 1, 
                    #         'name': 'wgh1', 
                    #         'email': '', 
                    #         'mobile': '', 
                    #         'password': '21218cca77804d2ba1922c33e0151105', 
                    #         'binded': 0, 
                    #         'e164': '5406260000209', 
                    #         'sex': 1, 
                    #         'date_of_birth': '', 'ext_num': '', 'fax': '', 
                    #         'office_location': '', 
                    #         'departments': [{'department_moid': '73a3133a-9ec4-4928-9d1a-cc91b4e6c12d', 'department_name': '未分组用户', 'department_position': ''}], 
                    #         'job_num': '', 'limited': 0, 'account_moid': '7fbcd163-a86d-4123-a8a0-2ce7b0009786', 
                    #         'account_jid': '7fbcd163-a86d-4123-a8a0-2ce7b0009786@2q5f94m6'
                    #     }
                    # ]

                    # mt_list = [
                    #     {
                    #         "account": "5406260000009",
                    #         "account_type": 5,
                    #         "bitrate": 2048,
                    #         "protocol": 1,
                    #         "forced_call": 0,
                    #         "call_mode": 0
                    #     }
                    # ]

                    invitee_info = [{
                        "account": invitee_info["e164"], 
                        "account_type": 5,
                        "bitrate": 2048,
                        "protocol": 1,
                        "forced_call": 0,
                        "call_mode": 0
                    }]

                    logger.debug(f"[会议ID: {conf_id}], 参会人信息: {invitee_info}")

                    # 邀请入会
                    result = self.meeting_executer.invite_mt(conf_id, invitee_info)
                    logger.debug(f"[会议ID: {conf_id}], 邀请参会人{invitee_info}。结果: {result}")

                    # # 遍历参会人列表，邀请参会人入会
                    # for invitee in invitees_list:
                    #     invitee = invitee.strip()
                    #     if invitee:
                    #         mt_name = invitee
                    #         mt_id = self.meeting_executer.query_mt_info(mt_name=mt_name)
                    #         if mt_id:
                    #             logger.info(f"开始邀请：{mt_name}")
                    #             self.meeting_executer.invite_mt(conf_id=conf_id, mt_list=[mt_id])
                    #         else:
                    #             logger.error(f"mt_name: {mt_name} not found")

                    # 拼接入会成功响应
                    result = {"success": 1, "message": f"邀请参会人{invitee_info}成功"}

                    # 获取在会中的mt列表
                    mt_list = self.meeting_executer.get_mts_in_meetings(conf_id)
                    logger.debug(f"[会议ID: {conf_id}], 在会中的mt列表: {mt_list}")

                    # 将成员列表添加到全局变量中
                    success = mt_list.get("success", 0)
                    if success == 1:
                        mt_list = mt_list.get("mts", [])
                        self.meeting_executer.meeting_config.set_meeting_termlist(mt_list)
                    else:
                        logger.error(f"获取会议{conf_id}的终端列表失败: {mt_list}")

                result = {
                    "err_code": 0, 
                    "tool_name": self.tool_name, 
                    "message": f"[{self.tool_name}] API调用成功", 
                    "slots": slots_data,
                    "data": result
                }

                return result
            elif self.tool_name == "meeting_leave_meeting":
                # 如果会议不存在，返回错误
                conf_id = self.meeting_executer.meeting_config.get_confid()
                if not conf_id:
                    logger.warning(f"self.meeting_executer.meeting_config:{self.meeting_executer.meeting_config.dump()}")
                    raise OddException(EM_ERR_API_INVOKE_EXCEPTION, "请先创建会议")

                result = {"success": 1, "message": f"成功退出会议:{conf_id}"}

                result = {
                    "err_code": 0, 
                    "tool_name": self.tool_name, 
                    "message": f"[{self.tool_name}] API调用成功", 
                    "slots": slots_data,
                    "data": result
                }

                return result
            elif self.tool_name == "meeting_dropout":
                # 如果会议不存在，返回错误
                conf_id = self.meeting_executer.meeting_config.get_confid()
                if not conf_id:
                    logger.warning(f"self.meeting_executer.meeting_config:{self.meeting_executer.meeting_config.dump()}")
                    raise OddException(EM_ERR_API_INVOKE_EXCEPTION, "请先创建会议")

                # 获取终端信息
                mt =slots_data["participants"]
                # 参会人列表，逗号分隔
                mt_list = mt.split(",")
                logger.debug(f"[会议ID: {conf_id}] 挂断: {mt_list}")

                # 检查输入
                if len(mt_list) > 1:
                    result = {"success": 0, "message": f"暂只支持一次挂断一个人，但是您输入了多个参会人：{mt_list}"}
                    return result
                elif len(mt_list) == 0:
                    result = {"success": 0, "message": f"请输入要挂断的参会人"}
                    return result
                
                # 查询参会成员列表中有没有这个人
                found = False
                meeting_termlist = self.meeting_executer.meeting_config.get_meeting_termlist()
                for item in meeting_termlist:
                    if item["alias"] == mt_list[0]:
                        mt_id = item["mt_id"]
                        found=True
                        break
                if not found:
                    result = {"success": 0, "message": f"没有找到该参会成员:{mt_list[0]}"}
                    logger.error(f"result:{result}")
                    return result
                
                # 拼接mt参数
                # mt_list = [
                #     {"mt_id": "1"}
                # ]
                mt_id = {"mt_id": mt_id}

                result = self.meeting_executer.hangup_mt(self.meeting_executer.meeting_config.get_confid(), [mt_id])

                # 挂断终端成功响应
                result = {"success": 1, "message": f"挂断参会人{mt_list[0]}成功"}

                result = {
                    "err_code": 0, 
                    "tool_name": self.tool_name, 
                    "message": f"[{self.tool_name}] API调用成功", 
                    "slots": slots_data,
                    "data": result
                }

                return result
            elif self.tool_name == "send_dual_stream":
                conf_id = self.meeting_executer.meeting_config.get_confid()
                if not conf_id:
                    logger.warning(f"self.meeting_executer.meeting_config:{self.meeting_executer.meeting_config.dump()}")
                    raise OddException(EM_ERR_API_INVOKE_EXCEPTION, "请先创建会议")
                # FIXME 如果走会管API的话，需要传一个终端ID。暂写死会议中的第一个终端
                mt_id = self.meeting_executer.meeting_config.get_meeting_termlist()[0]["mt_id"]

                result = self.meeting_executer.send_dual_stream(conf_id=conf_id, mt_id=mt_id)
                result = {"success": 1, "message": f"发送双流成功"}

                result = {
                    "err_code": 0, 
                    "tool_name": self.tool_name, 
                    "message": f"[{self.tool_name}] API调用成功", 
                    "slots": slots_data,
                    "data": result
                }

                return result
            elif self.tool_name == "stop_dual_stream":
                conf_id = self.meeting_executer.meeting_config.get_confid()
                if not conf_id:
                    logger.warning(f"self.meeting_executer.meeting_config:{self.meeting_executer.meeting_config.dump()}")
                    raise OddException(EM_ERR_API_INVOKE_EXCEPTION, "请先创建会议")
                # FIXME 如果走会管API的话，需要传一个终端ID。暂写死会议中的第一个终端
                mt_id = self.meeting_executer.meeting_config.get_meeting_termlist()[0]["mt_id"]

                result = self.meeting_executer.stop_dual_stream(conf_id=conf_id, mt_id=mt_id)
                result = {"success": 1, "message": f"关闭双流成功"}

                result = {
                    "err_code": 0, 
                    "tool_name": self.tool_name, 
                    "message": f"[{self.tool_name}] API调用成功", 
                    "slots": slots_data,
                    "data": result
                }

                return result
            elif self.tool_name == "meeting_end":
                conf_id = self.meeting_executer.meeting_config.get_confid()
                if not conf_id:
                    logger.warning(f"self.meeting_executer.meeting_config:{self.meeting_executer.meeting_config.dump()}")
                    raise OddException(EM_ERR_API_INVOKE_EXCEPTION, "请先创建会议")
                result = self.meeting_executer.end_conference(conf_id=conf_id)

                result = {
                    "err_code": 0, 
                    "tool_name": self.tool_name, 
                    "message": f"[{self.tool_name}] API调用成功", 
                    "slots": slots_data,
                    "data": result
                }

                return result
            else:
                result = {"err_code": 500, "msg": "不支持的tool_name", "data": "不支持的tool_name: " + self.tool_name}

                result = {
                    "err_code": 0, 
                    "tool_name": self.tool_name, 
                    "message": f"[{self.tool_name}] API调用成功", 
                    "slots": slots_data,
                    "data": result
                }

                return result


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
            result, err_code = llm_chat(prompt, chat_history)

            if err_code != 0:
                logger.error("处理API结果时出错: %s", err_code)
                result = {"err_code": EM_ERR_SLOT_PARSE_EXCEPTION, "msg": odd_err_desc(EM_ERR_SLOT_PARSE_EXCEPTION), "data": "execute_result_parser"}
                return result
            
            if result:
                return result
            else:
                return {"err_code": EM_ERR_SLOT_PARSE_INVALID_SLOT_NAME, "msg": odd_err_desc(EM_ERR_SLOT_PARSE_INVALID_SLOT_NAME), "data": "execute_result_parser"}
                
        except Exception as e:
            logger.error(f"处理API结果时出错: {e}")
            return {"err_code": EM_ERR_SLOT_PARSE_EXCEPTION, "msg": odd_err_desc(EM_ERR_SLOT_PARSE_EXCEPTION), "data": "execute_result_parser"}
            