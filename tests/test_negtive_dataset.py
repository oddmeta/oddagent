from typing import Optional
import requests
import time

from utils import load_config, compare_slots, _logging, TestItem, TestResults

LOG_FILE = "test_negitive_dataset.log"
API_BASE_URL = 'http://127.0.0.1:5050/oddagent/chat'    # API地址
DATASET_FILE = "../docs/other_unknown examples.txt"

logger = _logging(LOG_FILE)

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

def load_dataset(file_path: str) -> list:
    """加载数据集文件"""
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 处理每一行，去掉"- "前缀
        processed_lines = []
        for line in lines:
            # 去除行尾换行符
            line = line.rstrip('\n')
            # 如果行以"- "开头，去掉这个前缀
            if line.startswith('- '):
                processed_line = line[2:]
            else:
                processed_line = line
            processed_lines.append(processed_line)

    except FileNotFoundError:
        print(f"错误：找不到文件 '{file_path}'")
    except Exception as e:
        print(f"处理文件时出错: {str(e)}")

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
    
def test_negitive_dataset(file_path: str, skip_lines: int = 0):
    """加载数据集文件"""
    logger.info(f"开始测试数据集: {file_path}")
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 跳过前skip_lines行
        lines = lines[skip_lines:]

        # 处理每一行，去掉"- "前缀
        processed_lines = []
        for line in lines:
            # 去除行尾换行符
            line = line.rstrip('\n')
            # 如果行以"- "开头，去掉这个前缀
            if line.startswith('    - '):
                processed_line = line[6:]
            else:
                processed_line = line

            test_item = TestItem(tool_name="", instruction=processed_line)
            test_item_list.append(test_item)

            test_item.start_time = time.time()
            response = api_oddagent_chat(processed_line)
            test_item.end_time = time.time()
            time_cost = test_item.end_time - test_item.start_time
            '''
            {
            "data": "用户输入: 先入为主",
            "err_code": 320002,
            "msg": "无法识别用户意图, 而且没有当前工具或不在补槽阶段。清空工具状态。"
            }

            {
                'err_code': 200, 
                'message': 'success', 
                'data': 
                {
                    'answer': 
                    {
                        'data': '用户输入: 更何况', 'err_code': 320002, 'msg': '无法识别用户意图, 而且没有当前工具或不在补槽阶段。清空工具状态。'
                    }
                }
            }
            '''
            if response["err_code"] == 200:
                try: 
                    if response["data"]["answer"]["err_code"] == 320002:
                        test_item.success = True
                        test_results.success_intent += 1
                    else:
                        test_item.success = False
                        test_results.failed += 1
                except Exception as e:
                    logger.error(f"处理响应数据时出错: {str(e)}, response: {response}")
                    test_item.success = False
                    test_results.failed += 1
            else:
                test_item.success = False
                test_results.failed += 1

            if test_item.success:
                logger.info(f"[{time_cost:.4f}s]测试项: {processed_line}, 成功: {test_results.success_intent}, 失败: {test_results.failed}")
            else:
                logger.error(f"[{time_cost:.4f}s]测试项: {processed_line}, 成功: {test_results.success_intent}, 失败: {test_results.failed}, response: {response}")

    except FileNotFoundError:
        logger.exception(f"错误：找不到文件 '{file_path}'")
    except Exception as e:
        logger.exception(f"处理文件时出错: {str(e)}")

if __name__ == '__main__':
    skip_lines = 2980
    test_negitive_dataset(DATASET_FILE, skip_lines)
