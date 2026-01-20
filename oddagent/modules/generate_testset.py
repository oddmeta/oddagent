# -*- coding: utf-8 -*-
""" 
@author: catherine wei
@contact: EMAIL@contact: catherine@oddmeta.com
@software: PyCharm 
@file: generate_testset.py 
@info: 读取当前目录下所有.json.py结尾的文件，并将其中
    的agent_tool_list 字段下的内容只保留tool_name、name、test_instructions、test_answers字段，
    其他字段删除，然后将其转换成json文件，用于自动生成的测试用例
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@info: 读取当前目录下所有.json.py结尾的文件，并将其中
    的agent_tool_list 字段下的内容只保留tool_name、name、test_instructions、test_answers字段，
    其他字段删除，然后将其转换成json文件，用于自动生成的测试用例
"""

import os
import json
import importlib.util
import glob

def load_python_module(file_path):
    """加载Python模块"""
    module_name = os.path.basename(file_path).replace('.', '_')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"无法加载Python模块: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def process_tool_item(tool_item):
    """处理单个工具项，只保留指定字段"""
    # 需要保留的字段
    keep_fields = ['agent_tool_list', 'tool_name', 'name', 'test_instructions', 'test_answers', 'enabled']
    
    # 创建新的工具项字典，只包含需要的字段
    processed_tool = {}
    for field in keep_fields:
        if field in tool_item:
            processed_tool[field] = tool_item[field]
    
    return processed_tool

def process_json_py_file(file_path):
    """处理单个配置文件，支持JSON和Python格式"""
    try:
        agent_tool_list = None
        
        # 根据文件扩展名选择加载方式
        if file_path.endswith('.json'):
            # 直接加载JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                tool_config = json.load(f)
            if isinstance(tool_config, dict) and 'agent_tool_list' in tool_config:
                agent_tool_list = tool_config['agent_tool_list']
        elif file_path.endswith('.py'):
            # 加载Python模块
            module = load_python_module(file_path)
            
            # 检查模块中是否有agent_tool_list属性
            if hasattr(module, 'tool_config'):
                # 从tool_config中获取agent_tool_list
                tool_config = module.tool_config
                if isinstance(tool_config, dict) and 'agent_tool_list' in tool_config:
                    agent_tool_list = tool_config['agent_tool_list']
        else:
            print(f"警告: 不支持的文件格式: {file_path}")
            return None
        
        if agent_tool_list is None:
            print(f"警告: 文件 {file_path} 中没有找到 agent_tool_list 属性")
            return None
        
        # 处理每个工具项
        processed_tools = []
        for tool in agent_tool_list:
            processed_tool = process_tool_item(tool)
            processed_tools.append(processed_tool)
        
        return processed_tools
        
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main(config_file:str = "*", config_file_ext: str = "_config.py"):
    """主函数"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print("==================================================================")
    print(f"开始处理当前目录: {current_dir}")
    print("==================================================================")
    
    # 查找所有配置文件
    config_files = []

    for file_path in glob.glob(f"**/{config_file}{config_file_ext}", recursive=True):
        # 排除__init__.py等非配置文件
        if not os.path.basename(file_path).startswith("__"):
            file_path = os.path.join(current_dir, file_path)
            print(f"处理文件: {file_path}")
            config_files.append(file_path)

    if not config_files:
        print(f"没有找到{config_file_ext}结尾的文件")
        return {"agent_tool_list": []}
    
    print(f"找到 {len(config_files)} 个配置文件")
    print("==================================================================")

    # 处理每个文件
    for file_path in config_files:
        print("------------------------------------------------------------------")
        print(f"处理文件: {file_path}")
        print("------------------------------------------------------------------")
        
        # 处理文件
        processed_tools = process_json_py_file(file_path)
        
        if processed_tools:
            # 生成输出文件名
            base_dir = os.path.dirname(file_path)
            output_filename = os.path.basename(file_path)
            if output_filename.endswith('.py'):
                output_filename = output_filename.replace('.py', '.test.json')
            else:
                output_filename = output_filename.replace('.json', '.test.json')
            output_path = os.path.join(base_dir, output_filename)
            
            # 保存为JSON文件
            result = {
                "agent_tool_list": processed_tools
            }
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"已保存处理后的文件: {output_path}")
            print(f"处理了 {len(processed_tools)} 个工具项")
        else:
            print(f"文件 {file_path} 处理失败")

        print("------------------------------------------------------------------")
    
    print("所有文件处理完成")

if __name__ == "__main__":
    main()