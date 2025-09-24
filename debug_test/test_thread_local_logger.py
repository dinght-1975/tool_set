#!/usr/bin/env python3
"""
测试线程本地 ExecutionLogger 功能
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
os.environ['SQLITE_FILE_PATH'] = str(project_root / 'thread_test_logs.db')

from utils.db.exe_log import ExecutionLogger, write_execution_log, query_execution_logs
from utils.output import clear_result, get_result


def test_thread_local_instances():
    """测试线程本地实例"""
    print("=== 测试线程本地实例 ===")
    
    def worker_thread(thread_id: int, user: str):
        """工作线程函数"""
        print(f"线程 {thread_id} 开始")
        
        # 获取当前线程的 logger 实例
        logger1 = ExecutionLogger.get_instance()
        logger2 = ExecutionLogger.get_instance()
        
        # 验证是同一个实例
        print(f"线程 {thread_id}: logger1 is logger2 = {logger1 is logger2}")
        print(f"线程 {thread_id}: logger1 id = {id(logger1)}")
        
        # 写入一些日志
        for i in range(3):
            success = ExecutionLogger.write_log(
                user=user,
                command=f"SELECT * FROM test_table_{i}",
                result={"data": [{"id": i, "thread": thread_id}]},
                execution_time=datetime.now(),
                time_cost_ms=50 + i * 10
            )
            print(f"线程 {thread_id}: 写入日志 {i} - {'成功' if success else '失败'}")
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


def test_static_methods():
    """测试静态方法"""
    print("\n=== 测试静态方法 ===")
    
    # 测试静态 write_log 方法
    print("测试静态 write_log 方法:")
    success = ExecutionLogger.write_log(
        user="static_test_user",
        command="SELECT COUNT(*) FROM users",
        result={"count": 100},
        execution_time=datetime.now(),
        time_cost_ms=200
    )
    print(f"静态方法写入日志: {'成功' if success else '失败'}")
    
    # 测试静态 query_logs 方法
    print("\n测试静态 query_logs 方法:")
    logs = ExecutionLogger.query_logs(user="static_test_user", limit=5)
    print(f"查询到 {len(logs)} 条日志")
    
    for log in logs:
        user = log.get('user_name') or log.get('user', 'unknown')
        command = log.get('command', '')[:30]
        time_cost = log.get('time_cost_ms', 0)
        print(f"  {user}: {command}... ({time_cost}ms)")


def test_convenience_functions():
    """测试便捷函数"""
    print("\n=== 测试便捷函数 ===")
    
    # 测试便捷函数
    print("测试便捷函数 write_execution_log:")
    success = write_execution_log(
        user="convenience_user",
        command="UPDATE users SET status = 'active'",
        result={"affected_rows": 5},
        execution_time=datetime.now(),
        time_cost_ms=150
    )
    print(f"便捷函数写入日志: {'成功' if success else '失败'}")
    
    # 测试便捷查询函数
    print("\n测试便捷函数 query_execution_logs:")
    logs = query_execution_logs(user="convenience_user", limit=5)
    print(f"便捷函数查询到 {len(logs)} 条日志")
    
    for log in logs:
        user = log.get('user_name') or log.get('user', 'unknown')
        command = log.get('command', '')[:30]
        time_cost = log.get('time_cost_ms', 0)
        print(f"  {user}: {command}... ({time_cost}ms)")


def test_thread_isolation():
    """测试线程隔离"""
    print("\n=== 测试线程隔离 ===")
    
    def thread_a():
        """线程 A"""
        logger = ExecutionLogger.get_instance()
        print(f"线程 A: logger id = {id(logger)}")
        
        # 写入日志
        ExecutionLogger.write_log(
            user="thread_a_user",
            command="SELECT * FROM table_a",
            result={"data": "from thread A"},
            time_cost_ms=100
        )
        print("线程 A: 写入日志完成")
    
    def thread_b():
        """线程 B"""
        logger = ExecutionLogger.get_instance()
        print(f"线程 B: logger id = {id(logger)}")
        
        # 写入日志
        ExecutionLogger.write_log(
            user="thread_b_user",
            command="SELECT * FROM table_b",
            result={"data": "from thread B"},
            time_cost_ms=200
        )
        print("线程 B: 写入日志完成")
    
    # 创建并启动线程
    thread1 = threading.Thread(target=thread_a)
    thread2 = threading.Thread(target=thread_b)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    # 验证日志隔离
    print("\n验证日志隔离:")
    thread_a_logs = ExecutionLogger.query_logs(user="thread_a_user", limit=10)
    thread_b_logs = ExecutionLogger.query_logs(user="thread_b_user", limit=10)
    
    print(f"线程 A 的日志: {len(thread_a_logs)} 条")
    print(f"线程 B 的日志: {len(thread_b_logs)} 条")
    
    # 验证没有交叉
    all_logs = ExecutionLogger.query_logs(limit=20)
    print(f"总日志数: {len(all_logs)} 条")


def test_instance_reuse():
    """测试实例重用"""
    print("\n=== 测试实例重用 ===")
    
    # 在同一线程中多次获取实例
    logger1 = ExecutionLogger.get_instance()
    logger2 = ExecutionLogger.get_instance()
    logger3 = ExecutionLogger.get_instance()
    
    print(f"logger1 is logger2: {logger1 is logger2}")
    print(f"logger2 is logger3: {logger2 is logger3}")
    print(f"logger1 is logger3: {logger1 is logger3}")
    print(f"所有实例 ID: {id(logger1)}, {id(logger2)}, {id(logger3)}")
    
    # 验证配置相同
    print(f"logger1 配置类型: {logger1.config.log_type}")
    print(f"logger2 配置类型: {logger2.config.log_type}")
    print(f"logger3 配置类型: {logger3.config.log_type}")


if __name__ == "__main__":
    print("=== 线程本地 ExecutionLogger 测试 ===\n")
    
    test_thread_local_instances()
    test_static_methods()
    test_convenience_functions()
    test_thread_isolation()
    test_instance_reuse()
    
    print("\n=== 测试完成 ===")
    print(f"日志文件位置: {project_root / 'thread_test_logs.db'}")
