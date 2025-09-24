#!/usr/bin/env python3
"""
测试执行日志记录功能
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
os.environ['SQLITE_FILE_PATH'] = str(project_root / 'test_execution_logs.db')

from utils.db.exe_log import write_execution_log, query_execution_logs, get_execution_logger
from functions.db.db_funs import sql_query
from utils.output import clear_result, get_result


def test_sqlite_logging():
    """测试 SQLite 日志记录"""
    print("=== Testing SQLite Logging ===")
    
    # 测试写入日志
    success = write_execution_log(
        user="test_user",
        command="SELECT * FROM test_table",
        result={"data": [{"id": 1, "name": "test"}]},
        execution_time=datetime.now(),
        time_cost_ms=150
    )
    
    print(f"Write log success: {success}")
    
    # 测试查询日志
    logs = query_execution_logs(user="test_user", limit=10)
    print(f"Found {len(logs)} logs")
    
    for log in logs:
        print(f"  - User: {log.get('user_name', log.get('user'))}")
        print(f"    Command: {log.get('command', '')[:50]}...")
        print(f"    Time: {log.get('execution_time', log.get('timestamp'))}")
        print(f"    Cost: {log.get('time_cost_ms', 0)}ms")
        print()


def test_sql_query_logging():
    """测试 SQL 查询日志记录"""
    print("=== Testing SQL Query Logging ===")
    
    clear_result()
    
    # 执行 SQL 查询（会自动记录日志）
    result = sql_query("SELECT 1 as test_value", "test", None, "sqlite")
    
    print(f"SQL Query Result: {result}")
    
    # 获取输出信息
    output_result = get_result()
    print(f"Output Status: {output_result['status']}")
    print(f"Output Count: {len(output_result['output'])}")
    print()


def test_file_logging():
    """测试文件日志记录"""
    print("=== Testing File Logging ===")
    
    # 切换到文件日志模式
    os.environ['LOG_TYPE'] = 'file'
    os.environ['LOG_FILE_DIR'] = str(project_root / 'test_logs')
    
    # 重新创建日志记录器
    from utils.db.exe_log import ExecutionLogger
    file_logger = ExecutionLogger()
    
    # 写入测试日志
    success = file_logger.write_log(
        user="file_test_user",
        command="ls -la /tmp",
        result={"output": "file1.txt\nfile2.txt", "success": True},
        execution_time=datetime.now(),
        time_cost_ms=200
    )
    
    print(f"File log write success: {success}")
    
    # 查询日志
    logs = file_logger.query_logs(user="file_test_user", limit=5)
    print(f"Found {len(logs)} file logs")
    
    for log in logs:
        print(f"  - User: {log.get('user')}")
        print(f"    Command: {log.get('command')}")
        print(f"    Time: {log.get('timestamp')}")
        print(f"    Cost: {log.get('time_cost_ms')}ms")
        print()


def test_mysql_logging():
    """测试 MySQL 日志记录（需要 MySQL 服务器）"""
    print("=== Testing MySQL Logging ===")
    
    # 设置 MySQL 配置
    os.environ['LOG_TYPE'] = 'mysql'
    os.environ['DB_IP'] = 'localhost'
    os.environ['DB_PORT'] = '3306'
    os.environ['DB_USER'] = 'root'
    os.environ['DB_PASSWORD'] = 'password'
    os.environ['DB_NAME'] = 'test_logs'
    
    try:
        # 重新创建日志记录器
        from utils.db.exe_log import ExecutionLogger
        mysql_logger = ExecutionLogger()
        
        # 写入测试日志
        success = mysql_logger.write_log(
            user="mysql_test_user",
            command="SELECT COUNT(*) FROM users",
            result={"count": 100},
            execution_time=datetime.now(),
            time_cost_ms=300
        )
        
        print(f"MySQL log write success: {success}")
        
        # 查询日志
        logs = mysql_logger.query_logs(user="mysql_test_user", limit=5)
        print(f"Found {len(logs)} MySQL logs")
        
        for log in logs:
            print(f"  - User: {log.get('user_name')}")
            print(f"    Command: {log.get('command')}")
            print(f"    Time: {log.get('execution_time')}")
            print(f"    Cost: {log.get('time_cost_ms')}ms")
            print()
            
    except Exception as e:
        print(f"MySQL logging test skipped: {e}")
        print("Make sure MySQL server is running and credentials are correct")
        print()


def test_log_query_filters():
    """测试日志查询过滤功能"""
    print("=== Testing Log Query Filters ===")
    
    # 切换回 SQLite 模式
    os.environ['LOG_TYPE'] = 'sqlite'
    os.environ['SQLITE_FILE_PATH'] = str(project_root / 'test_execution_logs.db')
    
    # 重新创建日志记录器
    from utils.db.exe_log import ExecutionLogger
    logger = ExecutionLogger()
    
    # 写入多条测试日志
    test_logs = [
        ("user1", "SELECT * FROM table1", {"data": [1, 2, 3]}, 100),
        ("user2", "SELECT * FROM table2", {"data": [4, 5, 6]}, 200),
        ("user1", "UPDATE table1 SET name='test'", {"affected_rows": 1}, 150),
        ("user3", "SELECT COUNT(*) FROM table3", {"count": 10}, 50),
    ]
    
    for user, command, result, cost in test_logs:
        logger.write_log(user, command, result, datetime.now(), cost)
        time.sleep(0.1)  # 确保时间不同
    
    # 测试按用户过滤
    print("Logs for user1:")
    user1_logs = logger.query_logs(user="user1", limit=10)
    print(f"  Found {len(user1_logs)} logs")
    
    # 测试按时间过滤
    start_time = datetime.now() - timedelta(minutes=1)
    print(f"Logs since {start_time}:")
    recent_logs = logger.query_logs(start_time=start_time, limit=10)
    print(f"  Found {len(recent_logs)} logs")
    
    # 测试限制条数
    print("Last 2 logs:")
    last_logs = logger.query_logs(limit=2)
    print(f"  Found {len(last_logs)} logs")
    
    for log in last_logs:
        print(f"    - {log.get('user_name', log.get('user'))}: {log.get('command', '')[:30]}...")


if __name__ == "__main__":
    print("=== Testing Execution Logging System ===\n")
    
    test_sqlite_logging()
    test_sql_query_logging()
    test_file_logging()
    test_mysql_logging()
    test_log_query_filters()
    
    print("\n=== All tests completed ===")
