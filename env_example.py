#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mac Python 脚本中获取环境变量的示例
"""

import os

def demo_getenv():
    """演示使用 os.getenv() 获取环境变量"""
    print("=== 使用 os.getenv() ===")
    
    # 获取环境变量，不存在时返回 None
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"GEMINI_API_KEY: {api_key}")
    
    # 获取环境变量，不存在时返回默认值
    api_key_with_default = os.getenv("GEMINI_API_KEY", "未设置")
    print(f"GEMINI_API_KEY (带默认值): {api_key_with_default}")
    
    # 检查环境变量是否存在
    if api_key:
        print("✅ 环境变量已设置")
    else:
        print("❌ 环境变量未设置")

def demo_environ():
    """演示使用 os.environ 获取环境变量"""
    print("\n=== 使用 os.environ ===")
    
    # 使用 get() 方法，不存在时返回 None
    api_key = os.environ.get("GEMINI_API_KEY")
    print(f"GEMINI_API_KEY: {api_key}")
    
    # 直接访问，不存在时抛出 KeyError
    try:
        api_key = os.environ["GEMINI_API_KEY"]
        print(f"GEMINI_API_KEY: {api_key}")
    except KeyError:
        print("❌ 环境变量 GEMINI_API_KEY 不存在")

def demo_set_env():
    """演示在脚本中设置环境变量"""
    print("\n=== 在脚本中设置环境变量 ===")
    
    # 设置环境变量
    os.environ["DEMO_VAR"] = "这是一个演示变量"
    
    # 获取刚设置的环境变量
    demo_var = os.getenv("DEMO_VAR")
    print(f"DEMO_VAR: {demo_var}")

def demo_all_env():
    """显示所有环境变量"""
    print("\n=== 所有环境变量 ===")
    for key, value in os.environ.items():
        if "GEMINI" in key.upper() or "API" in key.upper():
            print(f"{key}: {value}")

if __name__ == "__main__":
    print("Mac Python 环境变量处理示例\n")
    
    demo_getenv()
    demo_environ()
    demo_set_env()
    demo_all_env()
    
    print("\n=== 使用建议 ===")
    print("1. 推荐使用 os.getenv() 方法")
    print("2. 总是检查环境变量是否存在")
    print("3. 敏感信息（如 API 密钥）不要硬编码在代码中")
    print("4. 可以使用 .env 文件管理环境变量") 