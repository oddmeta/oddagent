**Read this in other languages: [English](README.en.md), [中文](README.md).**

# OddAgent: A General-Purpose Intent and Command Recognition Framework

[TOC]

Want to create your own personalized version of "Siri" or "Cortana"? If you have this idea but don't know where to start, the [OddAgent](https://pypi.org/project/oddagent/ "OddAgent") project can be your easy-to-use open-source solution.

This functionality was originally supported by [Xiao Luo Tong Xue](https://x.oddmeta.net "Xiao Luo Tong Xue") in early 2024. Recently, due to a company request to build an LLM-based intelligent assistant system, relevant code was extracted from the Xiao Luo Tong Xue project to create a separate OddAgent project. This LLM-based intelligent assistant system provides features like multi-turn conversations and streaming AI chat as an independent project for evolution.

OddAgent is a general-purpose intent and command recognition framework that is business-agnostic. The recognition accuracy and capabilities depend entirely on your agent configuration file.

At the same time, <font color=red>**OddAgent only recognizes intents and commands**</font>; it does not implement specific functions. After OddAgent recognizes intents and commands, you need to <font color=red>**implement the tool logic yourself**</font> and call the corresponding tools to complete the required functions.

<div align="center">
  <img src="https://www.oddmeta.net/wp-content/uploads/2025/11/OddAgent_400x200.png" alt="OddAgent Logo" width="400">
  
  [![GitHub Stars](https://img.shields.io/github/stars/oddmeta/oddagent.svg?style=social)](https://github.com/oddmeta/oddagent)
  [![Documentation](https://img.shields.io/badge/Documentation-Online-green.svg)](https://docs.oddmeta.net/)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
</div>

## I. Features

### 1. Framework Features

- Multi-turn conversation support
- Streaming AI chat interface support
- Template-based tool processing
- Voice conversation support (requires separate deployment of the [OddAsr project](https://github.com/oddmeta/oddasr "OddAsr project") and pointing the OddAsr deployment IP address to the server where OddAsr is deployed in config.json)

> The OddAsr project is located at: https://github.com/oddmeta/oddasr. Please deploy it separately if voice support is needed.

### 2. Example Functions

Based on video conferencing features, the following assistant functions are implemented in the example:

- Meeting scheduling service, can create meetings at specified times and locations.
- Meeting creation service.
- Meeting termination service.
- Meeting joining service, can join specified meetings.
- Meeting exiting service.
- Participant invitation service, can invite participants to specified meetings.
- Participant disconnection service, can disconnect participants from specified meetings.
- Camera activation service.
- Camera deactivation service.
- Microphone activation service.
- Microphone deactivation service.
- Dual stream sending service.
- Dual stream stopping service.
- Real-time subtitles activation service.
- Meeting minutes activation service.
- Meeting minutes deactivation service.

## II. Quick Start

It is recommended to install in a virtual environment to avoid conflicts with other products and projects. I personally use conda, but you can also use venv, uv, poetry, etc. The following introduction uses conda as an example.

Environment requirements: Python 3.10+

- 1. Create a test virtual environment

```bash
conda create -n oddagent_test python==3.12
conda activate oddagent_test
```

- 2. Install OddAgent in the virtual environment

```bash
pip install -i https://pypi.org/simple/ oddagent
```

> Non-official mirror sites may not have the latest version, so it is recommended to use the official PyPI source.

## III. Create Your Own Agent Project

### 1. Step 1: Create a directory in any location you want

For example: `d:\\myagent` or `/home/user/myagent`

### 2. Step 2: Download project configuration samples

Project configuration sample: https://oddmeta.net/tools/oddagent/config.json.sample
Agent configuration sample: https://oddmeta.net/tools/oddagent/conference_config.json

Download them and place them in the directory you created earlier. Then copy `config.json.sample` and rename it to `config.json`.

Then start adjusting the settings in config.json to configure your own system.

## IV. Configure Your System Settings

In the `config.json` system configuration, the main content that must be modified is two parts:

- LLM configuration: You need to fill in the address `GPT_URL`, model name `MODEL`, and `API_KEY` of the large model you want to use in the configuration.
- Agent configuration: Specify which agent OddAgent should enable. If you want to run multiple different agents simultaneously, you can refer to the later section "Advanced Usage: Running Multiple Agents Simultaneously".

Here is an example of system configuration:

### 1. LLM Configuration

```bash
  "GPT_URL": "https://qianfan.baidubce.com/v2/chat/completions",
  "MODEL": "ernie-4.5-turbo-128k",
  "API_KEY": "your api key",
```

### 2. Agent Configuration

```bash
  "TOOL_CONFIG_FILE_EXT": "_config.py",
  "TOOL_CONFIG_FILE": "agents/xiaoluo/xiaoluo_config.py",
```

## V. Agent Skill Configuration

OddAgent supports configuring different agent skills through JSON files, with configuration files located in the `agents` directory under your project root.

Under the agent_tool_list field, add the functions you want to implement one by one:

- `tool_name`: Tool name. It is recommended to use the actual API name that needs to be called when implementing this tool.
- `name`: Detailed tool name. A practical name that users can understand.
- `description`: Detailed tool introduction.
- `example`: Optional. If this tool requires calling parameters, it is recommended to specifically introduce them here. This introduction will be included in the prompt sent to the large model, helping the model better understand the intent corresponding to this tool and more accurately parse the slots for this tool.
- `parameters`: Optional. If this tool requires calling parameters, all parameters need to be listed here. Like the example, this content will also be sent to the large model in the prompt to help the model more accurately parse intents and slots.
- `enabled`: Whether to enable this tool.
- `tool_api_url`: [Not recommended] The API address that needs to be called to implement this tool after identifying the tool intent.
- `tool_api_headers`: [Not recommended] The parameter list that needs to be included in the API header when calling the tool API, such as authentication tokens.
- `tool_api_method`: [Not recommended] The method used when calling the tool API, such as: GET/POST/PUT/DELETE, etc.

Notes:
<font color=red>**The current open-source version only supports one parameter slot per tool. Do not fill in multiple parameters, otherwise the test will keep asking you to supplement information.**</font>

Here is an example configuration:

```json
{
  "global_variants": [],
  "agent_tool_list": [
    {
      "tool_name": "meeting_schedule",
      "name": "Schedule Meeting",
      "description": "Meeting scheduling service, can create meetings at specified times and locations.",
      "example": "JSON: [{'name': 'time', 'desc': 'Meeting time, format yyyy-MM-dd HH:mm:ss', 'value': ''} ]\nInput: Help me schedule a meeting on April 18, 2046 at 10:00:00\nAnswer: { 'time': '2046-04-18 10:00:00'}",
      "parameters": [
        {"name": "time", "desc": "Meeting time, format yyyy-MM-dd HH:mm:ss", "type": "string", "required": false},
      ],
      "enabled": true,
      "tool_api_url": "https://api.oddmeta.net/api/meeting_schedule",
      "tool_api_headers": "{'Content-Type': 'application/json', 'Authorization': '{{ api_key }}'}",
      "tool_api_method": "POST"
    }
  ]
}
```

## VI. Run and Test Your Own Agent

### 1. Start the OddAgent backend

In the directory of your own agent project, open a terminal command line and start OddAgent. You can also write a simple script to implement startup or automatic startup.

Startup command: `oddagent -c config.json`

### 2. Start the test interface

#### 1) Interface test
The OddAgent backend includes a simple web interface specifically for testing and debugging your agent skill configuration. The default address is: http://localhost:5050
The bound IP and port can be modified in the system configuration (config.json).
The interface after opening is shown in the following image:
![](https://kb.oddmeta.net/uploads/omassistant/images/m_b5793dcf08ff15d2caaf770a7707884b_r.png)
In this interface, you can select command words on the right and send requests to OddAgent, then check if it correctly parses and returns the intent and slots you want. If some command expressions fail to correctly identify intents and slots, you can continue to adjust your agent configuration.

#### 2) Actual API test

OddAgent only recognizes intents and commands, so in actual scenarios, it is basically used in your own product to call OddAgent through API to recognize intents and commands, and then implement the corresponding functions yourself.
The following is a complete example code for calling OddAgent through API:

```python
import json
import requests

API_BASE_URL = 'http://127.0.0.1:5050/oddagent/chat'                # API address

def recognize_intent(message):
    """Call api_oddagent_chat API"""
    try:
        response = requests.post(
            API_BASE_URL,
            json={
                'question': message, 
                'api_mode': 1 # Simulate API results, 0-not simulate, 1-simulate, 2-custom API
                }, 
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return { 'err_code': 200, 'message': 'success', 'data': data}
    except Exception as e:
        print(f"API call failed: {str(e)}")
        return { 'err_code': 500, 'message': f'API call failed: {str(e)}', 'data': None }

if __name__ == '__main__':
    json_response = recognize_intent("Start a weekly meeting")
    print(json.dumps(json_response, ensure_ascii=False, indent=2))
```

Run the test code: `python test_oddagent.py`

The result returned after calling:

```json
{
  "err_code": 200,
  "message": "success",
  "data": {
    "answer": {
      "data": "[Simulated API mode] Pretend success!",
      "err_code": 0,
      "message": "[meeting_create] API call successful",
      "slots": {
        "meeting_name": "Weekly Meeting"
      },
      "tool_name": "meeting_create"
    }
  }
}
```

Where:
- `tool_name`: The recognized intent (configured by the agent skill configuration file)
- `slots`: The slot values corresponding to the intent tool.

Emphasis again: As a general-purpose intent and command recognition framework, OddAgent is business-agnostic, and the effect is completely determined by your agent configuration file.

## VII. Advanced Usage: Running Multiple Agents Simultaneously

In some cases, there is a need to run multiple agents simultaneously. There are two recommended solutions:

### 1. Use a single OddAgent instance

In the system configuration (config.json), you can set `TOOL_CONFIG_FILE` to `agents/xiaoluo/*`, and then place all your agent configurations in the `agents/xiaoluo` directory. When OddAgent starts, it will read all files ending with `*_config.json` in this directory and load them.

### 2. Deploy multiple OddAgent instances separately

Create multiple system configurations (config1.json, config2.json, config3.json...) for each agent, and in each system configuration, set:
- `TOOL_CONFIG_FILE`: Point to the corresponding agent's configuration file. For example: `conference_config.py`, `smarthome_iot_config.py`...
- `BACKEND_PORT`: Use different ports, such as: 5050, 5051, 5052, 5053...

Taking [Xiao Luo Tong Xue](https://x.oddmeta.net "Xiao Luo Tong Xue") as an example, she supports multiple agent functions such as weather forecasting, meeting scheduling, and smart home control. Her approach is to deploy multiple different agents, that is: start multiple OddAgent instances, each with one agent configuration and bound to one port, then use a workflow in front to accept user input, and then route to different OddAgent instances for processing according to user output.

Here is an example of Xiao Luo Tong Xue's agent structure:

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

If you want to use a single OddAgent instance, set `TOOL_CONFIG_FILE` to `agents/xiaoluo/*` in the system configuration config.json, then start OddAgent in the directory where config.json is located: `oddagent -c config.json`.
If you want to deploy multiple OddAgent instances separately, copy the system configuration config.json multiple times, modify the corresponding `TOOL_CONFIG_FILE` and `BACKEND_PORT` in each system configuration, then start each OddAgent separately: `oddagent -c config1.json`, `oddagent -c config2.json`...

## VIII. Announcement

A new technical exchange group has been created. Welcome everyone to join the discussion.
Scan the QR code to join the AI technical exchange group (WeChat)
Follow my public account: 奥德元 (Ao De Yuan)
**<font color=red>Let's learn artificial intelligence together and catch up with this era.</font>**
(If the QR code expires, you can send me a private message)
Contact me on WeChat: oddmeta | Exchange group: 8655372