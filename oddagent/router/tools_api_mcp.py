# -*- coding: utf-8 -*-
""" 
MCP协议服务器实现
"""

import time
import uuid
from flask import request, jsonify, Blueprint

from oddagent.odd_agent_logger import logger
from oddagent.config_loader import config

from oddagent.logic.odd_agent import OddAgent
from oddagent.modules.module_tool import load_all_tool_config

# 创建MCP Blueprint
bp = Blueprint('mcp', __name__, url_prefix='/mcp')

# 全局OddAgent实例
odd_agent = OddAgent(load_all_tool_config(config.TOOL_CONFIG_FILE_EXT))

# MCP会话管理
mcp_sessions = {}

class MCPSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.created_at = time.time()
        self.messages = []
        self.context = {}
        
    def save_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        # 限制消息历史长度
        self.messages = self.messages[-config.LLM_MAX_HISTORY_MESSAGE:]

@bp.route('/chat/completions', methods=['POST'])
async def mcp_chat_completions():
    """MCP聊天完成接口"""
    try:
        # 解析请求数据
        data = request.json
        
        # 验证必要参数
        if not data.get('model'):
            return jsonify({"error": {"message": "No model specified", "type": "invalid_request_error"}}), 400
            
        if not data.get('messages'):
            return jsonify({"error": {"message": "No messages provided", "type": "invalid_request_error"}}), 400
        
        # 调用模式，0为真实调用，1为模拟调用
        api_mode = data.get('api_mode', 1)

        # 获取会话ID，创建或复用
        session_id = data.get('session_id', str(uuid.uuid4()))
        if session_id not in mcp_sessions:
            mcp_sessions[session_id] = MCPSession(session_id)
        
        # 获取最后一条用户消息
        last_user_message = None
        for msg in reversed(data['messages']):
            if msg.get('role') == 'user':
                last_user_message = msg.get('content')
                break
                
        if not last_user_message:
            return jsonify({"error": {"message": "No user message found", "type": "invalid_request_error"}}), 400
        
        # 检查是否是流式请求
        is_stream = data.get('stream', False)
        answer = ""
        
        # 处理请求
        if is_stream:
            # 流式响应
            # for chunk in odd_agent.process_oddagent_chat(last_user_message, stream=True):
            #     answer += chunk
            answer = "暂不支持流式响应"
        else:
            # 非流式响应
            response = odd_agent.process_oddagent_chat(last_user_message, api_mode)
        
            # 格式化响应为MCP格式
            if isinstance(response, dict):
                answer = str(response)
            else:
                answer = response
                
            # 保存消息历史
            mcp_sessions[session_id].save_message('user', last_user_message)
            mcp_sessions[session_id].save_message('assistant', str(answer))
        
        # 构建MCP响应
        mcp_response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:16]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": data['model'],
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": str(answer)
                },
                "finish_reason": "stop"
            }],
            "session_id": session_id,
            "usage": {
                "prompt_tokens": len(last_user_message),
                "completion_tokens": len(str(answer)),
                "total_tokens": len(last_user_message) + len(str(answer))
            }
        }
        
        return jsonify(mcp_response)
        
    except Exception as e:
        logger.error(f"MCP处理错误: {str(e)}")
        return jsonify({"error": {"message": str(e), "type": "server_error"}}), 500

@bp.route('/health', methods=['GET'])
def mcp_health():
    """MCP健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "OddMCP",
        "version": "1.0.0"
    })