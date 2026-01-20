from oddagent.odd_agent_logger import logger

def api_response_parser(tool_name: str, tool_response):
    """
    解析工具响应，提取有用的信息
    :param tool_name: 工具名称字符串
    :param tool_response: 工具响应字符串
    :return: 解析后的信息字典
    """
    # case "create_meeting":
    #     tool_response = create_meeting(tool_response)
    # case "get_meeting_info":
    #     tool_response = get_meeting_info(tool_response)
    # case _:
    #     logger.error(f"Unsupported tool name: {tool_name}")
    #     return None
    if tool_name == "create_meeting":
            tool_response = create_meeting(tool_response)
    elif tool_name == "get_meeting_info":
        tool_response = get_meeting_info(tool_response)
    else:
        logger.error(f"Unsupported tool name: {tool_name}")
        return None
    return tool_response

def create_meeting(tool_response):
    """
    处理创建会议工具响应
    :param tool_response: 创建会议工具响应字符串
    :return: 处理后的信息字典
    """
    
    try:
        tool_response = tool_response.json()
        if 'data' in tool_response and 'confid' in tool_response['data']:
            confid = tool_response['data']['confid']
            tool_response['confid'] = confid
            #############################
            # TODO 将confid添加到global_variants里
            #############################
            # odd_agent.update_global_variants({'confid': confid})
        else:
            logger.error("confid not found in create_meeting response")
            return {"error": "confid not found in create_meeting response"}
    except Exception as e:
        logger.error(f"Error parsing create_meeting response: {e}")
        return {"error": f"Error parsing create_meeting response: {e}"}
    
    return tool_response

def get_meeting_info(tool_response):
    """
    处理获取会议信息工具响应
    :param tool_response: 获取会议信息工具响应字符串
    :return: 处理后的信息字典
    """
    return {"meeting_info": tool_response}
