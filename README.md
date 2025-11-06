
# OddAgent

一个基于LLM的智能助手系统，提供多轮问答、流式AI聊天等功能。

## 功能特性

- 多轮对话支持
- 流式AI聊天接口
- 工具模板处理
- 场景化配置
- 完整的日志系统

## 技术栈

- **后端**：Python, Flask, Flask-CORS
- **LLM服务**：阿里云DashScope (qwen3-30b-a3b-instruct-2507模型)
- **前端**：Bootstrap, jQuery
- **日志**：Python标准logging模块

## 快速开始

### 环境要求

- Python 3.6+  
- 安装依赖：`pip install -r requirements.txt`

### 配置

修改 `odd_agent_config.py` 文件中的配置参数：

```python
# 调试模式
DEBUG = True

# LLM 模型参数
GPT_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
MODEL = 'qwen3-30b-a3b-instruct-2507'
API_KEY = 'sk-d8f0024e2d874a7dac8324538ecf2e6c'
SYSTEM_PROMPT = 'You are a helpful assistant.'

# Flask 配置
BACKEND_HOST = 'localhost'
BACKEND_PORT = 5050

# 其他配置...
```

### 启动服务

#### Windows
```bash
start.bat
```

#### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

或者直接运行：
```bash
python app.py
```

服务启动后，访问 http://localhost:5050 查看界面。

## API接口

### 多轮问答接口

```
POST /multi_question
```

**参数**：
- `question`: 问题内容

**返回**：
- `answer`: 回答内容

### 流式AI聊天接口

```
POST /api/llm_chat
```

## 项目结构

```
├── app.py                # 应用主入口
├── odd_agent_config.py   # 配置文件
├── odd_agent_logger.py   # 日志配置
├── logic/                # 业务逻辑
│   └── odd_agent.py      # 核心Agent实现
├── tools/                # 工具处理模块
│   ├── tool_template_utils.py  # 工具模板工具
│   └── ...
├── router/               # API路由
│   ├── tools_api.py      # 工具API接口
│   └── tools_front.py    # 前端路由
├── modules/              # 场景配置模块
│   ├── catherine/        # Catherine场景
│   ├── xiaoke/           # 小科场景
│   └── xiaoluo/          # 小洛场景
├── static/               # 静态资源
│   ├── bootstrap.min.css # Bootstrap CSS
│   ├── bootstrap.min.js  # Bootstrap JS
│   └── ...
├── templates/            # HTML模板
│   └── index.html        # 主页面
├── log/                  # 日志文件目录
│   └── odd_agent.log     # 日志文件
└── requirements.txt      # 依赖清单
```

## 场景配置

项目支持通过JSON文件配置不同的场景，配置文件位于`modules/`目录下：

```json
{
  "common_fields": [],
  "scene_list": [
    {
      "scene_name": "场景名称",
      "scene_desc": "场景描述",
      "parameters": [],
      "tool_call_params": {},
      "tool_call_api": ""
    }
  ]
}
```

## 日志说明

日志配置在`odd_agent_logger.py`中，日志文件保存在`log/odd_agent.log`，支持按天轮转。

## 开发说明

1. 安装开发依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 启动开发服务器：
   ```bash
   python app.py
   ```

3. 调试模式下，修改代码会自动重启服务。

## 注意事项

- 确保API_KEY配置正确，否则无法调用LLM服务
- 开发环境建议设置DEBUG=True，生产环境建议设置为False
- 会话数据当前存储在内存中，生产环境建议使用Redis或数据库

## 作者信息

- catherine wei
- Email: catherine@oddmeta.com

## 开源地址

⭐️ [GitHub](https://github.com/oddmeta/oddagent)
📖 [文档](https://docs.oddmeta.net/)
        