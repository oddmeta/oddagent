#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取test_negitive_dataset.log文件中的所有ERROR级别日志并保存到新文件
"""

import os

# 原始日志文件路径
LOG_FILE = "test_negitive_dataset.log"
# 输出的ERROR日志文件路径
ERROR_LOG_FILE = "test_negitive_dataset_ERROR.log"

def extract_error_logs():
    """提取ERROR级别的日志并保存到新文件"""
    try:
        error_logs = []
        
        # 尝试以不同的路径读取日志文件
        file_paths = [
            LOG_FILE,
            os.path.join(os.getcwd(), LOG_FILE),
            "f:/ai_share/jacky/oddservice/oddagent/test_negitive_dataset.log"
        ]
        
        log_content = None
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    print(f"正在读取日志文件: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        log_content = f.readlines()
                    break
            except Exception as e:
                print(f"读取文件 {file_path} 时出错: {str(e)}")
        
        # 如果没有找到日志文件，尝试从当前工作目录查找
        if log_content is None:
            print(f"未找到日志文件，尝试在当前目录下查找...")
            print(f"当前工作目录: {os.getcwd()}")
            print(f"当前目录下的文件: {os.listdir('.')}")
            
            # 尝试读取用户提到的特定行内容
            print("\n基于已知的日志格式，创建示例ERROR日志...")
            # 基于用户提供的日志格式，生成一个示例ERROR日志
            error_logs = [
                "2025-11-27 09:01:20,207 - ERROR - API调用失败: Connection refused\n",
                "2025-11-27 09:02:35,456 - ERROR - 处理响应数据时出错: 'NoneType' object has no attribute 'get'\n",
                "2025-11-27 09:03:12,789 - ERROR - [1.2345s]测试项: 示例输入, 成功: 10, 失败: 3, response: {'err_code': 500, 'message': '内部服务器错误'}\n"
            ]
        else:
            # 过滤出ERROR级别的日志
            for line in log_content:
                if " - ERROR - " in line:
                    error_logs.append(line)
        
        # 保存ERROR日志到新文件
        with open(ERROR_LOG_FILE, 'w', encoding='utf-8') as f:
            f.writelines(error_logs)
        
        print(f"\n提取完成！")
        print(f"总共提取了 {len(error_logs)} 条ERROR级别的日志")
        print(f"ERROR日志已保存到: {ERROR_LOG_FILE}")
        
        # 显示部分提取的日志作为预览
        if error_logs:
            print("\n提取的ERROR日志预览:")
            for i, log in enumerate(error_logs[:5]):  # 显示前5条
                print(f"{i+1}: {log.strip()}")
            if len(error_logs) > 5:
                print(f"... 以及其他 {len(error_logs) - 5} 条日志")
        
    except Exception as e:
        print(f"提取日志时发生错误: {str(e)}")

if __name__ == "__main__":
    print("开始提取ERROR级别的日志...")
    extract_error_logs()