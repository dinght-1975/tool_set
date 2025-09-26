#!/usr/bin/env python3
"""
Linux 工具模块
提供常用的 Linux 命令执行功能
"""

import subprocess
import os
from typing import Optional, Dict, Any
from utils.exception_handler import print_exception_stack
from utils.output import show_info, show_error, write_function_link,write_web_link
#测试

def execute_ls_command(directory: str = None, options: str = "") -> Dict[str, Any]:
    """
    执行 Linux ls 命令  
    
    Args:
        directory (str, optional): 要列出内容的目录路径，如果为None则使用当前目录
        options (str): ls 命令的选项参数，如 "-la", "-lh" 等
        
    Returns:
        Dict[str, Any]: 包含执行结果的字典
            - success (bool): 命令是否执行成功
            - output (str): 命令输出结果
            - error (str): 错误信息（如果有）
            - command (str): 实际执行的命令
            - directory (str): 目标目录
    """    
    try:
        # 如果没有指定目录，使用当前目录
        if directory is None:
            directory = os.getcwd()
        
        show_info(f"Executing ls command in directory: {directory}", "LS Command")
        
        # 验证目录是否存在
        if not os.path.exists(directory):
            error_msg = f"Directory does not exist: {directory}"
            show_error(error_msg, "Directory Error")
            return {
                "success": False,
                "output": "",
                "error": error_msg,
                "command": f"ls {options} {directory}",
                "directory": directory
            }
        
        # 构建完整的 ls 命令
        if options:
            command = ["ls"] + options.split() + [directory]
        else:
            command = ["ls", directory]
        
        show_info(f"Command: {' '.join(command)}", "Command Info")
        
        # 执行命令
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )
        write_web_link(f"https://www.baidu.com", "百度")
        write_function_link("functions/examples/linux_funs_execute_ls_command", "执行 ls 命令", {"directory": "/tmp"})
        # 检查命令执行结果
        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                show_info(f"Command output:\n{output}", "LS Output")
            else:
                show_info("Command executed successfully (no output)", "LS Output")
                
            
            return {
                "success": True,
                "output": output,
                "error": "",
                "command": " ".join(command),
                "directory": directory
            }
        else:
            error_msg = result.stderr.strip()
            show_error(f"Command failed: {error_msg}", "LS Error")
            return {
                "success": False,
                "output": "",
                "error": error_msg,
                "command": " ".join(command),
                "directory": directory
            }
            
    except subprocess.TimeoutExpired:
        error_msg = "Command execution timeout (30 seconds)"
        show_error(error_msg, "Timeout Error")
        return {
            "success": False,
            "output": "",
            "error": error_msg,
            "command": f"ls {options} {directory}",
            "directory": directory
        }
    except Exception as e:
        print_exception_stack(e, "执行 ls 命令", "ERROR")
        error_msg = f"Error executing command: {str(e)}"
        show_error(error_msg, "Execution Error")
        return {
            "success": False,
            "output": "",
            "error": error_msg,
            "command": f"ls {options} {directory}",
            "directory": directory
        }


def list_directory_contents(directory: str = None, show_hidden: bool = False, long_format: bool = False, human_readable: bool = False) -> Dict[str, Any]:
    """
    列出目录内容的便捷方法
    
    Args:
        directory (str, optional): 目录路径，如果为None则使用当前目录
        show_hidden (bool): 是否显示隐藏文件
        long_format (bool): 是否使用长格式显示
        human_readable (bool): 是否使用人类可读的文件大小
        
    Returns:
        Dict[str, Any]: ls 命令的执行结果
    """
    options = []
    
    if show_hidden:
        options.append("-a")
    
    if long_format:
        options.append("-l")
    
    if human_readable:
        options.append("-h")
    
    options_str = " ".join(options)
    
    show_info(f"Listing directory contents with options: {options_str or 'default'}", "Directory Listing")
    return execute_ls_command(directory, options_str)


# 示例用法
if __name__ == "__main__":
    # 测试基本 ls 命令（指定目录）
    print("=== 基本 ls 命令（指定目录） ===")
    result = execute_ls_command("/tmp")
    print(f"成功: {result['success']}")
    print(f"输出: {result['output']}")
    print(f"命令: {result['command']}")
    
    # 测试基本 ls 命令（当前目录）
    print("\n=== 基本 ls 命令（当前目录） ===")
    result = execute_ls_command()
    print(f"成功: {result['success']}")
    print(f"输出: {result['output']}")
    print(f"命令: {result['command']}")
    
    # 测试带参数的 ls 命令
    print("\n=== 带参数的 ls 命令 ===")
    result = execute_ls_command("/tmp", "-la")
    print(f"成功: {result['success']}")
    print(f"输出: {result['output']}")
    print(f"命令: {result['command']}")
    
    # 测试便捷方法（当前目录）
    print("\n=== 便捷方法（当前目录） ===")
    result = list_directory_contents(show_hidden=True, long_format=True, human_readable=True)
    print(f"成功: {result['success']}")
    print(f"输出: {result['output']}")
    print(f"命令: {result['command']}")
