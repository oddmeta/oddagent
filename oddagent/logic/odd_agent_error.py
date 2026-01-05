import json

EM_ERR_TYPE_LLM             = "1"         # 调用大模型 error
EM_ERR_TYPE_INTENT          = "2"         # 意图识别 error
EM_ERR_TYPE_SLOT            = "3"         # 槽位解析 error
EM_ERR_TYPE_TOOL            = "4"         # 工具调用 error

# BBB: MOD [000,999]
MOD_ODDAGENT                = "001"
MOD_LLM                     = "002"
MOD_INTENT_RECOGNITION      = "003"
MOD_SLOT_PARSE              = "004"
MOD_API_INVOKING            = "005"
MOD_TOOL_INVOKING           = "006"

# C.DDD: CODE [0000,9999]
g_odd_agent_err_api = {}

def DEF_ERR(MOD,TYPE,CODE,DESC = ""):
    err_code = (int)(TYPE + MOD + CODE)
    g_odd_agent_err_api[err_code] = DESC
    return err_code


def odd_err_name(err_code):
    ns = globals()
    for name in ns:
        if ns[name] == err_code:
            return name
    return ""

def odd_err_desc(err_code):
    if err_code in g_odd_agent_err_api:
        return g_odd_agent_err_api[err_code]
    return ""

def from_exc(exc):
    r = OddResult()
    r.set_code(exc.err_code)
    r.set_msg(exc.message)
    return r.result

def odd_exception_handler(exc):
    response_data = from_exc(exc)
    return json.dumps(response_data)

class OddException(Exception):
    """
    自定义异常类
    """
    
    def __init__(self, err_code, message):
        super().__init__()
        self.err_code = err_code
        self.message = message

    def __str__(self):
        return "%d - %s" % (self.err_code, self.message)

    def __unicode__(self):
        return u"%d - %s" % (self.err_code, self.message)

class OddResult:
    """
    结果返回

    返回结果格式如下：
        {
            "err_code": 0,
            "message": "操作成功",
            "data": {}
        }
    示例使用：
        返回结果：
            result = OddResult()
            result.set_code(0)
            result.set_msg("操作成功")
            result.set_data(data)
            return result.result
    """
    def __init__(self):
        self._result = {}

    def set_code(self, err_code):
        self._result['err_code'] = err_code

    def set_msg(self, message):
        self._result['message'] = message

    def set_data(self, data):
        self._result['data'] = data

    @property
    def result(self):
        return self._result

class ResultException(OddException):
    """
    异常返回

    异常返回格式如下：
        {
            "err_code": 1001,
            "message": "操作失败，请重试"
        }
    示例使用：
        触发异常：
            raise OddException("1001", "操作失败，请重试")
        捕获异常：
            try:
                # 可能出错的代码
                do_something()
            except OddException as e:
                # 处理自定义异常
                print(f"错误代码: {e.err_code}, 错误信息: {e.message}")
    """
    def __init__(self, err_code, message):
        super(ResultException, self).__init__(err_code, message)

#错误码定义如下:

EM_ERR_LLM_ARGS_ERROR                                   = DEF_ERR(EM_ERR_TYPE_LLM, MOD_LLM, "0001", "参数错误")
EM_ERR_LLM_APIKEY_ERROR                                 = DEF_ERR(EM_ERR_TYPE_LLM, MOD_LLM, "0002", "API_KEY错误")
EM_ERR_LLM_CONNECTION_ERROR                             = DEF_ERR(EM_ERR_TYPE_LLM, MOD_LLM, "0003", "调用大模型接口失败，请检查网络连接")
EM_ERR_LLM_TIMEOUT                                      = DEF_ERR(EM_ERR_TYPE_LLM, MOD_LLM, "0004", "调用大模型接口超时，请检查网络连接")

EM_ERR_INTENT_RECOGNITION_SERVER_ERROR                  = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0001", "intent recognition server error")
EM_ERR_INTENT_RECOGNITION_NO_TOOL                       = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0002", "无法识别用户意图, 而且没有当前工具或不在补槽阶段。清空工具状态。")
EM_ERR_INTENT_RECOGNITION_NO_TOOL2                      = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0003", "无法识别用户意图, 但是当前处于补槽阶段。保留当前工具")
EM_ERR_INTENT_RECOGNITION_NO_TOOL3                      = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0004", "LLM返回一个不在当前工具列表中的工具。保留当前工具")
EM_ERR_INTENT_RECOGNITION_NO_TOOL_RESPONSE              = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0005", "您好，我是一个个人助手，我还不会这项技能。我可以帮您xxx,yyy,zzz等。")                 # 无工具识别的默认响应
EM_ERR_INTENT_RECOGNITION_API_CONNECTION_ERROR          = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0006", "tool api connection error")
EM_ERR_INTENT_RECOGNITION_METHOD_NOT_SUPPORT            = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0007", "method not support")
EM_ERR_INTENT_RECOGNITION_STATUS_ERROR                  = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0008", "status error")
EM_ERR_INTENT_RECOGNITION_EXCEPTION                     = DEF_ERR(EM_ERR_TYPE_INTENT, MOD_INTENT_RECOGNITION, "0009", "exception while recognizing intent")

EM_ERR_SLOT_PARSE_INVALID_SLOT_NAME                     = DEF_ERR(EM_ERR_TYPE_SLOT, MOD_SLOT_PARSE, "0001", "invalid slot name")
EM_ERR_SLOT_PARSE_EXCEPTION                             = DEF_ERR(EM_ERR_TYPE_SLOT, MOD_SLOT_PARSE, "0002", "exception while parsing slot LLM response")

EM_ERR_API_INVOKE_EXCEPTION                             = DEF_ERR(EM_ERR_TYPE_TOOL, MOD_API_INVOKING, "0002", "exception while invoking tool API")

