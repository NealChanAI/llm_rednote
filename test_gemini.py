#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from google import genai
    from google.genai import types
    print("✅ google-genai 模块导入成功")
    
    # 测试基本功能
    print("✅ 基本导入测试通过")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
except Exception as e:
    print(f"❌ 其他错误: {e}")

print("测试完成") 