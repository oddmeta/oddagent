tool_config = {
  "agent_api_base": "https://api.xiaoke.ai",
  "global_variants": [
  ],
  "agent_tool_list": [
    {
      "tool_name": "INSTANT_MEETING",
      "name": "创建会议",
      "description": "立即创建会议。例：创建xxx，开个xxx，xxx会议。",
      "parameters": [
        { "name": "meeting_name", "desc": "会议名称", "type": "string", "required": True }
      ],
      "example": "输入：江苏省公安厅创建公安会议\n答：{ 'meeting_name': '公安会议' }",
      "test_instructions": [
        "创建公安会议",
        "开个周例会",
        "现在开晨会"
      ],
      "test_answers": [
        { "tool_name": "INSTANT_MEETING", "slots": { "meeting_name": "公安会议" }},
        { "tool_name": "INSTANT_MEETING", "slots": { "meeting_name": "周例会" }},
        { "tool_name": "INSTANT_MEETING", "slots": { "meeting_name": "晨会" }}
      ],
      "tool_api_url": "https://api.xiaoke.ai/api/INSTANT_MEETING",
      "tool_api_method": "POST",
      "enabled": True
    },
    {
      "tool_name": "SILENCE",
      "name": "全场麦克风静音控制",
      "custom_system_prompt": "你是一个专业的语音助手，你的任务是根据用户的指令，控制会议中所有麦克风的静音与取消静音。\n返回严格按照以下格式:{ 'enabled': int } }",
      "description": "关闭或者开启会议中所有人的麦克风，控制会议中所有麦克风的静音与取消静音。",
      "parameters2": [
        { "name": "enabled", "desc": "静音开关：1表示全场静音，也即关闭麦克风/闭麦；0表示取消静音，也即打开麦克风/开麦。", "type": "number", "required": True }
      ],
      "parameters": [
        { "name": "enabled", "desc": "静音开关：1表示全场静音，也即关闭麦克风/闭麦；0表示取消静音，也即打开麦克风/开麦。", "type": "number", "required": True }
      ],
      "example": "'enabled':1代表静音或者关闭麦克风，0代表解除静音或开启。\n\n输入：关闭全场麦克风\n答：{ 'enabled': 1 }\n输入：打开全场麦克风\n答：{ 'enabled': 0 }",
      "test_instructions": [
        "关闭全场麦克风",
        "关闭全场全体麦克风",
        "关掉全场全体麦克风",
        "所有麦克风静音",
        "把全场全体的麦都关闭",
        "把所有麦克风都关闭",
        "关闭所有人的麦克风",
        "全场关麦",
        "全关麦克风",
        "开启全场麦克风",
        "打开全场全体麦克风",
        "把所有麦克风都打开",
        "打开所有人的麦克风",
        "把大家的麦都打开",
        "全场开麦",
        "全开麦克风"
      ],
      "test_answers": [
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 1 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 0 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 0 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 0 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 0 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 0 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 0 }},
        { "tool_name": "SILENCE", "slots": { "enabled": 0 }}
      ],
      "tool_api_url": "https://api.xiaoke.ai/api/SILENCE",
      "tool_api_method": "POST",
      "enabled": True
    },
    {
      "tool_name": "SPEAKER",
      "name": "设置发言人",
      "description": "设置某个会场画面作为发言人，以广播其图像。如：请xxx发言，调度上海, 广播xxx, 将xxx设置为发言人,选看xxx,画面给xxx,主看xxx。\n其中: xxx 为发言人的名称，通常是为省、直辖市一级的省厅、公安厅，如湖南、湖南省厅、湖南公安厅等。",
      "parameters": [
        { "name": "mt", "desc": "发言人会场名称", "type": "string", "required": True }
      ],
      "example": "输入：广播浙江\n答：{ 'mt': '浙江' }\n输入：请江苏省公安厅发言\n答：{ 'mt': '江苏省公安厅' }",
      "test_instructions": [
        "广播江苏省公安厅",
        "广播江苏省厅",
        "广播浙江",
        "主看江西省厅",
        "把主画面切到河北省厅",
        "给所有人看河北省厅的画面",
        "选看江西",
        "将河北设为发言人",
        "把发言人设为河北",
        "请湖南省公安厅发言",
        "接下来请江苏省公安厅发言"
      ],
      "test_answers": [
        { "tool_name": "SPEAKER", "slots": { "mt": "江苏" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "江苏" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "浙江" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "江西" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "河北" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "河北" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "江西" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "河北" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "河北" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "湖南" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "江苏" }}
      ],
      "test_answers2": [
        { "tool_name": "SPEAKER", "slots": { "mt": "江苏省公安厅" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "江苏省厅" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "浙江" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "江西省厅" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "河北省厅" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "河北省厅" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "江西" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "河北省厅" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "河北省厅" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "湖南省公安厅" }},
        { "tool_name": "SPEAKER", "slots": { "mt": "江苏省公安厅" }}
      ],
      "tool_api_url": "https://api.xiaoke.ai/api/SPEAKER",
      "tool_api_method": "POST",
      "enabled": True
    },
    {
      "tool_name": "POLL",
      "name": "会议轮询控制",
      "description": "控制会议轮询功能，可开启或结束会场轮询。",
      "parameters": [
        { "name": "enabled", "desc": "1 表示开始轮询，0 表示结束轮询", "type": "number", "required": True }
      ],
      "example": "输入：开始轮询\n答：{ 'enabled': 1 }\n输入：结束轮询\n答：{ 'enabled': 0 }",
      "test_instructions": [
        "开始轮询",
        "轮询开始",
        "开始轮询",
        "轮询一下",
        "轮询",
        "全场轮询",
        "开始轮询",
        "开始快速轮询",
        "对全体参会者开始轮询",
        "结束轮询",
        "停止轮询",
        "关闭轮询",
        "退出轮询模式",
        "轮询结束",
        "轮询可以关了",
        "轮询到此为止",
        "轮询完成",
        "轮询取消",
        "把轮询结束掉"
      ],
      "test_answers": [
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 1 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }},
        { "tool_name": "POLL", "slots": { "enabled": 0 }}
      ],
      "tool_api_url": "https://api.xiaoke.ai/api/POLL",
      "tool_api_method": "POST",
      "enabled": True
    },
    {
      "tool_name": "POLL_INTERVAL",
      "name": "设置会议轮询间隔",
      "description": "控制会议轮询（轮巡）间隔时间。如：间隔x秒，x秒间隔,轮询x秒。x秒为正整数，值应该转换为数字。",
      "parameters": [
        { "name": "poll_interval", "desc": "轮询/轮巡间隔时间，单位秒", "type": "number", "required": True }
      ],
      "example": "输入：轮询间隔5秒\n答：{ 'poll_interval': 5 }",
      "test_instructions": [
        "轮询间隔时间5秒",
        "轮巡间隔设为五秒",
        "轮询间隔5秒",
        "轮询十秒",
        "轮询5秒间隔",
        "间隔十秒",
        "5秒间隔",
        "间隔5",
        "设个间隔十秒",
        "间隔5秒"
      ],
      "test_answers": [
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 5 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 5 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 5 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 10 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 5 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 10 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 5 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 5 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 10 }},
        { "tool_name": "POLL_INTERVAL", "slots": { "poll_interval": 5 }}
      ],
      "tool_api_url": "https://api.xiaoke.ai/api/POLL_INTERVAL",
      "tool_api_method": "POST",
      "enabled": True
    },
    {
      "tool_name": "ONLINE_MTS_POST",
      "name": "呼叫会场",
      "description": "呼叫xxx，邀请xxx加入会议。",
      "parameters": [
        { "name": "mt", "desc": "呼叫的会场列表，逗号分隔", "type": "string", "required": True }
      ],
      "example": "输入：呼叫江苏省厅和浙江省厅\n答：{ 'mt': '江苏省厅,浙江省厅' }",
      "test_instructions": [
        "呼叫浙江省厅",
        "呼叫江苏省公安厅",
        "呼叫江苏、浙江省厅",
        "再呼一遍江苏、浙江省厅",
        "呼叫河北"
      ],
      "test_answers": [
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "浙江" }},
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "江苏" }},
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "江苏,浙江" }},
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "江苏,浙江" }},
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "河北" }}
      ],
      "test_answers2": [
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "浙江省厅" }},
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "江苏省厅" }},
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "江苏省厅,浙江省厅" }},
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "江苏省厅,浙江省厅" }},
        { "tool_name": "ONLINE_MTS_POST", "slots": { "mt": "河北省厅" }}
      ],
      "tool_api_url": "https://api.xiaoke.ai/api/ONLINE_MTS_POST",
      "tool_api_method": "POST",
      "enabled": True
    },
    {
      "tool_name": "MTS_DELETE",
      "name": "挂断或移除会场",
      "description": "挂断xxx，断开xxx的连接, 结束xxx的通话, 结束xxx的接入, 终止xxx的接入, 结束xxx的呼叫，移除xxx, 请离xxx, 清退xxx, 踢掉xxx，或将xxx从会议中删除、断开、下线。",
      "description_qw2.5": "挂断指定会场，或将其从会议中清退、移除、删除、断开、下线。",
      "parameters": [
        {"name": "mt", "desc": "要挂断或删除的会场列表，逗号分隔", "type": "string", "required": True }
      ],
      "example": "输入：挂断江苏和浙江省厅\n答：{ 'mt': '江苏省厅,浙江省厅' }",
      "test_instructions": [
        "挂断江苏和浙江省公安厅",
        "挂掉浙江",
        "断开河北、江西省厅的连接",
        "结束与江苏、浙江的通话",
        "移除江西",
        "请离江苏和江西省厅",
        "清退杭州省厅",
        "把江苏、江西踢出去",
        "将江苏和浙江从会议中踢掉",
        "让江苏和浙江省厅下线",
        "江苏省厅，删除",
        "把江苏省厅断开",
        "江西卡顿了，移除一下",
        "终止河北公安厅的接入",
        "结束对江苏省厅的呼叫"
      ],
      "test_answers": [
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏,浙江" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "浙江" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "河北,江西" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏,浙江" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江西" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏,江西" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "杭州" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏,江西" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏,浙江" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏,浙江" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江西" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "河北" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏" }}
      ],
      "test_answers2": [
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏省厅,浙江省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "浙江省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "河北省厅,江西省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏省厅,浙江省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江西省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏省厅,江西省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "杭州市省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏省厅,江西省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏,浙江" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏省厅,浙江省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江西省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "河北省厅" }},
        { "tool_name": "MTS_DELETE", "slots": { "mt": "江苏省厅" }}
      ],
      "tool_api_url": "https://api.xiaoke.ai/api/MTS_DELETE",
      "tool_api_method": "POST",
      "enabled": True
    }
  ]
}