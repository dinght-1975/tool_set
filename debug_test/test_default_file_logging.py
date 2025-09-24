#!/usr/bin/env python3
"""
测试缺省文件日志记录功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

# 不设置任何环境变量，使用缺省配置
# 缺省应该使用文件模式，目录为当前路径下的 execution_logs

from utils.db.sql_db import execute, executemany
from utils.db.exe_log import ExecutionLogger, query_execution_logs


def test_default_file_logging():
    """测试缺省文件日志记录"""
    print("=== 测试缺省文件日志记录 ===")
    
    # 设置当前用户
    ExecutionLogger.set_current_user("default_user")
    
    # 创建测试表
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS test_default (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        value TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
    
    # 执行创建表
    result = execute(create_table_sql)
    print(f"创建表结果: {result['success']}")
    
    # 插入测试数据
    insert_sql = "INSERT INTO test_default (name, value) VALUES (?, ?)"
    insert_result = execute(insert_sql, params=("测试数据", "缺省文件日志"))
    print(f"插入数据结果: {insert_result['success']}, 影响行数: {insert_result['row_count']}")
    
    # 查询数据
    select_sql = "SELECT * FROM test_default WHERE name = ?"
    select_result = execute(select_sql, params=("测试数据",))
    print(f"查询数据结果: {select_result['success']}, 数据行数: {select_result['row_count']}")
    
    # 批量插入数据
    batch_data = [
        ("批量数据1", "文件日志1"),
        ("批量数据2", "文件日志2"),
        ("批量数据3", "文件日志3")
    ]
    batch_result = executemany(insert_sql, batch_data)
    print(f"批量插入结果: {batch_result['success']}, 影响行数: {batch_result['row_count']}")


def test_log_directory_creation():
    """测试日志目录创建"""
    print("\n=== 测试日志目录创建 ===")
    
    # 检查 execution_logs 目录是否被创建
    log_dir = Path.cwd() / 'execution_logs'
    print(f"日志目录路径: {log_dir}")
    print(f"目录是否存在: {log_dir.exists()}")
    
    if log_dir.exists():
        # 列出目录中的文件
        log_files = list(log_dir.glob('*.log'))
        print(f"日志文件数量: {len(log_files)}")
        
        for log_file in log_files:
            print(f"日志文件: {log_file.name}")
            # 显示文件内容的前几行
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:5]  # 只显示前5行
                    print(f"  内容预览:")
                    for i, line in enumerate(lines, 1):
                        print(f"    {i}: {line.strip()}")
            except Exception as e:
                print(f"  读取文件失败: {e}")


def test_log_query():
    """测试日志查询"""
    print("\n=== 测试日志查询 ===")
    
    # 查询所有日志
    all_logs = query_execution_logs(limit=10)
    print(f"总日志数: {len(all_logs)}")
    
    # 按用户查询日志
    user_logs = query_execution_logs(user="default_user", limit=10)
    print(f"用户 default_user 的日志数: {len(user_logs)}")
    
    for i, log in enumerate(user_logs):
        command = log.get('command', '')[:50]
        time_cost = log.get('time_cost_ms', 0)
        success = log.get('success', False)
        user_name = log.get('user_name', 'unknown')
        print(f"  {i+1}. {user_name}: {command}... ({time_cost}ms, {'成功' if success else '失败'})")


def test_configuration_info():
    """测试配置信息"""
    print("\n=== 测试配置信息 ===")
    
    logger = ExecutionLogger.get_instance()
    print(f"日志类型: {logger.config.log_type}")
    print(f"文件目录: {logger.config.get_file_config()}")
    
    # 检查环境变量
    print(f"LOG_TYPE 环境变量: {os.getenv('LOG_TYPE', '未设置')}")
    print(f"LOG_FILE_DIR 环境变量: {os.getenv('LOG_FILE_DIR', '未设置')}")


if __name__ == "__main__":
    print("=== 缺省文件日志记录测试 ===\n")
    
    test_configuration_info()
    test_default_file_logging()
    test_log_directory_creation()
    test_log_query()
    
    print("\n=== 测试完成 ===")
    print(f"当前工作目录: {Path.cwd()}")
    print(f"日志目录: {Path.cwd() / 'execution_logs'}")
