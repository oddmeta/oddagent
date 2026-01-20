from oddagent.odd_agent_logger import logger

def api_request_composer(tool_name: str, tool_config: dict, slots_data: dict):
    api_url: str = tool_config["api_url"]
    api_header: dict = tool_config["api_header"]
    api_content: dict = {}

    # cython 不支持match case，重写为if else
    # match tool_name:
    #     case "create_meeting":
    #         api_url, api_header, api_content = compose_create_meeting(tool_config, slots_data)
    #     case "get_meeting_info":
    #         api_url, api_header, api_content = compose_get_meeting_info(tool_config, slots_data)
    #     case _:
    #         logger.error(f"Unsupported tool name: {tool_name}")
    #         return None, None, None
    if tool_name == "create_meeting":
        api_url, api_header, api_content = compose_create_meeting(tool_config, slots_data)
    elif tool_name == "get_meeting_info":
        api_url, api_header, api_content = compose_get_meeting_info(tool_config, slots_data)
    else:
        logger.error(f"Unsupported tool name: {tool_name}")
        return None, None, None
        
    return api_url, api_header, api_content

def compose_create_meeting(tool_config: dict, slots_data: dict):
    """
    处理创建会议工具请求
    :param tool_config: 创建会议工具配置字典
    :param slots_data: 槽位参数JSON数据列表
    :return: 处理后的API请求字典
    """
    tool_name: str = tool_config.get("tool_name", "")
    api_url: str = tool_config.get("api_url", "")
    api_header_template: dict = tool_config.get("api_header", {})

    # 构建API URL
    api_url_template = f'{api_url}/api/{{tool_name}}' # 工具处理API地址模板
    api_url = api_url_template.format(tool_name=tool_name)
    
    # 构建API请求头
    # TODO 如果parameters里有confid, e164, token等全局变量，则添加到api_header里
    #api_header = api_header_template.format(token=token)
    api_header = {
        "Content-Type": "application/json"
    }

    # 构建API请求内容
    content = slots_data

    return api_url, api_header, content

def compose_get_meeting_info(tool_config: dict, slots_data: dict):
    """
    处理获取会议信息工具请求
    :param tool_config: 获取会议信息工具配置字典
    :param user_input: 用户输入字符串
    :param context: 上下文字典
    :return: 处理后的API请求字典
    """
    tool_name: str = tool_config.get("tool_name", "")
    api_url: str = tool_config.get("api_url", "")
    api_header_template: dict = tool_config.get("api_header", {})

    # 构建API URL
    api_url_template = f'{api_url}/api/{{tool_name}}' # 工具处理API地址模板
    api_url = api_url_template.format(tool_name=tool_name)
    
    # 构建API请求头
    # TODO 如果parameters里有confid, e164, token等全局变量，则添加到api_header里
    #api_header = api_header_template.format(token=token)
    api_header = {
        "Content-Type": "application/json"
    }

    # 构建API请求内容
    content = slots_data

    return api_url, api_header, content
