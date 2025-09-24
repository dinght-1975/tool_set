#!/usr/bin/env python3
"""
执行日志记录系统演示
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['LOG_TYPE'] = 'sqlite'
os.environ['SQLITE_FILE_PATH'] = str(project_root / 'demo_execution_logs.db')

from utils.db.exe_log import write_execution_log, query_execution_logs
from functions.db.db_funs import sql_query
from functions.examples.log_manager import get_log_statistics, get_slow_queries, get_user_activity_summary
from utils.output import clear_result, get_result


def demo_basic_logging():
    """演示基本日志记录功能"""
    print("=== 基本日志记录演示 ===")
    
    # 模拟一些执行日志
    test_logs = [
        ("admin", "SELECT * FROM users WHERE status = 'active'", {"data": [{"id": 1, "name": "John"}]}, 120),
        ("admin", "UPDATE users SET last_login = NOW() WHERE id = 1", {"affected_rows": 1}, 80),
        ("user1", "SELECT COUNT(*) FROM orders WHERE user_id = 1", {"count": 15}, 95),
        ("user2", "SELECT * FROM products WHERE price > 100", {"data": [{"id": 1, "name": "Product A"}]}, 200),
        ("admin", "DELETE FROM temp_table WHERE created_at < '2025-01-01'", {"affected_rows": 50}, 300),
    ]
    
    print("写入测试日志...")
    for user, command, result, cost in test_logs:
        success = write_execution_log(
            user=user,
            command=command,
            result=result,
            execution_time=datetime.now(),
            time_cost_ms=cost
        )
        print(f"  {user}: {command[:30]}... - {'成功' if success else '失败'}")
        time.sleep(0.1)  # 确保时间不同
    
    print(f"\n共写入 {len(test_logs)} 条日志")


def demo_sql_query_logging():
    """演示 SQL 查询自动日志记录"""
    print("\n=== SQL 查询自动日志记录演示 ===")
    
    clear_result()
    
    # 执行一些 SQL 查询（会自动记录日志）
    queries = [
        "SELECT 1 as test_value",
        "SELECT * FROM sqlite_master WHERE type='table'",
        "PRAGMA table_info(sqlite_master)",
        "SELECT datetime('now') as current_time"
    ]
    
    for i, sql in enumerate(queries, 1):
        print(f"\n{i}. 执行查询: {sql}")
        result = sql_query(sql, "demo", None, "sqlite")
        print(f"   结果: {result.get('success', False)}")
        if result.get('data'):
            print(f"   数据: {len(result['data'])} 条记录")


def demo_log_query():
    """演示日志查询功能"""
    print("\n=== 日志查询功能演示 ===")
    
    # 查询所有日志
    all_logs = query_execution_logs(limit=20)
    print(f"总日志数: {len(all_logs)}")
    
    # 按用户查询
    admin_logs = query_execution_logs(user="admin", limit=10)
    print(f"admin 用户的日志: {len(admin_logs)} 条")
    
    # 查询最近1小时的日志
    recent_logs = query_execution_logs(
        start_time=datetime.now() - timedelta(hours=1),
        limit=50
    )
    print(f"最近1小时的日志: {len(recent_logs)} 条")
    
    # 显示最近的日志
    print("\n最近的日志:")
    for log in all_logs[:5]:
        user = log.get('user_name') or log.get('user', 'unknown')
        command = log.get('command', '')[:40]
        time_cost = log.get('time_cost_ms', 0)
        print(f"  {user}: {command}... ({time_cost}ms)")


def demo_statistics():
    """演示统计功能"""
    print("\n=== 统计功能演示 ===")
    
    # 获取统计信息
    stats = get_log_statistics(hours=24)
    print(f"统计信息 (最近24小时):")
    print(f"  总日志数: {stats['total_logs']}")
    print(f"  唯一用户数: {stats['unique_users']}")
    print(f"  平均执行时间: {stats['avg_execution_time']}ms")
    print(f"  错误数: {stats['error_count']}")
    print(f"  成功数: {stats['success_count']}")
    print(f"  错误率: {stats['error_rate']}%")
    
    # 获取慢查询
    slow_queries = get_slow_queries(threshold_ms=100, limit=5)
    print(f"\n慢查询 (>{100}ms):")
    for query in slow_queries:
        user = query.get('user_name') or query.get('user', 'unknown')
        command = query.get('command', '')[:30]
        time_cost = query.get('time_cost_ms', 0)
        print(f"  {user}: {command}... ({time_cost}ms)")
    
    # 获取用户活动摘要
    admin_activity = get_user_activity_summary("admin", days=1)
    print(f"\nadmin 用户活动摘要 (最近1天):")
    print(f"  总命令数: {admin_activity['total_commands']}")
    print(f"  平均执行时间: {admin_activity['avg_execution_time']}ms")
    print(f"  错误率: {admin_activity['error_rate']}%")
    print(f"  最常用命令: {admin_activity['most_used_commands']}")


def demo_file_logging():
    """演示文件日志记录"""
    print("\n=== 文件日志记录演示 ===")
    
    # 切换到文件日志模式
    os.environ['LOG_TYPE'] = 'file'
    os.environ['LOG_FILE_DIR'] = str(project_root / 'demo_logs')
    
    # 重新创建日志记录器
    from utils.db.exe_log import ExecutionLogger
    file_logger = ExecutionLogger()
    
    # 写入一些文件日志
    file_logs = [
        ("system", "ls -la /tmp", {"output": "file1.txt\nfile2.txt", "success": True}, 50),
        ("system", "df -h", {"output": "Filesystem Size Used Avail Use%", "success": True}, 30),
        ("user1", "grep 'error' /var/log/app.log", {"output": "Error: connection failed", "success": True}, 200),
    ]
    
    print("写入文件日志...")
    for user, command, result, cost in file_logs:
        success = file_logger.write_log(
            user=user,
            command=command,
            result=result,
            execution_time=datetime.now(),
            time_cost_ms=cost
        )
        print(f"  {user}: {command} - {'成功' if success else '失败'}")
        time.sleep(0.1)
    
    # 查询文件日志
    file_log_entries = file_logger.query_logs(limit=10)
    print(f"\n文件日志查询结果: {len(file_log_entries)} 条")
    
    for log in file_log_entries:
        user = log.get('user', 'unknown')
        command = log.get('command', '')
        time_cost = log.get('time_cost_ms', 0)
        print(f"  {user}: {command} ({time_cost}ms)")


if __name__ == "__main__":
    print("=== 执行日志记录系统演示 ===\n")
    
    demo_basic_logging()
    demo_sql_query_logging()
    demo_log_query()
    demo_statistics()
    demo_file_logging()
    
    print("\n=== 演示完成 ===")
    print("\n生成的日志文件:")
    print(f"  SQLite: {project_root / 'demo_execution_logs.db'}")
    print(f"  文件日志: {project_root / 'demo_logs'}")
    print("\n您可以使用以下工具查看日志:")
    print("  - SQLite 浏览器查看 .db 文件")
    print("  - 文本编辑器查看 JSONL 文件")
    print("  - 使用 log_manager 模块进行查询和分析")
