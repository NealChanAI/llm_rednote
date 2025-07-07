# -*- coding: utf-8 -*-
# ===============================================================
#
#    @Create Author : chenyongming
#    @Create Time   : 2025-07-07 17:38
#    @Description   : 基于gemini对文本内容进行除AI味
#
# ===============================================================


from google import genai
from google.genai import types
import os
import re
import json
import argparse
from os import path as osp 
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv


ROOT_DIR = osp.dirname(osp.dirname(osp.dirname(osp.abspath(__file__))))

def read_prompt(file_path):
    """读取提示词文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_content(file_path):
    """读取需要处理的文本文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return None

def save_output(content, input_file_path):
    """保存生成的内容到原文件目录"""
    try:
        # 获取原文件的目录和文件名
        input_path = Path(input_file_path)
        directory = input_path.parent
        filename = input_path.stem
        extension = input_path.suffix
        
        # 生成新的文件名（添加deai标识）
        new_filename = f"{filename}_deai{extension}"
        output_path = directory / new_filename
        
        # 保存内容
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    except Exception as e:
        print(f"保存内容时发生错误: {str(e)}")
        return None

def generate_content(input_file_path):
    """生成内容的主函数"""
    try:
        # 读取输入文件内容
        content = read_content(input_file_path)
        if not content:
            raise ValueError("无法读取输入文件内容")

        # 加载环境变量
        load_dotenv()
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        if not gemini_api_key:
            raise ValueError("未找到 GEMINI_API_KEY 环境变量")
        
        # 初始化 Gemini 客户端
        client = genai.Client(
            vertexai=False,
            api_key=gemini_api_key
        )
        
        # 配置搜索工具
        grounding_tool = types.Tool(
            google_search = types.GoogleSearch()
        )

        # 读取提示词
        system_prompt = read_prompt("prompts/de_ai/system_prompt.txt")
        user_prompt = read_prompt("prompts/de_ai/user_prompt.txt")
        
        # 设置生成配置
        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            thinking_config=types.ThinkingConfig(thinking_budget=1024),
            system_instruction=system_prompt,
            top_p=0,
            temperature=0,
            max_output_tokens=2048,
        )
        
        # 替换用户提示词中的占位符
        user_prompt = user_prompt.replace("${content}", content)
        
        print("正在生成内容...")
        
        # 生成内容
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=config,
        )
        
        if response.text:
            # 保存内容
            output_path = save_output(response.text, input_file_path)
            if output_path:
                print(f"内容已生成并保存至: {output_path}")
            else:
                print("保存内容失败")
        else:
            print("生成的内容为空")
            
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")

if __name__ == "__main__":
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description='使用Gemini对文本进行AI味道去除处理',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # 添加参数
    parser.add_argument(
        '-f', '--file',
        type=str,
        help='输入文件的路径',
        default=osp.join(ROOT_DIR, 'data', 'topic', 'output', '20250707_172524_特征数据泄露data_leak.txt')
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 执行处理
    generate_content(args.file)