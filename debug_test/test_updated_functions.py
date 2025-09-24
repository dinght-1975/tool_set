#!/usr/bin/env python3
"""
测试更新后的 functions 模块
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

from utils.output import clear_result, get_result
from functions.db.db_funs import sql_query
from functions.examples.linux_funs import execute_ls_command, list_directory_contents
from functions.examples.user_funs import UserTool, add_user, get_user_by_name_and_email, search_users_by_name


def test_db_functions():
    """测试数据库函数"""
    print("=== Testing Database Functions ===")
    
    clear_result()
    
    # 测试 SQL 查询
    db_result = sql_query("SELECT 1 as test_value", "test", None, "sqlite")
    
    print(f"DB Function Return Value:")
    print(f"  Success: {db_result.get('success', False)}")
    print(f"  Data: {db_result.get('data', [])}")
    print(f"  Error: {db_result.get('error', '')}")
    
    result = get_result()
    print(f"DB Function Output:")
    print(f"  Status: {result['status']}")
    print(f"  Output count: {len(result['output'])}")
    print(f"  Error: {result['error']}")
    print()


def test_linux_functions():
    """测试 Linux 函数"""
    print("=== Testing Linux Functions ===")
    
    clear_result()
    
    # 测试 ls 命令
    ls_result = execute_ls_command("/tmp")
    
    print(f"LS Function Return Value:")
    print(f"  Success: {ls_result.get('success', False)}")
    print(f"  Output: {ls_result.get('output', '')[:100]}{'...' if len(ls_result.get('output', '')) > 100 else ''}")
    print(f"  Error: {ls_result.get('error', '')}")
    
    result = get_result()
    print(f"LS Function Output:")
    print(f"  Status: {result['status']}")
    print(f"  Output count: {len(result['output'])}")
    print(f"  Error: {result['error']}")
    print()
    
    # 测试目录列表
    clear_result()
    dir_result = list_directory_contents("/tmp", show_hidden=True, long_format=True)
    
    print(f"Directory Listing Return Value:")
    print(f"  Success: {dir_result.get('success', False)}")
    print(f"  Output: {dir_result.get('output', '')[:100]}{'...' if len(dir_result.get('output', '')) > 100 else ''}")
    print(f"  Error: {dir_result.get('error', '')}")
    
    result = get_result()
    print(f"Directory Listing Output:")
    print(f"  Status: {result['status']}")
    print(f"  Output count: {len(result['output'])}")
    print(f"  Error: {result['error']}")
    print()


def test_user_functions():
    """测试用户函数"""
    print("=== Testing User Functions ===")
    
    clear_result()
    
    # 测试用户工具类
    user_tool = UserTool()
    table_result = user_tool.create_user_table()
    
    print(f"User Table Creation Return Value:")
    print(f"  Success: {table_result.get('success', False)}")
    print(f"  Error: {table_result.get('error', '')}")
    
    result = get_result()
    print(f"User Table Creation Output:")
    print(f"  Status: {result['status']}")
    print(f"  Output count: {len(result['output'])}")
    print(f"  Error: {result['error']}")
    print()
    
    # 测试添加用户
    clear_result()
    add_result = add_user("Test User", "test@example.com", 25, "active")
    
    print(f"Add User Return Value:")
    print(f"  Success: {add_result.get('success', False)}")
    print(f"  Error: {add_result.get('error', '')}")
    
    result = get_result()
    print(f"Add User Output:")
    print(f"  Status: {result['status']}")
    print(f"  Output count: {len(result['output'])}")
    print(f"  Error: {result['error']}")
    print()
    
    # 测试查询用户
    clear_result()
    query_result = get_user_by_name_and_email("Test User", "test@example.com")
    
    print(f"Query User Return Value:")
    print(f"  Success: {query_result.get('success', False)}")
    print(f"  Data count: {len(query_result.get('data', []))}")
    print(f"  Error: {query_result.get('error', '')}")
    
    result = get_result()
    print(f"Query User Output:")
    print(f"  Status: {result['status']}")
    print(f"  Output count: {len(result['output'])}")
    print(f"  Error: {result['error']}")
    print()
    
    # 测试搜索用户
    clear_result()
    search_result = search_users_by_name("%Test%")
    
    print(f"Search User Return Value:")
    print(f"  Success: {search_result.get('success', False)}")
    print(f"  Data count: {len(search_result.get('data', []))}")
    print(f"  Error: {search_result.get('error', '')}")
    
    result = get_result()
    print(f"Search User Output:")
    print(f"  Status: {result['status']}")
    print(f"  Output count: {len(result['output'])}")
    print(f"  Error: {result['error']}")
    print()


def test_error_handling():
    """测试错误处理"""
    print("=== Testing Error Handling ===")
    
    clear_result()
    
    # 测试不存在的目录
    error_result = execute_ls_command("/nonexistent/directory")
    
    print(f"Error Handling Return Value:")
    print(f"  Success: {error_result.get('success', False)}")
    print(f"  Error: {error_result.get('error', '')}")
    
    result = get_result()
    print(f"Error Handling Output:")
    print(f"  Status: {result['status']}")
    print(f"  Output count: {len(result['output'])}")
    print(f"  Error: {result['error']}")
    print()


if __name__ == "__main__":
    print("=== Testing Updated Functions ===\n")
    
    test_db_functions()
    test_linux_functions()
    test_user_functions()
    test_error_handling()
    
    print("=== All tests completed ===")
