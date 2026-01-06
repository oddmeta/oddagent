#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OddAgent MCP协议测试程序

这个程序用于测试OddAgent的MCP协议实现，支持测试健康检查和聊天完成端点。
"""

import argparse
import json
import requests
import time
import sys
from datetime import datetime
from typing import Optional

from utils import load_config, compare_slots, _logging, TestItem, TestResults

TEST_CONFIG_FILE = '../modules/GAB/GAB_config.test.json'                # 请确保此路径正确
TEST_CONFIG_FILE = '../modules/xiaoluo/conference_config.test.json'     # 请确保此路径正确
MCP_BASE_URL = 'http://172.16.237.141:5050'                             # API地址
MCP_BASE_URL = 'http://172.16.237.141:5051'                             # API地址
MCP_BASE_URL = 'http://127.0.0.1:5050'                                  # API地址

test_item_list = []
test_results = TestResults()
logger = _logging("test_mcp.log")

def load_config(config_file):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_file}")
        raise
    except json.JSONDecodeError:
        logger.error(f"配置文件格式错误: {config_file}")
        raise

def print_colored(text, color="default"):
    """打印带颜色的文本"""
    colors = {
        "default": "\033[0m",
        "green": "\033[32m",
        "blue": "\033[34m",
        "red": "\033[31m",
        "yellow": "\033[33m"
    }
    
    # Windows命令行可能不支持ANSI颜色
    if sys.platform.startswith('win'):
        print(text)
    else:
        print(f"{colors.get(color, colors['default'])}{text}{colors['default']}")

def test_health_check(base_url):
    """测试健康检查端点"""
    url = f"{base_url}/mcp/health"
    logger.info(f"\n测试健康检查端点: {url}")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=10)
        end_time = time.time()
        
        logger.info(f"响应状态码: {response.status_code}")
        logger.info(f"响应时间: {((end_time - start_time) * 1000):.2f} ms")
        
        if response.status_code == 200:
            try:
                data = response.json()
                logger.info("响应内容:")
                logger.info(json.dumps(data, indent=2, ensure_ascii=False))
                return True
            except json.JSONDecodeError:
                logger.error("错误: 响应不是有效的JSON格式")
                logger.error(response.text)
                return False
        else:
            logger.error(f"错误: 请求失败，状态码: {response.status_code}")
            logger.error(response.text)
            return False
    except Exception as e:
        logger.error(f"错误: {str(e)}")
        return False


def print_test_results(test_items: TestItem, test_results: TestResults):
    global logger
    """打印测试结果"""
    logger.info("========== 测试结果汇总 ==========")
    
    # 计算耗时统计信息
    durations = []
    for item in test_items:
        status = "通过" if item.success else "失败"
        duration = item.end_time - item.start_time if item.end_time and item.start_time else 0
        durations.append(duration)
        logger.info(f"[{status}] 工具: {item.tool_name}, 指令: {item.instruction}, 耗时: {duration:.2f}s")
    
    # 计算统计数据
    if durations:
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        logger.info(f"平均耗时: {avg_duration:.2f}s, 最大耗时: {max_duration:.2f}s,最小耗时: {min_duration:.2f}s")
    
    # 计算成功率
    logger.info(f"测试结果:\n \
                    总意图={test_results.total_intents}\n \
                    总命令词={test_results.total_tests}\n \
                    意图通过={test_results.success_intent}/{test_results.total_tests}，{test_results.success_intent/test_results.total_tests:.2%} % \n \
                    意图槽位通过={test_results.success_intent_and_slots}/{test_results.total_tests}，{test_results.success_intent_and_slots/test_results.total_tests:.2%} % \n \
                    测试失败={test_results.failed}")

    logger.info("==================================")

def test_chat_completion(base_url, model="odd-mcp", session_id=None, stream=False, message="请介绍一下自己"):
    """测试聊天完成端点"""
    url = f"{base_url}/mcp/chat/completions"
    logger.info(f"测试消息: {message}")
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是一个有用的助手"},
            {"role": "user", "content": message}
        ],
        "stream": stream,
        "api_mode": 1
    }
    
    if session_id:
        payload["session_id"] = session_id

    result = {}
    
    try:
        start_time = time.time()
        
        if stream:
            # 测试流式响应
            response = requests.post(url, json=payload, stream=True, timeout=60)
            response.raise_for_status()
            
            full_response = ""
            for chunk in response.iter_lines(decode_unicode=True):
                if chunk:
                    # 移除 'data: ' 前缀
                    if chunk.startswith('data: '):
                        chunk = chunk[6:]
                    if chunk != '[DONE]':
                        try:
                            data = json.loads(chunk)
                            if data.get('choices') and len(data['choices']) > 0:
                                content = data['choices'][0].get('delta', {}).get('content', '')
                                full_response += content
                        except json.JSONDecodeError:
                            logger.error(f"警告: 无法解析块: {chunk}")
            
            print()  # 换行
            return True, result
        else:
            # 测试非流式响应
            response = requests.post(url, json=payload, timeout=60)
            end_time = time.time()
            
            logger.debug(f"响应时间: {((end_time - start_time) * 1000):.2f} ms")

            if response.status_code == 200:
                try:
                    data = response.json()
                    # print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # 提取并打印助手回复
                    if data.get('choices') and len(data['choices']) > 0:
                        assistant_reply = data['choices'][0].get('message', {}).get('content', '')

                    if assistant_reply.find("err_code") != -1:
                        try:
                            # 首先尝试标准JSON解析（双引号）
                            assistant_reply = json.loads(assistant_reply)
                        except json.JSONDecodeError:
                            try:
                                # 如果失败，尝试Python字典解析（单引号）
                                import ast
                                assistant_reply = ast.literal_eval(assistant_reply)
                            except Exception as e:
                                logger.error(f"警告: 无法解析助手回复: {assistant_reply}")

                    result = assistant_reply

                    logger.info(f"测试结果: {assistant_reply}, type: {type(assistant_reply)}")

                    return True, result
                except json.JSONDecodeError:
                    logger.error("错误: 响应不是有效的JSON格式")
                    print(response.text)
                    return False, result
            else:
                logger.error(f"错误: 请求失败，状态码: {response.status_code}")
                print(response.text)
                return False, result
    except Exception as e:
        logger.error(f"错误: {str(e)}")
        return False, result


def process_mcp_tests(base_url, config):
    global test_results
    global test_item_list

    """处理意图测试"""
    if not config or 'agent_tool_list' not in config:
        logger.error("配置文件格式不正确，缺少'agent_tool_list'字段")
        return

    test_results.total_intents = len(config['agent_tool_list'])
    # test_results.total_tests = sum(len(tool.get('test_instructions', [])) for tool in config['agent_tool_list'])
    for tool in config['agent_tool_list']:
        if not tool.get('enabled', False): 
             continue
        test_results.total_tests += len(tool.get('test_instructions', []))
    test_results.success_intent_and_slots = 0
    test_results.success_intent = 0
    test_results.failed = 0

    count = 0

    # 遍历每个工具
    for tool in config['agent_tool_list']:
        tool_name = tool.get('tool_name', '未知工具')
        logger.info("==================================================================")
        logger.info(f"开始测试工具: {tool_name}")
        logger.info("==================================================================")

        enabled = tool.get('enabled', False)
        if not enabled:
            logger.warning(f"工具 {tool_name} 未启用，跳过测试")
            continue

        # 检查是否有example_instructs
        test_instructions = tool.get('test_instructions', [])
        if not test_instructions:
            logger.warning(f"工具 {tool_name} 没有test_instructions字段")
            continue

        test_answers = tool.get('test_answers', [])
        if not test_answers:
            logger.warning(f"工具 {tool_name} 没有test_answers字段")
            continue
        
        # 遍历每个指令
        for index, instruction in enumerate(test_instructions, 1):
            test_item = TestItem(tool_name, instruction)
            test_item_list.append(test_item)
            count += 1
            
            # logger.info(f"测试指令 {index}/{len(test_instructions)}: {instruction}, test_answers[index]={test_answers[index-1]}")

            # 调用API
            test_item.start_time = time.time()
            success, response = test_chat_completion(base_url=base_url, message=instruction)
            test_item.end_time = time.time()
            
            time_costs = test_item.end_time - test_item.start_time

            # 打印响应
            logger.debug(f"指令 '{instruction}' 的响应: {json.dumps(response, ensure_ascii=False, indent=2)}")

            ## 成功示例 
            # {
            #       "tool_name": "MTS_DELETE",
            #       "data": "假装 [MTS_DELETE] API调用成功",
            #       "err_code": 0,
            #       "message": "假装 [MTS_DELETE] API调用成功",
            #       "slots": {
            #         "mt": "江苏省厅"
            #       }
            # }
            try:
                if not success or response["err_code"] != 0:
                    logger.error(f"意图失败！工具 {tool_name} 的指令 {index} 测试失败！")
                    test_results.failed += 1
                else:
                    responsed_tool_name = response["tool_name"]
                    if responsed_tool_name == tool_name:
                        test_results.success_intent += 1

                        # 检查slots是否匹配
                        # 处理instruction可能是字符串的情况
                        if isinstance(test_answers[index-1], dict):
                            expected_slots = test_answers[index-1].get("slots", {})
                        else:
                            # 如果instruction是字符串，可能需要根据实际情况进行解析或设置为空字典
                            # 假设字符串指令没有关联的slots期望
                            expected_slots = {}

                        responsed_slots = response["slots"]

                        logger.info(f"[耗时：{time_costs:.2f}s], {index}/{len(test_instructions)}. 意图通过！工具 {tool_name} 的指令{index}={instruction}, 预期槽位：{expected_slots}, 实际槽位：{responsed_slots} ！")

                        is_match, error_msg = compare_slots(expected_slots, responsed_slots)
                        if is_match:
                            test_results.success_intent_and_slots += 1
                            test_item.success = True
                            # print(f"测试通过！工具 {tool_name} 的指令 {index} 测试成功！slots匹配！")
                        else:
                            test_item.success = False
                            logger.error(f"测试失败！工具 {tool_name} 的指令 {index} 测试失败！slots不匹配！expected: {expected_slots}, responsed: {responsed_slots}, error_msg: {error_msg}") 

                    else:
                        test_item.success = False
                        logger.error(f"测试失败！工具 {tool_name}: {responsed_tool_name} 的指令 {index} 测试失败！")
                        test_results.failed += 1

            except KeyError:
                logger.error(f"测试失败！工具 {tool_name} 的指令 {index} 响应格式错误！")
                test_results.failed += 1
            except Exception as e:
                logger.error(f"测试失败！工具 {tool_name} 的指令 {index} 测试失败！错误信息: {str(e)}")
                test_results.failed += 1

            logger.info(f"=== 工具: {tool_name}, 指令 {index}: {instruction}")
            logger.debug(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
            logger.info(f"测试结果: \
总意图={test_results.total_intents}, 总命令词={test_results.total_tests}, \
意图通过={test_results.success_intent}/{count}，{test_results.success_intent/count:.2%} % , \
意图槽位通过={test_results.success_intent_and_slots}/{count}，{test_results.success_intent_and_slots/count:.2%} %, \
测试失败={test_results.failed}")

            # 睡3秒，避免对服务器压力过大
            time.sleep(1)


def main():
    global test_results
    global test_item_list

    # 确保URL不以斜杠结尾
    base_url = MCP_BASE_URL.rstrip('/')
    config = load_config(TEST_CONFIG_FILE)

    """运行所有测试"""
    logger.info(f"=== OddAgent MCP协议测试套件 ===")
    logger.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"测试目标: {base_url}")

    # 测试健康检查
    logger.info(f"测试 健康检查")
    if test_health_check(base_url):
        process_mcp_tests(base_url, config)

        logger.info("测试运行完成！")

        test_item_list.sort(key=lambda x: (x.tool_name, x.instruction))
        print_test_results(test_item_list, test_results)

    else:
        logger.error("健康检查失败，测试终止")

if __name__ == "__main__":
    main()