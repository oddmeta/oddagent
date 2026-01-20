**Read this in other languages: [English](README.en.md), [中文](README.md).**

# OddAgent：一个通用的意图、指令识别框架

[TOC]

想自己动手来手搓一个完全属于你自己的“小爱同学”、“小艺”吗？如果有你这么一个想法，而又不知道该如何开始的话，那么[OddAgent](https://pypi.org/project/oddagent/ "OddAgent")项目可以成为你非常容易上手的开源项目。

本来这个功能是[小落同学](https://x.oddmeta.net "小落同学")在2024年初就已经支持，由于前阵子公司老板说需要做一个基于LLM的智能助手系统，因此就先从小落同学项目里把相关的代码摘了一下出来，单独搞了一个OddAgent项目出来，作为一个基于LLM的智能助手系统，提供多轮问答、流式AI聊天等功能独立项目来演进。

OddAgent作为一个通用的意图、指令识别框架，跟业务无关，效果识别的准确率，可识别的能力，完全由你的智能体技术配置文件决定。

同时，<font color=red>**OddAgent只负责识别意图、指令**</font>，不负责实现具体的功能。通过OddAgent识别出来意图、指令后，你需要<font color=red>**自行实现工具**</font>逻辑，并调用对应的工具，完成相应的功能。

<div align="center">
  <img src="https://www.oddmeta.net/wp-content/uploads/2025/11/OddAgent_400x200.png" alt="OddAgent Logo" width="400">
  
  [![Documentation](https://img.shields.io/badge/Documentation-Online-green.svg)](https://docs.oddmeta.net/)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
</div>

## 一、功能特性

### 1. 框架特性

- 支持多轮对话
- 支持流式AI聊天接口
- 工具模板化处理
- 支持语音对话（需要自行部署 [OddAsr项目](https://github.com/oddmeta/oddasr "OddAsr项目")，并在config.json中将OddAsr部署的IP地址指向OddAsr所在的服务器）

> OddAsr项目位于：https://github.com/oddmeta/oddasr ，若需要语音的支持，请自行部署。

### 2. 示例功能

根据视频会议的功能特性，在示例中实现了如下的助手功能：

- 预约会议服务，可创建指定时间、地点的会议。
- 创建会议服务。
- 结束会议服务。
- 加入会议服务，可加入指定会议。
- 退出会议服务。
- 邀请参会人服务，可邀请指定会议的参会人。
- 挂断参会人服务，可挂断指定会议的参会人。
- 打开摄像头服务。
- 关闭摄像头服务。
- 打开麦克风服务。
- 关闭麦克风服务。
- 发送双流服务。
- 停止双流服务。
- 打开同声字幕服务。
- 打开会议纪要服务。
- 关闭会议纪要服务。

## 二、快速开始

建议在一个虚拟环境里安装，以避免与其它的产品和项目冲突。我个人习惯用conda，你用venv, uv，poetry什么也都OK。下面以conda为例介绍整个安装。

环境要求: Python 3.10+

- 1. 创建测试用的虚拟环境

```bash
conda create -n oddagent_test python==3.12
conda activate oddagent_test
```

- 2. 在虚拟环境里安装OddAgent

```bash
pip install -i https://pypi.org/simple/ oddagent
```

> 非官方的镜像站可能不一定能找到最新版本，因此建议使用pypi官方源。

## 三、创建你自己的智能体项目

### 1. 步骤一：在任意你想要的目录下创建一个目录

如：`d:\\myagent` 或者 `/home/user/myagent`

### 2. 步骤二：下载项目配置样例

项目配置样例：https://oddmeta.net/tools/oddagent/config.json.sample
智能体配置样例：https://oddmeta.net/tools/oddagent/conference_config.json

下载好后放在你前面创建的目录下。然后复制`config.json.sample`，并将其改名为`config.json`

然后开始调整设置config.json里配置你自己的系统配置

## 四、配置你自己的系统配置

在`config.json`系统配置里，必改的内容主要是两个：

- 大模型配置：需要将你自己用的大模型的地址`GPT_URL`，模型名`MODEL`，以及`API_KEY`在配置里填一下
- 智能体的配置：指定OddAgent启用哪个智能体。如果你有多个不同的智能体希望同时运行的话，可以参考后面的介绍《`进阶用法：同时运行多个智能体`》

下面是一个系统配置的示例。

### 1. 大模型配置

```bash
  "GPT_URL": "https://qianfan.baidubce.com/v2/chat/completions",
  "MODEL": "ernie-4.5-turbo-128k",
  "API_KEY": "your api key",
```

### 2. 智能体配置

```bash
  "TOOL_CONFIG_FILE_EXT": "_config.py",
  "TOOL_CONFIG_FILE": "agents/xiaoluo/xiaoluo_config.py",
```

## 五. 智能体技能配置

OddAgent支持通过JSON文件配置不同的智能体技能，配置文件位于你的项目根目录下`agents`目录下。

在agent_tool_list字段下面，将你要实现的功能一个个加进去：

- `tool_name`： 工具名。建议可以是实际这个工具在实现时需要调用的API的名字。
- `name`: 详细工具名。一个实际的、用户要以看在懂的名字。
- `description`: 工具具体介绍。
- `example`: 可选。如果这个工具是需要带调用参数的，建议在这里具体介绍一下，这里的介绍是会带在prompt提示词里送给大模型，让大模型来更清楚明白的了解这个工具所对应的意图（intent），以及更准确的去解析出此工具对应的slot(槽位)。
- `parameters`: 可选。如果这个工具是需要带调用参数的，所有的参数需要在这里列示一下。同example一样，这里的内容也是会在prompt里带给大模型的，以便大模型更精准的解析意图及槽位。
- `enabled`: 启用与否
- `tool_api_url`: 【不建议使用】识别出工具意图后，实际实现该工具所需要调用的API的地址。
- `tool_api_headers`: 【不建议使用】调用工具API时，需要在API的头信息里带的参数列表，如认证的token。
- `tool_api_method`: 【不建议使用】调用工具API时，使用的方法（method），比如：GET/POST/PUT/DELETE等。

注意事项：
<font color=red>**当前开源版本每个tool只提供一个parameter槽位的支持，请匆填充多个parameter，否则测试时会一直在要求你补充。**</font>

以下是一个示例配置。

```json
{
  "global_variants": [],
  "agent_tool_list": [],
    {
      "tool_name": "meeting_schedule",
      "name": "预约会议",
      "description": "预约会议服务，可创建指定时间、地点的会议。",
      "example": "JSON：[{'name': 'time', 'desc': '会议时间，格式为yyyy-MM-dd HH:mm:ss', 'value': ''} ]\n输入：帮我预约一个2046年4月18日10:00:00的会议\n答：{ 'time': '2046-04-18 10:00:00'}",
      "parameters": [
        {"name": "time", "desc": "会议时间，格式为yyyy-MM-dd HH:mm:ss", "type": "string", "required": false},
      ],
      "enabled": true,
      "tool_api_url": "https://api.oddmeta.net/api/meeting_schedule",
      "tool_api_headers": "{'Content-Type': 'application/json', 'Authorization': '{{ api_key }}'}",
      "tool_api_method": "POST"
    }
  ]
}
```

## 六、运行测试你自己的智能体

### 1. 启动oddagent智能体后台

在你创建的自己的智能体项目的目录下，打开一个terminal命令行，然后启动oddagent。当然你也可以自己写个简单的脚本来实现启动或者自动启动。

启动命令：`oddagent -c config.json`

### 2. 启动测试界面

#### 1）界面测试
oddagent后台加了一个简单的Web界面，专门用于测试和调试你的智能体技能配置，默认的地址是：http://localhost:5050
绑定的IP和端口可以在系统配置（config.json）里修改。
打开后的界面如下图所示
![](https://kb.oddmeta.net/uploads/omassistant/images/m_b5793dcf08ff15d2caaf770a7707884b_r.png)
在这个界面里，你可以选择右边的命令词然后发送请求到oddagent，然后看看它是否正确的解析并返回了你要的意图和槽位，如果有一些命令词说法未能正确识别出意图和槽位的话，可以再继续对你的智能体技术配置里做调整。

#### 2）实际API测试

OddAgent只做意图、指令的识别，所以实际场景里基本上都是在你自己的产品里用API来调用OddAgent识别意图指令，然后自行去实现相应的功能。
以下是一个API调用OddAgent的完整示例代码：
```python
import json
import requests

API_BASE_URL = 'http://127.0.0.1:5050/oddagent/chat'                # API地址

def recognize_intent(message):
    """调用api_oddagent_chat API"""
    try:
        response = requests.post(
            API_BASE_URL,
            json={
                'question': message, 
                'api_mode': 1 # 模拟API结果，0-不模拟，1-模拟，2-自定义API
                }, 
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return { 'err_code': 200, 'message': 'success', 'data': data}
    except Exception as e:
        print(f"API调用失败: {str(e)}")
        return { 'err_code': 500, 'message': f'API调用失败: {str(e)}', 'data': None }

if __name__ == '__main__':
    json_response = recognize_intent("开个周例会")
    print(json.dumps(json_response, ensure_ascii=False, indent=2))
```

运行测试代码：`python test_oddagent.py`

调用后返回的结果：
```json
{
  "err_code": 200,
  "message": "success",
  "data": {
    "answer": {
      "data": "[模拟API模式] 假装成功！",
      "err_code": 0,
      "message": "[meeting_create] API调用成功",
      "slots": {
        "meeting_name": "周例会"
      },
      "tool_name": "meeting_create"
    }
  }
}
```
其中：
- `tool_name`: 识别出来的意图（由智能体技能配置文件所配置）
- `slots`: 该意图工具对应的槽位值。

再次强制：OddAgent作为一个通用的意图、指令识别框架，跟业务无关，效果完全由你的智能体技术配置文件决定。

## 七、进阶用法：同时运行多个智能体

在一些情况下，存在同时运行多个智能体的需求，建议的方案有两种。

### 1. 用一个oddagent搞定

在系统配置（config.json）里，你可以将 `TOOL_CONFIG_FILE` 设置为`agents/xiaoluo/*`，然后把你智能体配置都放到 `agents/xiaoluo` 目录下，这样 oddagent 在启动的时候就会去读取 这个目录下所有的 `*_config.json` 结尾的文件，并将他们加载起来。

### 2. 用多个oddagent分开部署

为每个智能体启用一个系统配置（config1.json, config2.json, config3.json...），并在每个系统配置里设置
- `TOOL_CONFIG_FILE`: 指向对应智能体的配置文件。如：`conference_config.py`，`smarthome_iot_config.py`...
- `BACKEND_PORT`: 使用不同的端口，如：5050，5051，5052，5053...

以[小落同学](https://x.oddmeta.net "小落同学")而言，她支持天气预报，会议调度，智能家居控制等多种智能体功能，她的做法是部署多个不同的智能体，也即：启动多个oddagent，每个oddagent配置一个智能体配置，并绑定一个端口，然后前置一个工作流接受用户输入，并根据用户的输出再导到不同的oddagent过去处理。

下面是小落同学的一个智能体示例。

```bash
\---oddagent
    |   config.json
    |   config.json.sample
    |
    +---agents
    |   \---xiaoluo
    |       |   conference_config.py
    |       |   GAB_config.py
    |       |   odd_bookmark_config.py
    |       |   smarthome_iot_config.py
    |       |   tpad_work_hour.py
    |       |   weather_config.py
    |       |   xiaoluo_config.py
    |       |   __init__.py
```

如果想用一个oddagent搞定，那你就在系统配置config.json里将 `TOOL_CONFIG_FILE` 设置为`agents/xiaoluo/*`，然后在`config.json`所在的目录下： `oddagent -c config.json` 启动 oddagent 即可。
如果想用多个 oddagent分开部署的话，就把系统配置config.json复制多份，并修改每个系统配置中对应的`TOOL_CONFIG_FILE`和`BACKEND_PORT`，然后再每个oddagent分别启动即可： `oddagent -c config1.json` , `oddagent -c config2.json` ...

## 八、广而告之

新建了一个技术交流群，欢迎大家一起加入讨论。
扫码加入AI技术交流群（微信）
关注我的公众号：奥德元
**<font color=red>让我们一起学习人工智能，一起追赶这个时代。</font>**
(若二维码过期了，可私信我)
有事+wx: oddmeta 交流群: 8655372