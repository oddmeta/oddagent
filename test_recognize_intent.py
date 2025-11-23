# 在文件顶部添加
# cython: language_level=3

from typing import Optional
import sys
import json
import requests
import time
import logging
from io import StringIO

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)


TEST_CONFIG_FILE = 'modules/GAB/GAB.json'               # 请确保此路径正确
API_BASE_URL = 'http://localhost:5050/oddagent/chat'    # API地址


class TestItem:
    def __init__(self, tool_name: str, instruction: str):
        self.tool_name: str = tool_name
        self.instruction: str = instruction
        self.responsed_tool_name: str = ""
        self.success: bool = False
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

class TestResults:
    def __init__(self):
        self.total_intents = 0
        self.total_tests = 0
        self.failed = 0
        self.success_intent = 0
        self.success_intent_and_slots = 0

test_item_list = []
test_results = TestResults()

def load_config(config_file):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"配置文件未找到: {config_file}")
        # 尝试备用路径
        alternate_path = 'tests/GAB语音指令意图配置.json'
        logger.info(f"尝试备用路径: {alternate_path}")
        try:
            with open(alternate_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"备用配置文件也未找到: {alternate_path}")
            raise
    except json.JSONDecodeError:
        logger.error(f"配置文件格式错误: {config_file}")
        raise


def api_oddagent_chat(message):
    """调用api_oddagent_chat API"""
    try:
        response = requests.post(
            API_BASE_URL,
            json={'question': message},  # 修改为question字段
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

def compare_slotvalue(expected_slot_value_list, actual_slot_value_list):
    matched = True
    error_msg = ""
    # 检查两个列表长度是否相同
    if len(expected_slot_value_list) != len(actual_slot_value_list):
        matched = False
        error_msg = f"列表长度不匹配，预期: {len(expected_slot_value_list)}, 实际: {len(actual_slot_value_list)}"
    else:
        # 初始化匹配标志和已匹配的实际值索引集合
        matched = True
        used_indices = set()
        
        # 遍历预期值列表
        for expected_val in expected_slot_value_list:
            # 将预期值转换为字符串
            expected_str = str(expected_val)
            # 标记当前预期值是否找到匹配
            current_matched = False
            
            # 遍历实际值列表
            for i, actual_val in enumerate(actual_slot_value_list):
                # 如果实际值索引已使用或当前预期值与实际值类型不匹配，则跳过
                if i in used_indices:
                    continue
                    
                # 将实际值转换为字符串
                actual_str = str(actual_val)
                
                # 检查预期值是否包含在实际值中
                if expected_str in actual_str:
                    print(f"匹配成功: 预期值 '{expected_str}' 包含在实际值 '{actual_str}' 中")
                    current_matched = True
                    used_indices.add(i)  # 标记此实际值已被使用
                    break
            
            # 如果当前预期值未找到匹配，则整体不匹配
            if not current_matched:
                matched = False
                error_msg = f"预期值 '{expected_str}' 未在任何实际值中找到匹配"
                print(f"匹配失败: {error_msg}")
                break
    return matched, error_msg

def compare_slots(expected_slots, responsed_slots):
    """
    比较expected_slots和responsed_slots是否匹配
    :param expected_slots: 预期的槽位数据，格式为{"tool_name": "工具名", "slots": {"槽位名": "值"}}
    :param responsed_slots: 实际响应的槽位数据
    :return: (是否匹配, 错误信息)
    """
    matched = True
    error_msg = ""
    # 检查expected_slots格式
    if not isinstance(expected_slots, dict):
        return False, "expected_slots格式错误，应为字典"
    
    expected_slots_dict = expected_slots  # 直接使用expected_slots作为槽位字典
    
    # 转换responsed_slots为字典格式（如果它是列表格式）
    responsed_slots_dict = {}
    if isinstance(responsed_slots, list):
        # 如果是列表格式，如[{"name": "槽位名", "value": "值"}, ...]
        for slot in responsed_slots:
            if isinstance(slot, dict) and "name" in slot and "value" in slot:
                responsed_slots_dict[slot["name"]] = slot["value"]
    elif isinstance(responsed_slots, dict):
        # 如果已经是字典格式
        responsed_slots_dict = responsed_slots
    else:
        return False, "responsed_slots格式错误，应为列表或字典"
    
    # 比较槽位
    # 1. 检查expected_slots中的所有槽位是否都存在且值匹配
    matched = True
    for slot_name, expected_value in expected_slots_dict.items():
        if slot_name not in responsed_slots_dict:
            return False, f"缺少预期的槽位: {slot_name}"
        
        actual_value = responsed_slots_dict[slot_name]

        # 2. 检查实际响应的槽位是否都存在且值匹配
        for expected_slot_name, expected_slot_value in expected_slots_dict.items():
            print(f"expected_slot_name={expected_slot_name}, expected_slot_value={expected_slot_value}")
        
            # 处理值的类型转换（如果需要）
            for actual_slot_name, actual_slot_value in responsed_slots_dict.items():
                print(f"actual_slot_name={actual_slot_name}, actual_slot_value={actual_slot_value}")

                # 将slot值转换成list
                actual_slot_value_list = str(actual_slot_value).split(',')
                expected_slot_value_list = str(expected_slot_value).split(',')
                print(f"actual_slot_value_list={actual_slot_value_list}, expected_slot_value_list={expected_slot_value_list}")

                # 3. 判断两个list是否相等，其中expected_slot_value_list的值可能是 {"浙江","江苏"} ，而actual_slot_value_list的值可能是 {"浙江省厅","江苏省厅"}
                matched, error_msg = compare_slotvalue(expected_slot_value_list, actual_slot_value_list)

                logger.debug(f"compare_slotvalue: matched={matched}, error_msg={error_msg}")

        if not matched:
            return False, f"槽位 '{slot_name}' 值不匹配，预期: {expected_value}, 响应: {actual_value}"

    # if str(expected_value) != str(actual_value):
    if not matched:
        return False, f"槽位 '{slot_name}' 值不匹配，预期: {expected_value}, 实际: {actual_value}， expected_slots_dict: {expected_slots_dict}"
    else:
        return True, "槽位匹配成功"

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
            
            logger.info(f"测试指令 {index}/{len(test_instructions)}: {instruction}, test_answers[index]={test_answers[index-1]}")

            # 调用API
            test_item.start_time = time.time()
            response = api_oddagent_chat(instruction)
            test_item.end_time = time.time()
            
            # 打印响应
            logger.info(f"[{test_item.start_time:.6f} - {test_item.end_time:.6f}] 指令 '{instruction}' 的响应: {json.dumps(response, ensure_ascii=False, indent=2)}")

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
                    print(f"意图失败！工具 {tool_name} 的指令 {index} 测试失败！")
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

                        logger.info(f"意图通过！工具 {tool_name} 的指令{index}={instruction}, 预期槽位：{expected_slots}, 实际槽位：{responsed_slots} ！")

                        is_match, error_msg = compare_slots(expected_slots, responsed_slots)
                        if is_match:
                            test_results.success_intent_and_slots += 1
                            test_item.success = True
                            print(f"测试通过！工具 {tool_name} 的指令 {index} 测试成功！slots匹配！")
                        else:
                            test_item.success = False
                            print(f"测试失败！工具 {tool_name} 的指令 {index} 测试失败！slots不匹配！expected: {expected_slots}, responsed: {responsed_slots}, error_msg: {error_msg}") 

                    else:
                        test_item.success = False
                        print(f"测试失败！工具 {tool_name}: {responsed_tool_name} 的指令 {index} 测试失败！")
                        test_results.failed += 1

            except KeyError:
                print(f"测试失败！工具 {tool_name} 的指令 {index} 响应格式错误！")
                test_results.failed += 1
            except Exception as e:
                print(f"测试失败！工具 {tool_name} 的指令 {index} 测试失败！")
                print(f"错误信息: {str(e)}")
                test_results.failed += 1

            print(f"\n=== 工具: {tool_name}, 指令 {index} ===")
            print(f"指令: {instruction}")
            print(f"响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
            print(f"测试结果:\n \
总意图={test_results.total_intents}\n \
总命令词={test_results.total_tests}\n \
意图通过={test_results.success_intent}/{count}，{test_results.success_intent/count:.2%} % \n \
意图槽位通过={test_results.success_intent_and_slots}/{count}，{test_results.success_intent_and_slots/count:.2%} % \n \
测试失败={test_results.failed}")

            # 睡3秒，避免对服务器压力过大
            time.sleep(1)

def print_test_results(test_items: TestItem, test_results: TestResults):
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
        logger.info(f"成功加载配置文件，包含 {len(config.get('agent_tool_list', []))} 个工具")
        
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