#!/usr/bin/env python3
"""
测试 SQL 执行日志记录功能
"""

import os
import sys
import threading
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['LOG_TYPE'] = 'sqlite'
os.environ['SQLITE_FILE_PATH'] = str(project_root / 'sql_test_logs.db')

from utils.db.sql_db import SimpleSQLDB, execute, executemany
from utils.db.exe_log import ExecutionLogger, query_execution_logs
from utils.output import clear_result, get_result, show_info, show_error


def test_basic_sql_logging():
    """测试基本 SQL 日志记录"""
    print("=== 测试基本 SQL 日志记录 ===")
    
    # 创建测试表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS test_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # 执行创建表
    result = execute(create_table_sql)
    print(f"创建表结果: {result['success']}")
    
    # 插入测试数据
    insert_sql = "INSERT INTO test_users (name, email) VALUES (?, ?)"
    insert_result = execute(insert_sql, params=("张三", "zhangsan@example.com"))
    print(f"插入数据结果: {insert_result['success']}, 影响行数: {insert_result['row_count']}")
    
    # 查询数据
    select_sql = "SELECT * FROM test_users WHERE name = ?"
    select_result = execute(select_sql, params=("张三",))
    print(f"查询数据结果: {select_result['success']}, 数据行数: {select_result['row_count']}")
    
    # 更新数据
    update_sql = "UPDATE test_users SET email = ? WHERE name = ?"
    update_result = execute(update_sql, params=("zhangsan_new@example.com", "张三"))
    print(f"更新数据结果: {update_result['success']}, 影响行数: {update_result['row_count']}")
    
    # 删除数据
    delete_sql = "DELETE FROM test_users WHERE name = ?"
    delete_result = execute(delete_sql, params=("张三",))
    print(f"删除数据结果: {delete_result['success']}, 影响行数: {delete_result['row_count']}")


def test_executemany_logging():
    """测试 executemany 日志记录"""
    print("\n=== 测试 executemany 日志记录 ===")
    
    # 批量插入数据
    insert_sql = "INSERT INTO test_users (name, email) VALUES (?, ?)"
    batch_data = [
        ("李四", "lisi@example.com"),
        ("王五", "wangwu@example.com"),
        ("赵六", "zhaoliu@example.com")
    ]
    
    result = executemany(insert_sql, batch_data)
    print(f"批量插入结果: {result['success']}, 影响行数: {result['row_count']}")


def test_thread_local_user():
    """测试线程本地用户信息"""
    print("\n=== 测试线程本地用户信息 ===")
    
    def worker_thread(thread_id: int, user_name: str):
        """工作线程函数"""
        print(f"线程 {thread_id} 开始，用户: {user_name}")
        
        # 设置线程本地用户信息
        ExecutionLogger.set_current_user(user_name)
        
        # 执行一些 SQL 操作
        for i in range(2):
            sql = f"SELECT {i} as test_value, '{user_name}' as user_name"
            result = execute(sql)
            print(f"线程 {thread_id}: 执行 SQL {i} - {'成功' if result['success'] else '失败'}")
            time.sleep(0.1)
        
        print(f"线程 {thread_id} 完成")
    
    # 创建多个线程
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker_thread, args=(i, f"user_{i}"))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("所有线程完成")


def test_log_query():
    """测试日志查询"""
    print("\n=== 测试日志查询 ===")
    
    # 查询所有日志
    all_logs = query_execution_logs(limit=10)
    print(f"总日志数: {len(all_logs)}")
    
    # 按用户查询日志
    for user in ["user_0", "user_1", "user_2"]:
        user_logs = query_execution_logs(user=user, limit=5)
        print(f"用户 {user} 的日志数: {len(user_logs)}")
        
        for log in user_logs:
            command = log.get('command', '')[:50]
            time_cost = log.get('time_cost_ms', 0)
            success = log.get('success', False)
            print(f"  {command}... ({time_cost}ms, {'成功' if success else '失败'})")


def test_error_logging():
    """测试错误日志记录"""
    print("\n=== 测试错误日志记录 ===")
    
    # 执行一个会出错的 SQL
    error_sql = "SELECT * FROM non_existent_table"
    result = execute(error_sql)
    print(f"错误 SQL 执行结果: {result['success']}")
    print(f"错误信息: {result.get('error', 'N/A')}")


def test_performance_logging():
    """测试性能日志记录"""
    print("\n=== 测试性能日志记录 ===")
    
    # 执行一些不同复杂度的查询
    queries = [
        "SELECT 1 as simple_query",
        "SELECT * FROM test_users WHERE id > 0",
        "SELECT COUNT(*) as total FROM test_users",
        "SELECT name, email FROM test_users ORDER BY name"
    ]
    
    for i, sql in enumerate(queries):
        start_time = time.time()
        result = execute(sql)
        end_time = time.time()
        
        print(f"查询 {i+1}: {sql[:30]}... - {'成功' if result['success'] else '失败'} - 耗时: {(end_time - start_time)*1000:.2f}ms")


if __name__ == "__main__":
    print("=== SQL 执行日志记录测试 ===\n")
    
    test_basic_sql_logging()
    test_executemany_logging()
    test_thread_local_user()
    test_log_query()
    test_error_logging()
    test_performance_logging()
    
    print("\n=== 测试完成 ===")
    print(f"日志文件位置: {project_root / 'sql_test_logs.db'}")
