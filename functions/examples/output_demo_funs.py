#!/usr/bin/env python3
"""
演示如何在业务函数中使用 output 模块
"""

from utils.output import show_info, show_error, show_warning


def demo_success_function(name: str = "World"):
    """
    演示成功执行的函数
    
    Args:
        name (str): 要问候的名字
    """
    show_info(f"Hello {name}!", "Greeting")
    show_info("This function executed successfully", "Success")
    show_warning("This is just a demo warning", "Demo Warning")


def demo_error_function():
    """
    演示有错误的函数
    """
    show_info("Starting error demo", "Demo Start")
    
    try:
        # 模拟一些业务逻辑
        result = 10 / 0  # 这会引发 ZeroDivisionError
    except Exception as e:
        show_error(f"Division by zero error: {str(e)}", "Math Error")
        return  # 提前返回，不继续执行
    
    show_info("This line should not be reached", "Unexpected Success")


def demo_mixed_output_function(data: list = None):
    """
    演示混合输出的函数
    
    Args:
        data (list): 要处理的数据列表
    """
    if data is None:
        data = [1, 2, 3, 4, 5]
    
    show_info(f"Processing {len(data)} items", "Data Processing")
    
    try:
        total = 0
        for i, item in enumerate(data):
            if not isinstance(item, (int, float)):
                show_warning(f"Item {i} is not a number: {item}", "Type Warning")
                continue
            
            total += item
            show_info(f"Processed item {i+1}/{len(data)}: {item}", "Progress")
        
        show_info(f"Total sum: {total}", "Result")
        show_info("Processing completed successfully", "Success")
        
    except Exception as e:
        show_error(f"Error during processing: {str(e)}", "Processing Error")


def demo_complex_function(config: dict = None):
    """
    演示复杂业务逻辑的函数
    
    Args:
        config (dict): 配置参数
    """
    if config is None:
        config = {"timeout": 30, "retries": 3, "debug": False}
    
    show_info("Starting complex operation", "Complex Operation")
    show_info(f"Configuration: {config}", "Config")
    
    # 模拟配置验证
    if config.get("timeout", 0) < 10:
        show_warning("Timeout is very short, this might cause issues", "Config Warning")
    
    if config.get("retries", 0) > 5:
        show_warning("Too many retries configured", "Config Warning")
    
    # 模拟处理步骤
    steps = ["Initialize", "Connect", "Process", "Validate", "Complete"]
    
    for i, step in enumerate(steps):
        try:
            show_info(f"Executing step {i+1}: {step}", "Step Progress")
            
            # 模拟步骤执行
            if step == "Connect" and config.get("debug"):
                show_info("Debug mode: simulating connection delay", "Debug Info")
            
            if step == "Process" and i == 2:  # 模拟处理步骤中的警告
                show_warning("Processing is taking longer than expected", "Performance Warning")
            
        except Exception as e:
            show_error(f"Error in step '{step}': {str(e)}", "Step Error")
            break
    
    show_info("Complex operation completed", "Operation Complete")
