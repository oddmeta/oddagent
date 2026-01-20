# -*- coding: utf-8 -*-
"""
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: config_loader.py 
@info: 配置加载器 从JSON文件加载配置，并支持环境变量覆盖
"""
import json
import os

class ConfigObject(dict):
    """同时支持点符号访问和字典式访问的配置对象"""
    def __init__(self, d):
        super().__init__()
        for k, v in d.items():
            if isinstance(v, dict):
                self[k] = ConfigObject(v)
                setattr(self, k, self[k])
            else:
                self[k] = v
                setattr(self, k, v)
    
    def __getattr__(self, name):
        """当点符号访问的属性不存在时调用"""
        if name in self:
            return self[name]
        raise AttributeError(f"'ConfigObject' object has no attribute '{name}'")
    
    def __setattr__(self, name, value):
        """设置属性时调用"""
        self[name] = value
        super().__setattr__(name, value)

# 默认配置文件路径
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'odd_agent_config.json')

class ConfigLoader:
    @staticmethod
    def load_config(config_path=None):
        """加载配置文件，支持从环境变量覆盖特定参数
        
        Args:
            config_path (str, optional): 配置文件路径，如果不指定则使用默认路径
            
        Returns:
            ConfigObject: 配置对象，支持点符号访问和字典式访问
        """
        if not config_path:
            config_path = DEFAULT_CONFIG_PATH
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            
            # # 从环境变量获取并覆盖特定参数
            # env_params = ['GPT_URL', 'MODEL', 'LLM_TYPE', 'API_KEY']
            # for param in env_params:
            #     if param in os.environ:
            #         config_dict[param] = os.environ[param]
            #         value_str = str(os.environ[param])[0:32] + "******" if len(os.environ[param]) > 32 else os.environ[param]
            #         print(f"从环境变量获取配置: {param} = {value_str}")
            
            # 将字典转换为支持两种访问方式的对象
            config = ConfigObject(config_dict)
            
            return config
        except FileNotFoundError:
            print(f"配置文件未找到: {config_path}")
            raise
        except json.JSONDecodeError:
            print(f"配置文件格式错误: {config_path}")
            raise

# 全局配置对象
config = ConfigLoader.load_config()