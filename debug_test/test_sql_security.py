#!/usr/bin/env python3
"""
测试 SQL 安全检查功能
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


def test_allowed_queries():
    """测试允许的查询语句"""
    print("=== Testing Allowed Queries ===")
    
    allowed_queries = [
        "SELECT * FROM users",
        "SELECT name, email FROM users WHERE age > ?",
        "SELECT COUNT(*) as total FROM users",
        "WITH temp AS (SELECT * FROM users) SELECT * FROM temp",
        "EXPLAIN SELECT * FROM users",
        "DESCRIBE users",
        "DESC users",
        "SHOW TABLES",
        "PRAGMA table_info(users)",
        "-- This is a comment\nSELECT * FROM users",
        "/* Multi-line comment */\nSELECT * FROM users",
        "SELECT * FROM users WHERE name LIKE '%test%'",
        "SELECT u.name, u.email FROM users u WHERE u.age > 18"
    ]
    
    for i, sql in enumerate(allowed_queries, 1):
        print(f"\n{i}. Testing: {sql[:50]}{'...' if len(sql) > 50 else ''}")
        
        clear_result()
        result = sql_query(sql, "test", None, "sqlite")
        
        print(f"   Success: {result.get('success', False)}")
        print(f"   Error: {result.get('error', '')}")
        
        output_result = get_result()
        print(f"   Output Status: {output_result['status']}")
        print(f"   Output Count: {len(output_result['output'])}")


def test_forbidden_queries():
    """测试禁止的修改语句"""
    print("\n=== Testing Forbidden Queries ===")
    
    forbidden_queries = [
        "INSERT INTO users (name, email) VALUES ('test', 'test@example.com')",
        "UPDATE users SET name = 'new_name' WHERE id = 1",
        "DELETE FROM users WHERE id = 1",
        "DROP TABLE users",
        "CREATE TABLE test (id INT)",
        "ALTER TABLE users ADD COLUMN phone TEXT",
        "TRUNCATE TABLE users",
        "GRANT SELECT ON users TO user1",
        "REVOKE SELECT ON users FROM user1",
        "COMMIT",
        "ROLLBACK",
        "SAVEPOINT sp1",
        "RELEASE SAVEPOINT sp1",
        "EXEC sp_procedure",
        "EXECUTE sp_procedure",
        "CALL procedure_name()",
        "DECLARE @var INT",
        "SET @var = 1",
        "BEGIN TRANSACTION",
        "END",
        "SELECT * FROM users; INSERT INTO users VALUES (1, 'test')",
        "SELECT * FROM users UNION ALL SELECT * FROM users; DROP TABLE users"
    ]
    
    for i, sql in enumerate(forbidden_queries, 1):
        print(f"\n{i}. Testing: {sql[:50]}{'...' if len(sql) > 50 else ''}")
        
        clear_result()
        result = sql_query(sql, "test", None, "sqlite")
        
        print(f"   Success: {result.get('success', False)}")
        print(f"   Error: {result.get('error', '')}")
        
        output_result = get_result()
        print(f"   Output Status: {output_result['status']}")
        print(f"   Output Count: {len(output_result['output'])}")


def test_edge_cases():
    """测试边界情况"""
    print("\n=== Testing Edge Cases ===")
    
    edge_cases = [
        "",  # 空字符串
        "   ",  # 只有空白
        "SELECT",  # 不完整的语句
        "select * from users",  # 小写
        "Select * From Users",  # 混合大小写
        "SELECT * FROM users WHERE name = 'test'; -- comment",  # 带注释
        "SELECT * FROM users /* comment */ WHERE age > 18",  # 多行注释
        "SELECT * FROM users WHERE name IN (SELECT name FROM other_table)",  # 子查询
        "SELECT * FROM users JOIN orders ON users.id = orders.user_id",  # JOIN
        "SELECT * FROM users ORDER BY name LIMIT 10 OFFSET 5",  # 复杂查询
    ]
    
    for i, sql in enumerate(edge_cases, 1):
        print(f"\n{i}. Testing: {sql[:50]}{'...' if len(sql) > 50 else ''}")
        
        clear_result()
        result = sql_query(sql, "test", None, "sqlite")
        
        print(f"   Success: {result.get('success', False)}")
        print(f"   Error: {result.get('error', '')}")
        
        output_result = get_result()
        print(f"   Output Status: {output_result['status']}")
        print(f"   Output Count: {len(output_result['output'])}")


if __name__ == "__main__":
    print("=== Testing SQL Security Check ===\n")
    
    test_allowed_queries()
    test_forbidden_queries()
    test_edge_cases()
    
    print("\n=== All tests completed ===")
