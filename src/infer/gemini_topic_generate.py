# -*- coding: utf-8 -*-
# ===============================================================
#
#    @Create Author : chenyongming
#    @Create Time   : 2025-07-07 16:29
#    @Description   : 使用Gemini对指定Topic进行生成
#
# ===============================================================

from google import genai
from google.genai import types
import os
import re
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

def read_prompt(file_path):
    """读取提示词文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def save_output(content, topic):
    """保存生成的内容"""
    try:
        # 创建输出目录
        output_dir = Path("data/topic/output")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名（使用时间戳和topic）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{topic.replace(' ', '_')}.txt"
        
        # 保存内容
        output_path = output_dir / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    except Exception as e:
        print(f"保存内容时发生错误: {str(e)}")
        return None

def generate_content(topic):
    """生成内容的主函数"""
    try:
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
        system_prompt = read_prompt("prompts/topic/system_prompt.txt")
        user_prompt = read_prompt("prompts/topic/user_prompt.txt")
        
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
        user_prompt = user_prompt.replace("${content}", topic)
        
        
        print("正在生成内容...")
        
        # 生成内容
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=config,
        )
        
        if response.text:
            # 保存内容
            output_path = save_output(response.text, topic)
            if output_path:
                print(f"内容已生成并保存至: {output_path}")
            else:
                print("保存内容失败")
        else:
            print("生成的内容为空")
            
    except Exception as e:
        print(f"执行过程中发生错误: {str(e)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="要生成内容的主题", default="特征数据泄露data leak")
    
    args = parser.parse_args()
    generate_content(args.topic)
