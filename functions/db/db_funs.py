#!/usr/bin/env python3
"""
Database execution wrapper module
Exposes execute, executemany, rollback, and commit methods from sql_db.py
"""

import sys
import os
import re
from typing import Optional, Union

# Add the parent directory to the path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from utils.db.sql_db import execute as sql_execute
from utils.output import show_info, show_error, show_warning


def _is_query_only(sql: str) -> bool:
    """
    检查 SQL 语句是否只包含查询操作
    
    Args:
        sql: SQL 语句
        
    Returns:
        bool: True 如果是查询语句，False 否则
    """
    # 移除注释和多余空白
    # 先处理多行注释
    sql_clean = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    # 再处理单行注释
    sql_clean = re.sub(r'--.*$', '', sql_clean, flags=re.MULTILINE)
    # 最后处理多余空白
    sql_clean = re.sub(r'\s+', ' ', sql_clean.strip())
    
    # 转换为小写进行检查
    sql_lower = sql_clean.lower()
    
    # 允许的查询语句开头
    allowed_starts = ['select', 'with', 'explain', 'pragma']
    
    # 检查是否以允许的查询语句开头
    for start_word in allowed_starts:
        if sql_lower.startswith(start_word):
            return True
    
    # 禁止的修改语句
    forbidden_keywords = [
        'insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate',
        'grant', 'revoke', 'commit', 'rollback', 'savepoint', 'release',
        'exec', 'execute', 'call', 'declare', 'set', 'begin', 'end'
    ]
    
    # 检查是否包含禁止的关键词
    for keyword in forbidden_keywords:
        if re.search(r'\b' + keyword + r'\b', sql_lower):
            return False
    
    return False

def sql_query(sql: str, db_name: Optional[str] = None, params: Optional[Union[tuple, list, dict]] = None, db_type: str = "sqlite") -> dict:
    """
    Execute SQL statement (Query only)
    
    Args:
        sql: SQL statement, supports parameterized queries (using %s or named parameters)
        db_name: Database name, if None will be extracted from SQL
        params: SQL parameters, can be tuple, list or dict
               - tuple/list: for positional parameters (%s)
               - dict: for named parameters (%(name)s)
        db_type: Database type ("mysql" or "sqlite")
        
    Returns:
        dict: SQL execution result with success, data, error fields
    """
    try:
        # 检查 SQL 语句是否只包含查询操作
        if not _is_query_only(sql):
            error_msg = "Only SELECT, WITH, EXPLAIN, and PRAGMA statements are allowed"
            show_error(error_msg, "SQL Security Check")
            return {
                'success': False,
                'data': None,
                'error': error_msg,
                'message': error_msg
            }
        
        show_info(f"Executing SQL query: {sql[:100]}{'...' if len(sql) > 100 else ''}", "SQL Execution")
        
        if params:
            show_info(f"Parameters: {params}", "SQL Parameters")
        
        result = sql_execute(sql, db_name, params)
        
        if result.get('success', False):
            if 'data' in result and result['data']:
                show_info(f"Query executed successfully. Found {len(result['data'])} records", "Query Result")
            else:
                show_info("Query executed successfully", "Query Result")
        else:
            show_error(f"SQL execution failed: {result.get('error', 'Unknown error')}", "SQL Error")
            
        return result
            
    except Exception as e:
        show_error(f"Error executing SQL query: {str(e)}", "SQL Execution Error")
        return {
            'success': False,
            'data': None,
            'error': str(e),
            'message': f"Error executing SQL query: {str(e)}"
        }

