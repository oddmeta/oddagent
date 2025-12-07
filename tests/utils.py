import logging
import json
import sys
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
                    # logger.debug(f"匹配成功: 预期值 '{expected_str}' 包含在实际值 '{actual_str}' 中")
                    current_matched = True
                    used_indices.add(i)  # 标记此实际值已被使用
                    break
            
            # 如果当前预期值未找到匹配，则整体不匹配
            if not current_matched:
                matched = False
                error_msg = f"预期值 '{expected_str}' 未在任何实际值中找到匹配"
                logger.error(f"匹配失败: {error_msg}")
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
            # print(f"expected_slot_name={expected_slot_name}, expected_slot_value={expected_slot_value}")
        
            # 处理值的类型转换（如果需要）
            for actual_slot_name, actual_slot_value in responsed_slots_dict.items():
                # print(f"actual_slot_name={actual_slot_name}, actual_slot_value={actual_slot_value}")

                # 将slot值转换成list
                actual_slot_value_list = str(actual_slot_value).split(',')
                expected_slot_value_list = str(expected_slot_value).split(',')
                # print(f"actual_slot_value_list={actual_slot_value_list}, expected_slot_value_list={expected_slot_value_list}")

                # 3. 判断两个list是否相等，其中expected_slot_value_list的值可能是 {"浙江","江苏"} ，而actual_slot_value_list的值可能是 {"浙江省厅","江苏省厅"}
                matched, error_msg = compare_slotvalue(expected_slot_value_list, actual_slot_value_list)

                # logger.debug(f"compare_slotvalue: matched={matched}, error_msg={error_msg}")

        if not matched:
            return False, f"槽位 '{slot_name}' 值不匹配，预期: {expected_value}, 响应: {actual_value}"

    # if str(expected_value) != str(actual_value):
    if not matched:
        return False, f"槽位 '{slot_name}' 值不匹配，预期: {expected_value}, 实际: {actual_value}， expected_slots_dict: {expected_slots_dict}"
    else:
        return True, "槽位匹配成功"


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