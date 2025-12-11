# OddAgent MCP 协议文档

## 概述
OddAgent MCP (Model Control Protocol) 是一个标准化的API接口，用于与OddAgent服务进行通信，支持文本生成、工具调用等功能。

## 支持的API端点

### 1. 聊天完成

**端点**: `/mcp/chat/completions`
**方法**: `POST`

**请求体**:
```json
{
  "model": "odd-mcp",
  "messages": [
    {"role": "system", "content": "你是一个会议助手"},
    {"role": "user", "content": "创建一个会议"}
  ],
  "stream": false,
  "session_id": "optional-session-id"
}
```

**响应**:
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1677825464,
  "model": "odd-mcp",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "会议已创建成功"
      },
      "finish_reason": "stop"
    }
  ],
  "session_id": "session-123",
  "usage": {
    "prompt_tokens": 30,
    "completion_tokens": 10,
    "total_tokens": 40
  }
}
```

### 2. 健康检查

**端点**: `/mcp/health`
**方法**: `GET`

**响应**:
```json
{
  "status": "healthy",
  "service": "Odd-MCP",
  "version": "1.0.0"
}
```

## 支持的模型

- odd-mcp
- odd-llm
- qwen2.5-0.5b-instruct
- qwen3-4b-instruct