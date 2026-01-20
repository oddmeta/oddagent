# OddAgent API 接口文档

## 1. ASR 接口

### 1.1 语音识别接口

**接口名称**：语音识别接口

**接口描述**：将音频文件转换为文本，通过代理转发到配置的 OddAsr 服务。

**请求方法**：POST

**请求 URL**：`/proxy/asr/sentence`

**请求参数**：

| 参数名 | 类型 | 位置 | 描述 | 是否必填 |
| ------ | ---- | ---- | ---- | -------- |
| audio_file | 文件 | FormData | 音频文件，支持 WAV、MP3 等格式 | 是 |
| language | string | FormData | 识别语言，默认为中文 | 否 |
| confidence_threshold | float | FormData | 置信度阈值，默认 0.6 | 否 |

**请求头**：
- Authorization: Bearer {ODD_ASR_TOKEN}，令牌从配置文件中读取

**响应格式**：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "text": "识别结果文本",
    "confidence": 0.95,
    "duration": 3.5
  }
}
```

**错误响应**：

```json
{
  "error": "Proxy error",
  "message": "请求转发失败的具体原因"
}
```

### 1.2 更新转写接口

**接口名称**：更新转写接口

**接口描述**：更新语音转写配置或状态，通过代理转发到 OddAsr 服务。

**请求方法**：POST

**请求 URL**：`/proxy/asr/sentence/update_transmit`

**请求参数**：根据 OddAsr 服务接口定义，支持 JSON 数据或文件上传。

**响应格式**：

- 成功：直接返回 OddAsr 服务的响应
- 失败：返回错误信息

**错误响应**：

```json
{
  "error": "Proxy error",
  "message": "请求转发失败的具体原因"
}
```

## 2. Chat 接口

### 2.1 OddAgent 聊天接口

**接口名称**：OddAgent 聊天接口

**接口描述**：与 OddAgent 进行单轮对话，支持模拟 API 调用。

**请求方法**：POST

**请求 URL**：`/oddagent/chat`

**请求体**：

```json
{
  "question": "你好，帮我创建一个需求讨论会议",
  "api_mode": 1
}
```

| 参数名 | 类型 | 描述 | 默认值 |
| ------ | ---- | ---- | ------ |
| question | string | 用户的问题或请求 | 必填 |
| api_mode | int | API 调用模式，0 真实调用，1 模拟调用 | 1 |

**响应格式**：

```json
{
  "data": "[模拟API模式] 假装成功！",
  "err_code": 0,
  "message": "[meeting_create] API调用成功",
  "slots": {
    "meeting_name": "需求讨论会议"
  },
  "tool_name": "meeting_create"
}
```

**错误响应**：

```json
{
  "data": "用户输入: 开个周例会",
  "err_code": 210002,
  "msg": "API_KEY错误"
}
```

### 2.2 流式 LLM 聊天接口

**接口名称**：流式 LLM 聊天接口

**接口描述**：与 LLM 进行多轮对话，支持流式响应。

**请求方法**：POST

**请求 URL**：`/api/llm_chat`

**请求头**：
- Accept: text/event-stream（用于流式响应）

**请求体**：

```json
{
  "user_input": "你好，帮我创建一个需求讨论会议",
  "messages": [
    {
      "role": "system",
      "content": "你是一个会议助手"
    }
  ],
  "session_id": "session_12345"
}
```

| 参数名 | 类型 | 描述 | 默认值 |
| ------ | ---- | ---- | ------ |
| user_input | string | 用户的问题或请求 | 必填 |
| messages | array | 聊天历史记录 | [] |
| session_id | string | 会话 ID，用于保持对话上下文 | 自动生成 |

**响应格式**：

非流式响应：
```json
{
  "data": "[模拟API模式] 假装成功！",
  "err_code": 0,
  "message": "[meeting_create] API调用成功",
  "slots": {
    "meeting_name": "需求讨论会议"
  },
  "tool_name": "meeting_create"
}
```

流式响应（SSE）：
```
data: 会议已

data: 创建成功

data: ，会议 ID 为：

data: meeting-12345

data: [DONE]
```

**错误响应**：

```json
{
  "data": "用户输入: 开个周例会",
  "err_code": 210002,
  "msg": "API_KEY错误"
}
```

## 3. MCP 接口

### 3.1 MCP 聊天完成接口

**接口名称**：MCP 聊天完成接口

**接口描述**：按照 MCP 协议与 LLM 进行聊天，支持流式响应。

**请求方法**：POST

**请求 URL**：`/mcp/chat/completions`

**请求体**：

```json
{
  "model": "oddagent-default",
  "messages": [
    {
      "role": "system",
      "content": "你是一个会议助手"
    },
    {
      "role": "user",
      "content": "你好，帮我创建一个会议"
    }
  ],
  "session_id": "session_12345",
  "stream": false,
  "api_mode": 1
}
```

| 参数名 | 类型 | 描述 | 默认值 |
| ------ | ---- | ---- | ------ |
| model | string | 模型名称 | 必填 |
| messages | array | 聊天历史记录 | 必填 |
| session_id | string | 会话 ID | 自动生成 |
| stream | boolean | 是否使用流式响应 | false |
| api_mode | int | API 调用模式，0 真实调用，1 模拟调用 | 1 |

**响应格式**：

```json
{
  "id": "chatcmpl-abcdef1234567890",
  "object": "chat.completion",
  "created": 1634567890,
  "model": "oddagent-default",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "会议已创建成功，会议 ID 为：meeting-12345"
      },
      "finish_reason": "stop"
    }
  ],
  "session_id": "session_12345",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

**错误响应**：

```json
{
  "error": {
    "message": "No model specified",
    "type": "invalid_request_error"
  }
}
```

### 3.2 MCP 健康检查接口

**接口名称**：MCP 健康检查接口

**接口描述**：检查 MCP 服务是否正常运行。

**请求方法**：GET

**请求 URL**：`/mcp/health`

**响应格式**：

```json
{
  "status": "healthy",
  "service": "OddMCP",
  "version": "1.0.0"
}
```

## 4. 辅助接口

### 4.1 模拟槽位接口

**接口名称**：模拟槽位接口

**接口描述**：返回模拟的槽位信息和可用服务列表，用于测试。

**请求方法**：GET

**请求 URL**：`/api/mock_slots`

**响应格式**：

```json
{
  "slots": {
    "phone_number": "13601708473",
    "user_name": "落鹤生",
    "service_type": "角色信息",
    "package_type": "角色查询"
  },
  "available_services": [
    {
      "id": 1,
      "name": "工作履历",
      "description": "查询角色信息"
    },
    {
      "id": 2,
      "name": "教育信息",
      "description": "查询角色教育信息"
    },
    {
      "id": 3,
      "name": "项目经历",
      "description": "查询角色项目经历"
    }
  ]
}
```

### 4.2 重置会话接口

**接口名称**：重置会话接口

**接口描述**：清除指定会话的历史记录。

**请求方法**：POST

**请求 URL**：`/api/reset_session`

**请求体**：

```json
{
  "session_id": "session_12345"
}
```

| 参数名 | 类型 | 描述 | 是否必填 |
| ------ | ---- | ---- | -------- |
| session_id | string | 会话 ID | 是 |

**响应格式**：

```json
{
  "message": "Session reset successfully",
  "session_id": "session_12345"
}
```

### 4.3 健康检查接口

**接口名称**：健康检查接口

**接口描述**：检查 OddAgent 服务是否正常运行。

**请求方法**：GET

**请求 URL**：`/api/health`

**响应格式**：

```json
{
  "status": "healthy",
  "backend_url": "http://0.0.0.0:5050",
  "environment": true
}
```

## 5. 配置说明

接口相关配置在 `odd_agent_config.py` 中定义：

```python
# ASR 配置
ODD_ASR_URL = 'http://47.116.14.194:9002'  # OddAsr 服务地址
ODD_ASR_TOKEN = 'your_odd_asr_token'       # 访问令牌

# API 配置
API_PREFIX = '/api'                         # API 前缀
API_TIMEOUT = 10                            # API 请求超时时间

# MCP 配置
MCP_VERSION = "1.0"                          # MCP 协议版本
MCP_SESSION_TIMEOUT = 3600                   # MCP 会话超时时间
MCP_STREAM_ENABLED = True                    # 是否启用 MCP 流式响应
MCP_API_PREFIX = "/mcp"                      # MCP 前缀
```

## 6. 错误码说明

| 错误码 | 描述 |
| ------ | ---- |
| 400 | 请求参数错误 |
| 404 | API 端点不存在 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用（如 ASR 服务连接失败） |
        