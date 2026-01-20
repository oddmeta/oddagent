
import uuid
import time
import requests
from threading import Lock
from flask import request, jsonify, Response, Blueprint, make_response

from oddagent.config_loader import config
from oddagent.logic.odd_agent import OddAgent
from oddagent.odd_agent_logger import logger
from oddagent.modules.module_tool import load_all_tool_config

bp = Blueprint('oddapi', __name__, url_prefix='')

# 实例化OddAgent
odd_agent = OddAgent(load_all_tool_config(config.TOOL_CONFIG_FILE_EXT))

# 会话存储 - 生产环境应使用Redis或数据库
sessions = {}
sessions_lock = Lock()

def update_global_variants(global_variants):
    """更新全局变量"""
    odd_agent.update_global_variants(global_variants)


def update_transmit():
    try:
        # 获取前端发送的数据
        data = request.get_json() or {}
        files = request.files if request.files else None
        
        # 转发请求到 ASR 服务
        asr_url = f"{config.ODD_ASR_URL}/update_transmit"
        
        if files:
            # 处理文件上传的情况
            response = requests.post(asr_url, files=files, verify=False)
        else:
            # 处理 JSON 数据的情况
            response = requests.post(asr_url, json=data, verify=False)
        
        # 使用make_response创建响应
        flask_response = make_response(response.content)
        flask_response.status_code = response.status_code
        
        # 复制必要的响应头
        content_type = response.headers.get('content-type')
        if content_type:
            flask_response.headers['Content-Type'] = content_type
            
        return flask_response
    
    except Exception as e:
        logger.error(f"Error proxying ASR request: {str(e)}")
        return jsonify({'error': 'Proxy error', 'message': str(e)}), 500

def proxy_asr_sentence():
    try:
        # 获取ASR服务的URL
        asr_server_url = f"{config.ODD_ASR_URL}/v1/asr/sentence"
        
        # 获取原始请求的headers，但不要直接复制，因为requests会自动处理content-type等
        headers = {'User-Agent': request.headers.get('User-Agent', ''),
                   'Authorization': f'Bearer {config.ODD_ASR_TOKEN}'}
        
        # 根据请求类型处理不同的请求数据
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 处理文件上传请求
            files = {}
            data = {}
            
            # 收集所有文件
            for key, file in request.files.items():
                files[key] = (file.filename, file.stream, file.mimetype)
            
            # 收集所有表单数据
            for key, value in request.form.items():
                data[key] = value
            
            # 发送multipart/form-data请求
            response = requests.post(
                asr_server_url,
                headers=headers,
                files=files,
                data=data,
                params=request.args,
                timeout=config.API_TIMEOUT,
                verify=False
            )
        else:
            # 处理普通请求（JSON或其他）
            headers['Content-Type'] = request.content_type or 'application/json'
            response = requests.post(
                asr_server_url,
                headers=headers,
                data=request.get_data(),
                params=request.args,
                timeout=config.API_TIMEOUT,
                verify=False
            )
        
        # 创建响应对象
        flask_response = make_response(response.content)
        flask_response.status_code = response.status_code
        
        # 复制响应headers
        for header_name, header_value in response.headers.items():
            # 跳过一些特定headers
            if header_name.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                flask_response.headers[header_name] = header_value
        
        # 确保设置CORS头
        flask_response.headers['Access-Control-Allow-Origin'] = '*'
        
        return flask_response
    except requests.exceptions.RequestException as e:
        logger.error(f"ASR代理请求失败: {str(e)}")
        return jsonify({"error": "Proxy error", "message": str(e)}), 500
    except Exception as e:
        logger.error(f"ASR代理处理出错: {str(e)}")
        return jsonify({"error": str(e)}), 500

bp.add_url_rule('/proxy/asr/sentence/update_transmit', view_func=update_transmit, methods=['POST'])
bp.add_url_rule('/proxy/asr/sentence', view_func=proxy_asr_sentence, methods=['POST'])

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


@bp.route('/oddagent/chat', methods=['POST'])
def api_oddagent_chat():
    """OddAgent聊天接口"""
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    api_mode = data.get('api_mode', config.API_FAKE_API_RESULT)
    time_start = time.time()
    response = odd_agent.process_oddagent_chat(question, api_mode)
    time_end = time.time()
    logger.info(f"api_oddagent_chat: {question}, time_cost: {time_end - time_start:.4f}s, response: {response}")
    
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
                    response = odd_agent.process_oddagent_chat(user_input)
                    
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
            response = odd_agent.process_oddagent_chat(user_input)
            return jsonify({
                "response": response,
                "session_id": session_id
            })
    
    except Exception as e:
        logger.error(f"LLM聊天错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route(f'{config.API_PREFIX}/mock_slots', methods=['GET'])
def api_mock_slots():

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

