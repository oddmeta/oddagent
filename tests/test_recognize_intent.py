# 在文件顶部添加
# cython: language_level=3

import json
import requests
import time

from utils import load_config, compare_slots, _logging, TestItem, TestResults

TEST_CONFIG_FILE = '../modules/GAB/GAB_config.test.json'            # 请确保此路径正确
TEST_CONFIG_FILE = '../modules/xiaoluo/conference_config.test.json' # 请确保此路径正确
API_BASE_URL = 'http://127.0.0.1:5050/oddagent/chat'                # API地址

test_item_list = []
test_results = TestResults()
logger = _logging("test_recognize_intent")

def api_oddagent_chat(message):
    """调用api_oddagent_chat API"""
    try:
        response = requests.post(
            API_BASE_URL,
            json={
                'question': message, 
                'api_mode': 1 # 模拟API结果，0-不模拟，1-模拟，2-自定义API
                }, 
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        # 处理响应，与JavaScript代码保持一致
        return {
            'err_code': 200,
            'message': 'success',
            'data': data  # 保留原始响应数据
        }
    except Exception as e:
        logger.error(f"API调用失败: {str(e)}")
        return {
            'err_code': 500,
            'message': f'API调用失败: {str(e)}',
            'data': None
        }


def process_intent_tests(config):
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
            response = api_oddagent_chat(instruction)
            test_item.end_time = time.time()
            
            time_costs = test_item.end_time - test_item.start_time

            # 打印响应
            logger.debug(f"指令 '{instruction}' 的响应: {json.dumps(response, ensure_ascii=False, indent=2)}")

            ## 成功示例 
            # {
            #   "err_code": 200,
            #   "message": "success",
            #   "data": {
            #     "answer": {
            #       "tool_name": "MTS_DELETE",
            #       "data": "假装 [MTS_DELETE] API调用成功",
            #       "err_code": 0,
            #       "message": "假装 [MTS_DELETE] API调用成功",
            #       "slots": {
            #         "mt": "江苏省厅"
            #       }
            #     }
            #   }
            # }
            try:
                if response["data"]["answer"]["err_code"] != 0:
                    logger.error(f"意图失败！工具 {tool_name} 的指令 {index} 测试失败！")
                    test_results.failed += 1
                else:
                    responsed_tool_name = response["data"]["answer"]["tool_name"]
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

                        responsed_slots = response["data"]["answer"]["slots"]

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

def run_test():
    """运行测试"""
    global test_results
    global test_item_list

    logger.info("开始运行意图识别测试...")
    try:
        # 加载配置
        config = load_config(TEST_CONFIG_FILE)
        logger.info(f"成功加载配置文件: 包含 {len(config.get('agent_tool_list', []))} 个工具")
        
        # 处理测试意图
        process_intent_tests(config)
        
        logger.info("测试运行完成！")

        test_item_list.sort(key=lambda x: (x.tool_name, x.instruction))
        print_test_results(test_item_list, test_results)

    except Exception as e:
        logger.error(f"测试运行失败: {str(e)}")
        raise


if __name__ == '__main__':
    run_test()