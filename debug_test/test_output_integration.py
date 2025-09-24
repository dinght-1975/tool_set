#!/usr/bin/env python3
"""
测试 output 模块与 FastAPI 的集成
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from utils.output import show_info, show_error, show_warning, get_result, clear_result


def test_success_function():
    """测试成功执行的函数"""
    clear_result()
    
    # 模拟业务逻辑
    show_info("Process started successfully", "Startup")
    show_info("Data processing completed", "Processing")
    show_warning("This is just a warning message", "Warning")
    
    # 获取结果
    result = get_result()
    print("Success function result:")
    print(f"Status: {result['status']}")
    print(f"Output count: {len(result['output'])}")
    print(f"Error: {result['error']}")
    print("Output messages:")
    for msg in result['output']:
        print(f"  - {msg['Title']}: {msg['Content']}")
    print()


def test_error_function():
    """测试有错误的函数"""
    clear_result()
    
    try:
        # 模拟业务逻辑
        show_info("Process started", "Startup")
        
        # 模拟一个错误
        raise ValueError("Something went wrong in the business logic")
        
    except Exception as e:
        # 捕获异常并调用 show_error
        show_error(str(e), "Business Logic Error")
    
    # 获取结果
    result = get_result()
    print("Error function result:")
    print(f"Status: {result['status']}")
    print(f"Output count: {len(result['output'])}")
    print(f"Error: {result['error']}")
    print("Output messages:")
    for msg in result['output']:
        print(f"  - {msg['Title']}: {msg['Content']}")
    print()


def test_mixed_output_function():
    """测试混合输出的函数"""
    clear_result()
    
    # 模拟复杂的业务逻辑
    show_info("Starting complex operation", "Complex Operation")
    show_warning("Memory usage is high", "Resource Warning")
    show_info("Step 1 completed", "Progress")
    show_warning("Network latency detected", "Performance Warning")
    show_info("Step 2 completed", "Progress")
    show_info("Operation completed successfully", "Success")
    
    # 获取结果
    result = get_result()
    print("Mixed output function result:")
    print(f"Status: {result['status']}")
    print(f"Output count: {len(result['output'])}")
    print(f"Error: {result['error']}")
    print("Output messages:")
    for msg in result['output']:
        print(f"  - {msg['Title']}: {msg['Content']}")
    print()


if __name__ == "__main__":
    print("=== Testing Output Module Integration ===\n")
    
    print("1. Testing success function:")
    test_success_function()
    
    print("2. Testing error function:")
    test_error_function()
    
    print("3. Testing mixed output function:")
    test_mixed_output_function()
    
    print("=== All tests completed ===")
