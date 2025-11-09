**Read this in other languages: [English](README.en.md), [中文](README.md).**

# OddAgent：轻松手搓一个你自己的“小艺”、“小爱同学”

[TOC]

想自己动手来手搓一个完全属于你自己的“小爱同学”、“小艺”吗？如果有你这么一个想法，而又不知道该如何开始的话，那么OddAgent项目可以成为你非常容易上手的开源项目。

本来这个功能是[小落同学](https://x.oddmeta.net "小落同学")在去年就已经支持，由于前两天公司老板说需要做一个基于LLM的智能助手系统，因此就先从[小落同学](https://x.oddmeta.net "小落同学")项目里把相关的代码摘了一下出来，单独搞了一个OddAgent项目出来，作为一个基于LLM的智能助手系统，提供多轮问答、流式AI聊天等功能独立项目来演进。

<div align="center">
  <img src="static/images/OddAgent_400x200.png" alt="OddAgent Logo" width="400">
  
  [![GitHub Stars](https://img.shields.io/github/stars/oddmeta/oddagent.svg?style=social)](https://github.com/oddmeta/oddagent)
  [![Documentation](https://img.shields.io/badge/Documentation-Online-green.svg)](https://docs.oddmeta.net/)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
</div>

## 一、功能特性

### 1. OddAgent框架特性
- 支持多轮对话
- 支持流式AI聊天接口
- 工具模板化处理
- 支持语音对话（需要自行部署 [OddAsr项目](https://github.com/oddmeta/oddasr "OddAsr项目")，并在`odd_agent_config.py`中将OddAsr部署的IP地址指向OddAsr所在的服务器）

[OddAsr项目](https://github.com/oddmeta/oddasr "OddAsr项目")位于：https://github.com/oddmeta/oddasr ，若需要语音的支持，请自行部署。

### 2. 示例功能介绍
根据视频会议的功能特性，在示例中实现了如下的助手功能：
1. 预约会议服务，可创建指定时间、地点的会议。
2. 创建会议服务。
3. 结束会议服务。
4. 加入会议服务，可加入指定会议。
5. 退出会议服务。
6. 邀请参会人服务，可邀请指定会议的参会人。
7. 挂断参会人服务，可挂断指定会议的参会人。
8. 打开摄像头服务。
9. 关闭摄像头服务。
10. 打开麦克风服务。
11. 关闭麦克风服务。
12. 发送双流服务。
13. 停止双流服务。
14. 打开同声字幕服务。
15. 打开会议纪要服务。
16. 关闭会议纪要服务。
17. 密码重置，提交手机号和身份证号。


## 二、快速开始

### 1. 环境要求

- Python 3.10+

注：启动服务时自动检查依赖，并自动安装，最简单的使用方式：`python app.py`

### 2. 配置

修改 `odd_agent_config.py` 文件中的配置参数：

```python
# 调试模式
DEBUG = True

# LLM 模型参数
GPT_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
MODEL = 'qwen3-30b-a3b-instruct-2507'
API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
SYSTEM_PROMPT = 'You are a helpful assistant.'

# Flask 配置
BACKEND_HOST = 'localhost'
BACKEND_PORT = 5050

# 其他配置...
```

### 3. 启动服务

若是 Windows 环境，执行 `start.bat`
若是 Linux/Mac 环境，执行
```bash
chmod +x start.sh
./start.sh
```

或者直接运行：
```bash
python app.py
```

服务启动后，访问 http://localhost:5050 查看界面。

## 三、项目结构

```
├── app.py # 应用主入口 
├── odd_agent_config.py # 配置文件 
├── odd_agent_logger.py # 日志配置 
├── logic/ # 业务逻辑 
│ ├── init.py # 模块初始化 
│ ├── api_request_composer.py # API请求构建器 
│ ├── api_response_paser.py # API响应解析器 
│ └── odd_agent.py # 核心Agent实现 
├── tools/ # 工具处理模块 
│ ├── init.py # 模块初始化 
│ ├── tool_template_utils.py # 工具模板工具 
│ ├── tool_executer.py # 工具执行器接口 
│ ├── tool_executer_impl.py # 工具执行器实现 
│ ├── tool_processor.py # 工具处理器接口 
│ ├── tool_processor_impl.py # 工具处理器实现 
│ ├── tool_prompts.py # 工具提示模板 
│ └── tool_datetime_utils.py # 日期时间工具 
├── router/ # API路由 
│ ├── init.py # 模块初始化 
│ ├── tools_api.py # 工具API接口 
│ └── tools_front.py # 前端路由 
├── modules/ # 场景配置模块 
│ ├── catherine/ # Catherine场景 
│ │ └── cc.json # 场景配置文件 
│ ├── xiaoke/ # 小科场景 
│ │ └── xiaoke.json # 场景配置文件 
│ └── xiaoluo/ # 小落场景 
│ └── xiaoluo.json # 场景配置文件 
├── static/ # 静态资源 
│ ├── bootstrap.min.css # Bootstrap CSS 
│ ├── bootstrap.min.js # Bootstrap JS 
│ ├── common/ # 通用脚本 
│ │ ├── oddagent.js # Agent客户端 
│ │ ├── oddasr.js # ASR客户端 
│ │ └── oddrecoder.js # 录音工具 
│ ├── dist/ # 编译后的资源 
│ ├── images/ # 图片资源 
│ └── plugins/ # 第三方插件 
├── templates/ # HTML模板 
│ └── index.html # 主页面 
├── log/ # 日志文件目录 
│ └── odd_agent.log # 日志文件 
├── requirements.txt # 依赖清单 
├── start.bat # Windows启动脚本 
└── start.sh # Linux/Mac启动脚本
```


## 四、工具模板配置

项目支持通过JSON文件配置不同的工具模板，配置文件位于`modules/`目录下。

在agent_tool_list字段下面，将你要实现的功能一个个加进去：
- `tool_name`： 工具名。建议可以是实际这个工具在实现时需要调用的API的名字。
- `name`: 详细工具名。一个实际的、用户要以看在懂的名字。
- `description`: 工具具体介绍。
- `example`: 可选。如果这个工具是需要带调用参数的，建议在这里具体介绍一下，这里的介绍是会带在prompt提示词里送给大模型，让大模型来更清楚明白的了解这个工具所对应的意图（intent），以及更准确的去解析出此工具对应的slot(槽位)。
- `parameters`: 可选。如果这个工具是需要带调用参数的，所有的参数需要在这里列示一下。同example一样，这里的内容也是会在prompt里带给大模型的，以便大模型更精准的解析意图及槽位。
- `enabled`: 启用与否
- `tool_api_url`: 识别出工具意图后，实际实现该工具所需要调用的API的地址。
- `tool_api_headers`: 调用工具API时，需要在API的头信息里带的参数列表。
- `tool_api_method`: 调用工具API时，使用的方法（method），比如：GET/POST/PUT等。

以下是一个示例配置
```json
{
  "global_variants": [],
  "agent_tool_list": [],
    {
      "tool_name": "meeting_schedule",
      "name": "预约会议",
      "description": "预约会议服务，可创建指定时间、地点的会议。",
      "example": "JSON：[{'name': 'time', 'desc': '会议时间，格式为yyyy-MM-dd HH:mm:ss', 'value': ''}, {'name': 'place', 'desc': '会议地点', 'value': ''} ]\n输入：帮我预约一个2046年4月18日10:00:00在北京的会议\n答：{ 'time': '2046-04-18 10:00:00', 'place': '北京' }",
      "parameters": [
        {"name": "time", "desc": "会议时间，格式为yyyy-MM-dd HH:mm:ss", "type": "string", "required": false},
        {"name": "place", "desc": "会议地点", "type": "string", "required": false}
      ],
      "enabled": true,
      "tool_api_url": "https://api.xiaoke.ai/api/meeting_schedule",
      "tool_api_headers": "{'Content-Type': 'application/json', 'Authorization': '{{ api_key }}'}",
      "tool_api_method": "POST"
    }
  ]
}
```

## 五、其它信息

### 1. 注意事项

- 配置LLM：确保API_KEY配置正确，否则无法调用LLM服务
- 工具模板配置：可根据您自己的需要自行配置相对应的意图工具
- 语音支持
  - 若需要语音支持，可自行下载安装部署 [OddAsr项目](https://github.com/oddmeta/oddasr "OddAsr项目")
  - OddAsr部署好后，修改`odd_agent_config.py`，并修改其中的ODD_ASR_URL地址为你自己的地址，比如： 'http://172.16.237.141:9002'
- 工具模板配置及API调用：在[小落同学](https://x.oddmeta.net "小落同学")里所有的后台API都是自己封装的，API的名字通常就是 工具配置里的 tool_name，但是如果一个工具需调用第三方的API来实现实际功能时，API的地址(url）、头（headers）、方法（Method）以及参数通常千奇百怪，因此整个工具模板配置的结构相比于[小落同学](https://x.oddmeta.net "小落同学")项目有了一些改动，并且单独出一个处理API请求的类（`api_request_composer.py`）和一个API响应的类（`api_request_composer.py`），在[OddAgent项目](https://github.com/oddmeta/oddagent "OddAgent项目")里，每个工具相关的业务都需在这两个类里由用户自行实现。
- 语音识别优化：如果使用了OddAsr来让OddAgent支持语音交互的话，需要将一些名词（如：人名、会议名、会议室名、参会成员列表等）以热词的方式加入的OddAsr的请求的API里，以让语音转写功能更加准确。
- 生产环境注意事项：
	- 开发环境建议设置`DEBUG=True`，生产环境建议设置为False
	- 会话数据当前存储在内存中，生产环境建议使用Redis或数据库

### 2. 待完成功能

在视频会议业务的部分命令里可能会存在slot内容需二次确认的场景，比如：邀请 xxx，而 xxx 这个名字可能存在多个相近的账号，此时需要在业务流程中加入一个中断，将查询到的多个 xxx 先返回给前端，让用户自己来选择要邀请的是第几个xxx。

### 3. 开源地址

⭐️ [GitHub](https://github.com/oddmeta/oddagent)
📖 [文档](https://docs.oddmeta.net/)