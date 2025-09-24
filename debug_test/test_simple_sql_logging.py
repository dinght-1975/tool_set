#!/usr/bin/env python3
"""
简化的 SQL 执行日志记录测试
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['LOG_TYPE'] = 'sqlite'
os.environ['SQLITE_FILE_PATH'] = str(project_root / 'simple_sql_test_logs.db')

from utils.db.sql_db import execute, executemany
from utils.db.exe_log import ExecutionLogger, query_execution_logs


def test_basic_sql_logging():
    """测试基本 SQL 日志记录"""
    print("=== 测试基本 SQL 日志记录 ===")
    
    # 设置当前用户
    ExecutionLogger.set_current_user("test_user")
    
    # 创建测试表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS test_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # 执行创建表
    result = execute(create_table_sql)
    print(f"创建表结果: {result['success']}")
    
    # 插入测试数据
    insert_sql = "INSERT INTO test_products (name, price) VALUES (?, ?)"
    insert_result = execute(insert_sql, params=("苹果", 5.5))
    print(f"插入数据结果: {insert_result['success']}, 影响行数: {insert_result['row_count']}")
    
    # 查询数据
    select_sql = "SELECT * FROM test_products WHERE name = ?"
    select_result = execute(select_sql, params=("苹果",))
    print(f"查询数据结果: {select_result['success']}, 数据行数: {select_result['row_count']}")
    
    # 更新数据
    update_sql = "UPDATE test_products SET price = ? WHERE name = ?"
    update_result = execute(update_sql, params=(6.0, "苹果"))
    print(f"更新数据结果: {update_result['success']}, 影响行数: {update_result['row_count']}")


def test_executemany_logging():
    """测试 executemany 日志记录"""
    print("\n=== 测试 executemany 日志记录 ===")
    
    # 批量插入数据
    insert_sql = "INSERT INTO test_products (name, price) VALUES (?, ?)"
    batch_data = [
        ("香蕉", 3.5),
        ("橙子", 4.0),
        ("葡萄", 8.0)
    ]
    
    result = executemany(insert_sql, batch_data)
    print(f"批量插入结果: {result['success']}, 影响行数: {result['row_count']}")


def test_log_query():
    """测试日志查询"""
    print("\n=== 测试日志查询 ===")
    
    # 查询所有日志
    all_logs = query_execution_logs(limit=10)
    print(f"总日志数: {len(all_logs)}")
    
    # 按用户查询日志
    user_logs = query_execution_logs(user="test_user", limit=10)
    print(f"用户 test_user 的日志数: {len(user_logs)}")
    
    for i, log in enumerate(user_logs):
        command = log.get('command', '')[:50]
        time_cost = log.get('time_cost_ms', 0)
        success = log.get('success', False)
        user_name = log.get('user_name', 'unknown')
        print(f"  {i+1}. {user_name}: {command}... ({time_cost}ms, {'成功' if success else '失败'})")


def test_error_logging():
    """测试错误日志记录"""
    print("\n=== 测试错误日志记录 ===")
    
    # 执行一个会出错的 SQL
    error_sql = "SELECT * FROM non_existent_table"
    result = execute(error_sql)
    print(f"错误 SQL 执行结果: {result['success']}")
    print(f"错误信息: {result.get('error', 'N/A')}")


def test_different_users():
    """测试不同用户的日志记录"""
    print("\n=== 测试不同用户的日志记录 ===")
    
    # 用户 1
    ExecutionLogger.set_current_user("admin")
    execute("SELECT 'admin query' as query_type")
    
    # 用户 2
    ExecutionLogger.set_current_user("guest")
    execute("SELECT 'guest query' as query_type")
    
    # 查询不同用户的日志
    admin_logs = query_execution_logs(user="admin", limit=5)
    guest_logs = query_execution_logs(user="guest", limit=5)
    
    print(f"管理员日志数: {len(admin_logs)}")
    print(f"访客日志数: {len(guest_logs)}")


if __name__ == "__main__":
    print("=== 简化 SQL 执行日志记录测试 ===\n")
    
    test_basic_sql_logging()
    test_executemany_logging()
    test_log_query()
    test_error_logging()
    test_different_users()
    
    print("\n=== 测试完成 ===")
    print(f"日志文件位置: {project_root / 'simple_sql_test_logs.db'}")
