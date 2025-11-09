
DEBUG = True

# LLM 模型参数
GPT_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
MODEL = 'qwen3-30b-a3b-instruct-2507'
API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxx'
SYSTEM_PROMPT = 'You are a helpful assistant.'
CHAT_HISTORY_COUNT = 3 # 聊天记录数量（发送给LLM的历史消息条数）
NO_TOOL_RESPONSE = "您好，小科是会议助手，请问您有什么会议业务需要小科处理吗？" # 无工具识别的默认响应
API_RESULT_PROMPT = "以下是查询的结果，请向用户解释，禁止使用markdown：\n\n{api_result}：" # API结果处理提示词

# Flask 配置
FLASK_ENV = 'development'
BACKEND_HOST = 'localhost'
BACKEND_PORT = 5050
CORS_ORIGINS = "*"
API_PREFIX = '/api'
BACKEND_URL = f'http://{BACKEND_HOST}:{BACKEND_PORT}'

# OddAsr 配置
ODD_ASR_URL = 'http://172.16.237.141:9002'
ODD_ASR_TOKEN = 'your_odd_asr_token'

# OddTTS 配置
ODD_TTS_URL = 'http://172.16.237.141:9001'
ODD_TTS_TOKEN = 'your_odd_tts_token'

# API 参数
API_TIMEOUT = 10 # API请求超时时间（秒）
API_RETRY_COUNT = 3
API_FAKE_API_RESULT = True

# 日志配置
LOG_LEVEL = 'DEBUG'
LOG_PATH = './log/'
LOG_FILE = 'odd_agent.log'
