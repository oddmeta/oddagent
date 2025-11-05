
import uuid
from threading import Lock
from flask import Flask, request, jsonify, send_file, Response, Blueprint
from flask_cors import CORS

from logic.odd_agent import OddAgent
from tools.tool_template_utils import load_all_tool_config
import odd_agent_config as config
from odd_agent_logger import logger

bp = Blueprint('oddapi', __name__, url_prefix='')

# 实例化OddAgent
odd_agent = OddAgent(load_all_tool_config())

# 会话存储 - 生产环境应使用Redis或数据库
sessions = {}
sessions_lock = Lock()

def get_or_create_session(session_id=None):
    """获取或创建会话"""
    with sessions_lock:
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        if session_id not in sessions:
            sessions[session_id] = {
                'messages': [],
                'context': {},
                'created_at': None
            }
        
        return session_id, sessions[session_id]


@bp.route('/multi_question', methods=['POST'])
def api_multi_question():
    """多轮问答接口（原有接口保持兼容）"""
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    response = odd_agent.process_multi_question(question)
    return jsonify({"answer": response})

@bp.route(f'{config.API_PREFIX}/llm_chat', methods=['POST'])
def api_llm_chat():
    """流式AI聊天接口"""
    data = request.json
    messages = data.get('messages', [])
    user_input = data.get('user_input', '')
    session_id = data.get('session_id')
    
    if not user_input:
        return jsonify({"error": "No user_input provided"}), 400
    
    # 获取或创建会话
    session_id, session_data = get_or_create_session(session_id)
    
    # 检查是否是流式请求
    accept_header = request.headers.get('Accept', '')
    is_stream = 'text/event-stream' in accept_header
    
    try:
        if is_stream:
            # 流式响应
            def generate():
                try:
                    import time
                    
                    # 处理消息
                    response = odd_agent.process_multi_question(user_input)
                    
                    # 流式输出：逐字符发送
                    buffer = ""
                    for i, char in enumerate(response):
                        buffer += char
                        
                        # 每隔几个字符或遇到标点符号时发送一次
                        if len(buffer) >= 3 or char in '。！？，、；：':
                            # 发送SSE格式数据
                            yield f"data: {buffer}\n\n"
                            buffer = ""
                            # 添加小延迟模拟真实流式体验
                            time.sleep(0.05)
                    
                    # 发送剩余内容
                    if buffer.strip():
                        yield f"data: {buffer}\n\n"
                    
                    # 发送完成标记
                    yield "data: [DONE]\n\n"
                
                except Exception as e:
                    logger.error(f"流式处理错误: {str(e)}")
                    yield f"data: [ERROR] {str(e)}\n\n"
            
            response = Response(
                generate(),
                mimetype='text/event-stream',
                headers={
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'X-Session-ID': session_id
                }
            )
            return response
        else:
            # 非流式响应
            response = odd_agent.process_multi_question(user_input)
            return jsonify({
                "response": response,
                "session_id": session_id
            })
    
    except Exception as e:
        logger.error(f"LLM聊天错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route(f'{config.API_PREFIX}/mock_slots', methods=['GET'])
def api_mock_slots():
    """获取模拟槽位数据"""
    mock_data = {
        "slots": {
            "phone_number": "13601708473",
            "user_name": "落鹤生",
            "service_type": "角色信息",
            "package_type": "角色查询"
        },
        "available_services": [
            {"id": 1, "name": "工作履历", "description": "查询角色信息"},
            {"id": 2, "name": "教育信息", "description": "查询角色教育信息"},
            {"id": 3, "name": "项目经历", "description": "查询角色项目"}
        ]
    }
    return jsonify(mock_data)

@bp.route(f'{config.API_PREFIX}/reset_session', methods=['POST'])
def api_reset_session():
    """重置会话"""
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({"error": "No session_id provided"}), 400
    
    with sessions_lock:
        if session_id in sessions:
            del sessions[session_id]
    
    return jsonify({"message": "Session reset successfully", "session_id": session_id})

@bp.route(f'{config.API_PREFIX}/health', methods=['GET'])
def api_health():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "backend_url": config.BACKEND_URL,
        "environment": config.DEBUG
    })


@bp.errorhandler(404)
def not_found(error):
    return jsonify({"error": "API endpoint not found"}), 404

@bp.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

