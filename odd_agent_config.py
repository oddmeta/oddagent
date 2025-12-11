import os

DEBUG = True

# LLM 模型参数，
GPT_URL = os.environ.get("GPT_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions")
MODEL = os.environ.get("MODEL", "qwen3-30b-a3b")
LLM_TYPE = os.environ.get("LLM_TYPE", "Qwen3-30B-A3B-Instruct")
API_KEY = os.environ.get("API_KEY", "your dashscope api key")

SYSTEM_PROMPT = 'You are a helpful assistant.'
NO_TOOL_RESPONSE = "您好，我是一个会议助手，我还不会这项技能。我可以帮您创建会议，设置发言人，广播会场，主看会场，选看会场，或请求指定会场发言等。"                 # 无工具识别的默认响应
API_RESULT_PROMPT = "以下是查询的结果，请向用户解释，禁止使用markdown：\n\n{api_result}："     # API结果处理提示词

LLM_MAX_HISTORY_MESSAGE = 4                     # 聊天记录数量（发送给LLM的历史消息条数）
LLM_FORCE_NO_THINK = True                       # 是否强制不使用思考模式，True-强制不使用，False-根据场景自动判断
LLM_TEMPERATURE = 0                             # LLM温度参数，控制生成文本的随机性，值越小越确定，值越大越随机
LLM_MAX_TOKEN = 2048                            # LLM最大token数，超过LLM_MAX_TOKEN限制的token数，LLM将截断输入

# API 配置
API_PRETTY_RSP = False                          # 是否调用LLM美化API响应，True-美化，False-不美化
API_TIMEOUT = 10                                # API请求超时时间（秒）
API_RETRY_COUNT = 3                             # API请求失败重试次数
API_FAKE_API_RESULT = 1                         # 模拟API结果，0-不模拟，1-模拟，2-自定义API
API_FORCE_ONESHOT = 0                           # 模拟API结果测试时，强制使用oneshot模式（一次请求必须同时返回intent+slots）

# 工具配置
TOOL_CONFIG_FILE_EXT = '_config.py'             # 工具配置文件扩展名。请勿修改
TOOL_CONFIG_FILE = 'modules/GAB/GAB_config.py'  # 工具配置文件，*表示使用modules目录下所有*-config.py文件作为工具配置
TOOL_CONFIG_FILE = 'modules/xiaoke/xiaoke_config.py'  # 工具配置文件，*表示使用modules目录下所有*-config.py文件作为工具配置

# Flask 配置
FLASK_ENV = 'development'
BACKEND_HOST = '0.0.0.0'
BACKEND_PORT = 5050
CORS_ORIGINS = "*"
API_PREFIX = '/api'
BACKEND_URL = f'http://{BACKEND_HOST}:{BACKEND_PORT}'

# MCP服务器配置
MCP_VERSION = "1.0"                 # MCP协议版本
MCP_SESSION_TIMEOUT = 3600          # # MCP会话超时时间（秒），默认1小时
MCP_STREAM_ENABLED = True           # 是否启用流式响应
MCP_API_PREFIX = "/mcp"             # MCP服务器前缀
# 支持的模型列表
SUPPORTED_MODELS = [
    "odd-mcp",
    "odd-llm",
    "qwen2.5-0.5b-instruct",
    "qwen3-4b-instruct"
]

# OddAsr 配置
# ODD_ASR_URL = 'https://oddasr.odmeta.net'
# ODD_ASR_URL = 'http://172.16.237.141:9002'
ODD_ASR_URL = 'http://47.116.14.194:9002'
ODD_ASR_TOKEN = 'your_odd_asr_token'

# OddTTS 配置
# ODD_TTS_URL = 'https://oddtts.odmeta.net'
# ODD_TTS_URL = 'http://172.16.237.141:9003'
ODD_TTS_URL = 'http://47.116.14.194:9003'
ODD_TTS_TOKEN = 'your_odd_tts_token'

# 日志配置
LOG_LEVEL = 'DEBUG'
LOG_PATH = './log/'
LOG_FILE = 'odd_agent.log'

# 会议系统配置
APS_IP = "10.67.20.13"
APS_AUTO_LOGIN = True
APS_CONFIG = {
    "ip": f"{APS_IP}",
    "user_name": "wgh1",
    "password": "888888",
    "oauth_consumer_key": "1",
    "oauth_consumer_secret": "1",
    "account_token": "",
    "cookie_jar": "",
    "base_api": f"http://{APS_IP}/api/v1/"
}
