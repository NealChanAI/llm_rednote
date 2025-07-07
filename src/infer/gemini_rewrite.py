# -*- coding: utf-8 -*-
# ===============================================================
#
#    @Create Author : chenyongming
#    @Create Time   : 2025-07-06 16:05
#    @Description   : 使用Gemini API进行文本重写
#
# ===============================================================


from ast import main
from google import genai
from google.genai import types
import os
from os import path as osp 
import re
import json
from dotenv import load_dotenv
import argparse
from typing import Optional

load_dotenv()   
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_PATH = os.path.join(ROOT_DIR, "data", "rewrite", "output")
SYSTEM_PROMPT_PATH = os.path.join(ROOT_DIR, "prompts", "rewrite", "system_prompt.txt")
USER_PROMPT_PATH = os.path.join(ROOT_DIR, "prompts", "rewrite", "user_prompt.txt")


def read_txt_file(file_path: str) -> str:
    """
    读取txt文件内容
    
    Args:
        file_path: 文件路径
        
    Returns:
        str: 文件内容
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
        UnicodeDecodeError: 编码错误时抛出
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"文件不存在: {file_path}")
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(f"文件编码错误: {file_path}", e.object, e.start, e.end, e.reason)


def save_txt_file(file_path: str, content: str) -> None:
    """
    保存内容到txt文件
    
    Args:
        file_path: 文件路径
        content: 要保存的内容
        
    Raises:
        IOError: 文件写入失败时抛出
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    except IOError as e:
        raise IOError(f"文件写入失败: {file_path}, 错误: {e}")


def rewrite_content_with_gemini(content: str, system_prompt_path: str, user_prompt_path: str) -> str:
    """
    使用Gemini API重写文本内容
    
    Args:
        content: 待重写的文本内容
        system_prompt_path: 系统提示词文件路径
        user_prompt_path: 用户提示词文件路径
        
    Returns:
        str: Gemini重写后的内容
        
    Raises:
        FileNotFoundError: 提示词文件不存在时抛出
        Exception: Gemini API调用失败时抛出
    """
    try:
        # 读取系统提示词
        system_prompt = read_txt_file(system_prompt_path)
        
        # 读取用户提示词
        user_prompt = read_txt_file(user_prompt_path)
        
        # 将内容替换到用户提示词中
        user_prompt = user_prompt.replace('${content}', content)
        
        # 初始化Gemini客户端
        client = genai.Client(
            vertexai=False,
            api_key=GEMINI_API_KEY
        )
        
        # 调用Gemini API
        response = client.models.generate_content(
            # model='gemini-2.0-flash-exp',
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                top_p=0,
                temperature=0,
                max_output_tokens=2048,
                # thinking_config=types.ThinkingConfig(thinking_budget=1024),
            ),
            contents=user_prompt
        )
        
        # 返回生成的内容
        if response.text is None:
            raise Exception("Gemini API 返回空内容")
        return response.text
        
    except FileNotFoundError as e:
        raise FileNotFoundError(f"提示词文件不存在: {e}")
    except Exception as e:
        raise Exception(f"Gemini API调用失败: {e}")


def workflow_rewrite_content(
    input_file_path: str,
    output_file_path: Optional[str] = None,
    system_prompt_path: str = "prompts/rewrite/system_prompt.txt",
    user_prompt_path: str = "prompts/rewrite/user_prompt.txt"
) -> None:
    """
    完整的内容重写工作流程
    
    该函数将整个重写流程串联起来：
    1. 读取输入文件
    2. 调用Gemini API进行内容重写
    3. 将重写结果保存到输出文件
    
    Args:
        input_file_path: 输入文件路径，可以是相对于data/rewrite/input的路径，也可以是绝对路径
        output_file_path: 输出文件路径，如果不指定则自动生成
        system_prompt_path: 系统提示词文件路径，默认为"prompts/rewrite/system_prompt.txt"
        user_prompt_path: 用户提示词文件路径，默认为"prompts/rewrite/user_prompt.txt"
        
    Returns:
        None
        
    Raises:
        FileNotFoundError: 输入文件或提示词文件不存在时抛出
        Exception: Gemini API调用失败或其他错误时抛出
    """
    try:
        # 1. 读取输入文件内容
        # 处理输入文件路径
        if not osp.isabs(input_file_path):
            _input_file_path = osp.join(ROOT_DIR, 'data', 'rewrite', 'input', input_file_path)
        else:
            _input_file_path = input_file_path
            
        print(f"正在读取输入文件: {_input_file_path}")
        content = read_txt_file(_input_file_path)
        print(f"成功读取文件，内容长度: {len(content)} 字符")
        
        # 2. 调用Gemini API进行内容重写
        print("正在调用Gemini API进行内容重写...")
        rewritten_content = rewrite_content_with_gemini(
            content=content,
            system_prompt_path=system_prompt_path,
            user_prompt_path=user_prompt_path
        )
        print("内容重写完成")
        print(f"重写后的内容长度: {len(rewritten_content)} 字符")
        
        # 3. 保存重写结果到输出文件
        # 处理输出文件路径
        if not output_file_path:
            input_filename = osp.basename(input_file_path)
            name, ext = osp.splitext(input_filename)
            output_filename = f"{name}.output{ext}"
            output_file_path = osp.join(OUTPUT_PATH, output_filename)
        elif not osp.isabs(output_file_path):
            output_file_path = osp.join(OUTPUT_PATH, output_file_path)
            
        print(f"正在保存重写结果到: {output_file_path}")
        save_txt_file(output_file_path, rewritten_content)
        print("重写结果保存成功")
        
        print("🎉 整个重写流程完成！")
        
    except FileNotFoundError as e:
        print(f"❌ 文件不存在错误: {e}")
        raise
    except Exception as e:
        print(f"❌ 重写流程执行失败: {e}")
        raise



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='使用Gemini API重写文本内容')
    parser.add_argument('--input', '-i', type=str, default='20250707-特征穿越.txt',
                      help='输入文件路径')
    parser.add_argument('--output', '-o', type=str,
                      help='输出文件路径')
    parser.add_argument('--system-prompt', '-s', type=str, default=SYSTEM_PROMPT_PATH,
                      help='系统提示词文件路径')
    parser.add_argument('--user-prompt', '-u', type=str, default=USER_PROMPT_PATH,
                      help='用户提示词文件路径')
    
    args = parser.parse_args()
    
    workflow_rewrite_content(
        input_file_path=args.input,
        output_file_path=args.output,
        system_prompt_path=args.system_prompt,
        user_prompt_path=args.user_prompt
    )





