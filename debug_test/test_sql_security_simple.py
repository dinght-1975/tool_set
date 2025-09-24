#!/usr/bin/env python3
"""
简化的 SQL 安全检查测试
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


def test_security_check():
    """测试安全检查功能"""
    print("=== Testing SQL Security Check ===\n")
    
    # 测试允许的查询语句
    print("1. Testing allowed queries:")
    allowed_queries = [
        "SELECT 1 as test",
        "SELECT * FROM sqlite_master",
        "PRAGMA table_info(sqlite_master)",
        "WITH temp AS (SELECT 1 as id) SELECT * FROM temp",
        "EXPLAIN SELECT 1",
        "-- This is a comment\nSELECT 1",
        "/* Multi-line comment */\nSELECT 1"
    ]
    
    for i, sql in enumerate(allowed_queries, 1):
        print(f"   {i}. {sql[:50]}{'...' if len(sql) > 50 else ''}")
        clear_result()
        result = sql_query(sql, "test", None, "sqlite")
        print(f"      Success: {result.get('success', False)}")
        if not result.get('success', False):
            print(f"      Error: {result.get('error', '')}")
        print()
    
    # 测试禁止的修改语句
    print("2. Testing forbidden queries:")
    forbidden_queries = [
        "INSERT INTO test VALUES (1)",
        "UPDATE test SET id = 1",
        "DELETE FROM test",
        "DROP TABLE test",
        "CREATE TABLE test (id INT)",
        "ALTER TABLE test ADD COLUMN name TEXT"
    ]
    
    for i, sql in enumerate(forbidden_queries, 1):
        print(f"   {i}. {sql}")
        clear_result()
        result = sql_query(sql, "test", None, "sqlite")
        print(f"      Success: {result.get('success', False)}")
        print(f"      Error: {result.get('error', '')}")
        print()


if __name__ == "__main__":
    test_security_check()
    print("=== Test completed ===")
