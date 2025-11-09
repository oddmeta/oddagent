# OddAgent: Build Your Own "Siri" or "Cortana"

[TOC]

Want to create your own personalized version of "Siri" or "Cortana"? If you have this idea but don't know where to start, the OddAgent project can be your easy-to-use open-source solution.

This functionality was originally supported by [Xiao Luo Tongxue](https://x.oddmeta.net "Xiao Luo Tongxue") last year. Due to a recent request from the company's boss to build an LLM-based intelligent assistant system, relevant code was extracted from the [Xiao Luo Tongxue](https://x.oddmeta.net "Xiao Luo Tongxue") project to create a separate OddAgent project. This LLM-based intelligent assistant system provides features like multi-turn conversations and streaming AI chat as an independent project for evolution.

<div align="center">
  <img src="static/images/OddAgent_400x200.png" alt="OddAgent Logo" width="400">
  
  [![GitHub Stars](https://img.shields.io/github/stars/oddmeta/oddagent.svg?style=social)](https://github.com/oddmeta/oddagent)
  [![Documentation](https://img.shields.io/badge/Documentation-Online-green.svg)](https://docs.oddmeta.net/)
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
</div>

## I. Features

### 1. OddAgent Framework Features
- Supports multi-turn conversations
- Supports streaming AI chat interface
- Template-based tool processing
- Voice conversation support (requires deploying the [OddAsr project](https://github.com/oddmeta/oddasr "OddAsr project") separately and pointing the OddAsr deployment IP address in [odd_agent_config.py](file://f:\ai_share\jacky\oddservice\oddagent\odd_agent_config.py) to the server where OddAsr is deployed)

The [OddAsr project](https://github.com/oddmeta/oddasr "OddAsr project") is located at: https://github.com/oddmeta/oddasr. Please deploy it separately if voice support is needed.

### 2. Sample Function Introduction
Based on video conferencing functionality characteristics, the following assistant functions are implemented in the example:
1. Meeting scheduling service, can create meetings at specified times and locations.
2. Create meeting service.
3. End meeting service.
4. Join meeting service, can join specified meetings.
5. Exit meeting service.
6. Invite participant service, can invite participants to specified meetings.
7. Disconnect participant service, can disconnect participants from specified meetings.
8. Turn on camera service.
9. Turn off camera service.
10. Turn on microphone service.
11. Turn off microphone service.
12. Send dual stream service.
13. Stop dual stream service.
14. Turn on real-time subtitles service.
15. Turn on meeting minutes service.
16. Turn off meeting minutes service.
17. Password reset, submit phone number and ID number.


## II. Quick Start

### 1. Environment Requirements

- Python 3.10+

Note: Dependencies are automatically checked and installed when starting the service. The simplest way to use it: `python app.py`

### 2. Configuration

Modify the configuration parameters in the [odd_agent_config.py](file://f:\ai_share\jacky\oddservice\oddagent\odd_agent_config.py) file:

```python
# Debug mode
DEBUG = True

# LLM model parameters
GPT_URL = 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
MODEL = 'qwen3-30b-a3b-instruct-2507'
API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
SYSTEM_PROMPT = 'You are a helpful assistant.'

# Flask configuration
BACKEND_HOST = 'localhost'
BACKEND_PORT = 5050

# Other configurations...
```

### 3. Start Service

For Windows environment, execute [start.bat](file://f:\ai_share\jacky\oddservice\oddagent\start.bat)
For Linux/Mac environment, execute
```bash
chmod +x start.sh
./start.sh
```

Or run directly:
```bash
python app.py
```

After the service starts, visit http://localhost:5050 to view the interface.

## III. Project Structure

```
├── app.py # Application main entry point
├── odd_agent_config.py # Configuration file
├── odd_agent_logger.py # Log configuration
├── logic/ # Business logic
│ ├── __init__.py # Module initialization
│ ├── api_request_composer.py # API request builder
│ ├── api_response_parser.py # API response parser
│ └── odd_agent.py # Core Agent implementation
├── tools/ # Tool processing module
│ ├── __init__.py # Module initialization
│ ├── tool_template_utils.py # Tool template utilities
│ ├── tool_executer.py # Tool executor interface
│ ├── tool_executer_impl.py # Tool executor implementation
│ ├── tool_processor.py # Tool processor interface
│ ├── tool_processor_impl.py # Tool processor implementation
│ ├── tool_prompts.py # Tool prompt templates
│ └── tool_datetime_utils.py # Date and time utilities
├── router/ # API routing
│ ├── __init__.py # Module initialization
│ ├── tools_api.py # Tool API interface
│ └── tools_front.py # Frontend routing
├── modules/ # Scenario configuration modules
│ ├── catherine/ # Catherine scenario
│ │ └── cc.json # Scenario configuration file
│ ├── xiaoke/ # Xiao Ke scenario
│ │ └── xiaoke.json # Scenario configuration file
│ └── xiaoluo/ # Xiao Luo scenario
│ └── xiaoluo.json # Scenario configuration file
├── static/ # Static resources
│ ├── bootstrap.min.css # Bootstrap CSS
│ ├── bootstrap.min.js # Bootstrap JS
│ ├── common/ # Common scripts
│ │ ├── oddagent.js # Agent client
│ │ ├── oddasr.js # ASR client
│ │ └── oddrecoder.js # Recording tool
│ ├── dist/ # Compiled resources
│ ├── images/ # Image resources
│ └── plugins/ # Third-party plugins
├── templates/ # HTML templates
│ └── index.html # Main page
├── log/ # Log file directory
│ └── odd_agent.log # Log file
├── requirements.txt # Dependency list
├── start.bat # Windows startup script
└── start.sh # Linux/Mac startup script
```


## IV. Tool Template Configuration

The project supports configuring different tool templates through JSON files, with configuration files located in the `modules/` directory.

Under the agent_tool_list field, add the functions you want to implement one by one:
- [tool_name](file://f:\ai_share\jacky\oddservice\oddagent\tools\tool_executer_impl.py#L0-L0): Tool name. It is recommended to be the actual API name that needs to be called when implementing this tool.
- `name`: Detailed tool name. A practical, user-understandable name.
- `description`: Detailed tool description.
- `example`: Optional. If this tool requires calling parameters, it is recommended to specifically introduce them here. This introduction will be included in the prompt sent to the large model, helping the model better understand the intent (intent) corresponding to this tool and more accurately parse the slots (slots) of this tool.
- `parameters`: Optional. If this tool requires calling parameters, all parameters need to be listed here. Like example, this content will also be sent to the large model in the prompt to help the model more accurately parse intents and slots.
- `enabled`: Enable or not
- [tool_api_url](file://f:\ai_share\jacky\oddservice\oddagent\tools\tool_executer_impl.py#L0-L0): The API address that needs to be called to implement this tool after identifying the tool intent.
- [tool_api_headers](file://f:\ai_share\jacky\oddservice\oddagent\tools\tool_processor_impl.py#L0-L0): The parameter list that needs to be included in the API header when calling the tool API.
- [tool_api_method](file://f:\ai_share\jacky\oddservice\oddagent\tools\tool_executer_impl.py#L0-L0): The method used when calling the tool API, such as: GET/POST/PUT, etc.

The following is a sample configuration:
```json
{
  "global_variants": [],
  "agent_tool_list": [],
    {
      "tool_name": "meeting_schedule",
      "name": "Schedule Meeting",
      "description": "Meeting scheduling service, can create meetings at specified times and locations.",
      "example": "JSON: [{'name': 'time', 'desc': 'Meeting time, format yyyy-MM-dd HH:mm:ss', 'value': ''}, {'name': 'place', 'desc': 'Meeting location', 'value': ''} ]\nInput: Help me schedule a meeting on April 18, 2046 at 10:00:00 in Beijing\nAnswer: { 'time': '2046-04-18 10:00:00', 'place': 'Beijing' }",
      "parameters": [
        {"name": "time", "desc": "Meeting time, format yyyy-MM-dd HH:mm:ss", "type": "string", "required": false},
        {"name": "place", "desc": "Meeting location", "type": "string", "required": false}
      ],
      "enabled": true,
      "tool_api_url": "https://api.xiaoke.ai/api/meeting_schedule",
      "tool_api_headers": "{'Content-Type': 'application/json', 'Authorization': '{{ api_key }}'}",
      "tool_api_method": "POST"
    }
  ]
}
```

## V. Other Information

### 1. Notes

- Configure LLM: Ensure API_KEY is configured correctly, otherwise LLM service cannot be called
- Production environment considerations:
  - Development environment recommends setting `DEBUG=True`, production environment recommends setting to False
  - Session data is currently stored in memory, production environment recommends using Redis or database
- Tool template configuration: Can be configured according to your own needs for corresponding intent tools
- Voice support: If voice support is needed, you can download, install and deploy the [OddAsr project](https://github.com/oddmeta/oddasr "OddAsr project")
- Tool template configuration and API calls: In [Xiao Luo Tongxue](https://x.oddmeta.net "Xiao Luo Tongxue"), all backend APIs are self-encapsulated, and the API names are usually the tool_name in the tool configuration. However, when a tool needs to call a third-party API to implement actual functionality, the API address (url), headers, method, and parameters are usually varied. Therefore, the structure of the entire tool template configuration has been modified compared to the [Xiao Luo Tongxue](https://x.oddmeta.net "Xiao Luo Tongxue") project, and a separate class for processing API requests ([api_request_composer.py](file://f:\ai_share\jacky\oddservice\oddagent\logic\api_request_composer.py)) and a class for API responses ([api_request_composer.py](file://f:\ai_share\jacky\oddservice\oddagent\logic\api_request_composer.py)) have been created. In the [OddAgent project](https://github.com/oddmeta/oddagent "OddAgent project"), each tool-related business needs to be implemented by users in these two classes.
- Speech recognition optimization: If OddAsr is used to enable voice interaction for OddAgent, some terms (such as names, meeting names, meeting room names, participant lists, etc.) need to be added to OddAsr's request API as hot words to make the speech-to-text function more accurate.

### 2. Pending Features

In some commands of the video conferencing business, there may be scenarios where slot content needs secondary confirmation. For example, when inviting xxx, and there may be multiple similar accounts for the name xxx, it is necessary to add an interruption in the business process to first return the multiple xxx to the frontend, allowing users to choose which xxx to invite.

### 3. Open Source Address

⭐️ [GitHub](https://github.com/oddmeta/oddagent)
📖 [Documentation](https://docs.oddmeta.net/)
