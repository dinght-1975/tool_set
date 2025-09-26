#!/usr/bin/env python3
"""
Simple SQL database wrapper
Provides basic database operations for tool_set
"""

import sqlite3
import os
import time
import logging
import threading
import json
import re
from typing import Dict, Any, Optional, List, Union, TypedDict
from pathlib import Path
from utils.exception_handler import print_exception_stack
from utils.exe_log import write_sql_log

# MySQL support
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    pymysql = None 

# 创建logger
logger = logging.getLogger(__name__)

# 线程本地存储
_thread_local = threading.local()

# 数据库配置缓存
_db_config = None

def _load_db_config() -> Dict[str, Any]:
    """加载数据库配置"""
    global _db_config
    if _db_config is None:
        config_path = Path(__file__).parent.parent.parent / "db.config.json"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                _db_config = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load db config: {e}")
            _db_config = {"sqlite": {"cache": {"database": "cache.db"}}}
    return _db_config

def _get_first_sqlite_db() -> str:
    """获取第一个 SQLite 数据库名称"""
    config = _load_db_config()
    sqlite_dbs = config.get("sqlite", {})
    if sqlite_dbs:
        return list(sqlite_dbs.keys())[0]
    return "cache"  # 默认值

def _parse_db_name_from_sql(sql: str) -> Optional[str]:
    """
    从 SQL 语句中解析数据库名称
    
    Args:
        sql (str): SQL 语句
        
    Returns:
        Optional[str]: 解析出的数据库名称，如果没有则返回 None
    """
    # 移除注释和多余空白
    sql_clean = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)
    sql_clean = ' '.join(sql_clean.split())
    
    # 匹配 FROM 子句中的数据库.表名格式
    # 支持: FROM db.table, FROM `db`.`table`, FROM "db"."table"
    patterns = [
        r'FROM\s+[`"]?(\w+)[`"]?\.[`"]?\w+[`"]?',  # FROM db.table
        r'JOIN\s+[`"]?(\w+)[`"]?\.[`"]?\w+[`"]?',   # JOIN db.table
        r'UPDATE\s+[`"]?(\w+)[`"]?\.[`"]?\w+[`"]?', # UPDATE db.table
        r'INSERT\s+INTO\s+[`"]?(\w+)[`"]?\.[`"]?\w+[`"]?', # INSERT INTO db.table
        r'DELETE\s+FROM\s+[`"]?(\w+)[`"]?\.[`"]?\w+[`"]?', # DELETE FROM db.table
    ]
    
    for pattern in patterns:
        match = re.search(pattern, sql_clean, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def _resolve_db_name(sql: str, db_name: Optional[str]) -> str:
    """
    解析数据库名称，如果 db_name 为 None 则从 SQL 中解析
    
    Args:
        sql (str): SQL 语句
        db_name (Optional[str]): 指定的数据库名称
        
    Returns:
        str: 解析出的数据库名称
    """
    if db_name is not None:
        return db_name
    
    # 从 SQL 中解析数据库名称
    parsed_db_name = _parse_db_name_from_sql(sql)
    if parsed_db_name:
        return parsed_db_name
    
    # 如果没有解析到数据库名称，使用第一个 SQLite 数据库
    return _get_first_sqlite_db()

def _get_db_config(db_name: str) -> Dict[str, Any]:
    """
    根据数据库名称获取配置信息
    
    Args:
        db_name (str): 数据库名称
        
    Returns:
        Dict[str, Any]: 数据库配置信息
        
    Raises:
        ValueError: 如果找不到对应的数据库配置
    """
    config = _load_db_config()
    
    # 首先检查 MySQL 配置
    mysql_config = config.get("mysql", {})
    if db_name in mysql_config:
        return {
            "type": "mysql",
            "config": mysql_config[db_name]
        }
    
    # 然后检查 SQLite 配置
    sqlite_config = config.get("sqlite", {})
    if db_name in sqlite_config:
        return {
            "type": "sqlite",
            "config": sqlite_config[db_name]
        }
    
    # 如果都没有找到，抛出异常
    available_mysql = list(mysql_config.keys())
    available_sqlite = list(sqlite_config.keys())
    raise ValueError(
        f"Database '{db_name}' not found in configuration. "
        f"Available MySQL databases: {available_mysql}, "
        f"Available SQLite databases: {available_sqlite}"
    )


class SQLResult(TypedDict, total=False):
    """
    SQL 执行结果的结构定义
    
    Attributes:
        success (bool): 执行是否成功
        data (List[Dict[str, Any]]): 查询结果数据 (SELECT 操作)
        row_count (int): 影响的行数
        columns (List[str]): 查询结果的列名 (SELECT 操作)
        error (str): 错误信息
        lastrowid (int): 最后插入的行ID (INSERT 操作)
    """
    success: bool
    data: List[Dict[str, Any]]
    row_count: int
    columns: List[str]
    error: str
    lastrowid: int


def _get_or_create_db_list() -> Dict[str, 'SimpleSQLDB']:
    """
    获取或创建线程本地的数据库列表
    
    Returns:
        Dict[str, SimpleSQLDB]: 数据库名称到数据库对象的映射
    """
    if not hasattr(_thread_local, 'db_list'):
        _thread_local.db_list = {}
    return _thread_local.db_list


def get_db(db_name: str) -> 'SimpleSQLDB':
    """
    获取指定名称的数据库对象
    
    Args:
        db_name (str): 数据库名称
        
    Returns:
        SimpleSQLDB: 数据库对象
    """
    db_list = _get_or_create_db_list()
    
    if db_name not in db_list:
        db_list[db_name] = SimpleSQLDB(db_name)
    
    return db_list[db_name]


def get_db_list() -> Dict[str, 'SimpleSQLDB']:
    """
    获取当前线程的所有数据库对象
    
    Returns:
        Dict[str, SimpleSQLDB]: 数据库名称到数据库对象的映射
    """
    return _get_or_create_db_list()


def clear_db_list():
    """
    清除当前线程的所有数据库连接
    """
    db_list = _get_or_create_db_list()
    for db in db_list.values():
        db.close()
    db_list.clear()


class SimpleSQLDB:
    """Simple SQL database wrapper"""
    
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.db_config = _get_db_config(db_name)
        self.db_type = self.db_config["type"]
        self.connection = None
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None:
            if self.db_type == "sqlite":
                self.connection = self._create_sqlite_connection()
            elif self.db_type == "mysql":
                self.connection = self._create_mysql_connection()
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        
        return self.connection
    
    def _create_sqlite_connection(self) -> sqlite3.Connection:
        """Create SQLite connection"""
        config = self.db_config["config"]
        database = config.get("database", f"{self.db_name}.db")
        
        # 如果是相对路径，创建在 sqlite_dbs 目录下
        if not os.path.isabs(database):
            db_path = Path(__file__).parent.parent.parent / "sqlite_dbs" / database
        else:
            db_path = Path(database)
        
        # 确保目录存在
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        return sqlite3.connect(str(db_path))
    
    def _create_mysql_connection(self):
        """Create MySQL connection"""
        if not MYSQL_AVAILABLE:
            raise ImportError("pymysql is required for MySQL connections. Install it with: pip install pymysql")
        
        config = self.db_config["config"]
        
        return pymysql.connect(
            host=config.get("host", "localhost"),
            port=config.get("port", 3306),
            user=config.get("user", "root"),
            password=config.get("password", ""),
            database=config.get("database", self.db_name),
            charset=config.get("charset", "utf8mb4"),
            autocommit=False
        )
    
    def execute(self, sql: str, params: Optional[Union[tuple, list, dict]] = None) -> SQLResult:
        """Execute SQL statement"""
        start_time = time.time()
        result = None
        
        # 记录SQL和参数日志
        logger.debug(f"Executing SQL on {self.db_name}: {sql}")
        if params:
            logger.debug(f"Parameters: {params}")
        else:
            logger.debug("No parameters")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                # 根据数据库类型转换占位符
                if self.db_type == "mysql":
                    # MySQL 使用 %s 占位符
                    converted_sql = sql.replace('?', '%s')
                else:
                    # SQLite 使用 ? 占位符
                    converted_sql = sql
                cursor.execute(converted_sql, params)
            else:
                cursor.execute(sql)
            
            # Check if it's a SELECT statement
            if sql.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Convert to list of dictionaries
                data = [dict(zip(columns, row)) for row in results]
                
                # 返回结果包含数据和列信息
                result: SQLResult = {
                    "success": True,
                    "data": data,
                    "row_count": len(data),
                    "columns": columns
                }
                
                # 记录执行日志
                time_cost_ms = int((time.time() - start_time) * 1000)
                command_with_params = f"{sql}"
                if params:
                    command_with_params += f" | Params: {params}"
                write_sql_log(
                    command=command_with_params,
                    result=result,
                    time_cost_ms=time_cost_ms
                )
            else:
                # For INSERT, UPDATE, DELETE
                conn.commit()
                row_count = cursor.rowcount
                
                # 获取 lastrowid，MySQL 和 SQLite 的处理方式不同
                if self.db_type == "mysql":
                    lastrowid = cursor.lastrowid if hasattr(cursor, 'lastrowid') else None
                else:  # SQLite
                    lastrowid = cursor.lastrowid
                
                result: SQLResult = {
                    "success": True,
                    "row_count": row_count,
                    "lastrowid": lastrowid
                }
                
                # 记录执行日志
                time_cost_ms = int((time.time() - start_time) * 1000)
                command_with_params = f"{sql}"
                if params:
                    command_with_params += f" | Params: {params}"
                write_sql_log(
                    command=command_with_params,
                    result=result,
                    time_cost_ms=time_cost_ms
                )
            
            return result
                
        except Exception as e:
            print_exception_stack(e, "执行 SQL", "ERROR")
            error_message = str(e)
            result: SQLResult = {
                "success": False,
                "error": error_message
            }
            
            # 记录错误日志
            time_cost_ms = int((time.time() - start_time) * 1000)
            command_with_params = f"{sql}"
            if params:
                command_with_params += f" | Params: {params}"
            write_sql_log(
                command=command_with_params,
                result=result,
                time_cost_ms=time_cost_ms
            )
            
            return result
    
    def executemany(self, sql: str, params_list: List[Union[tuple, list, dict]]) -> SQLResult:
        """Execute SQL statement multiple times"""
        start_time = time.time()
        result = None
        
        # 记录SQL和参数日志
        logger.debug(f"Executing SQL (batch) on {self.db_name}: {sql}")
        logger.debug(f"Batch size: {len(params_list)}")
        logger.debug(f"Parameters list: {params_list}")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # 根据数据库类型转换占位符
            if self.db_type == "mysql":
                # MySQL 使用 %s 占位符
                converted_sql = sql.replace('?', '%s')
            else:
                # SQLite 使用 ? 占位符
                converted_sql = sql
            
            cursor.executemany(converted_sql, params_list)
            conn.commit()
            
            row_count = cursor.rowcount
            result: SQLResult = {
                "success": True,
                "row_count": row_count
            }
            
            # 记录执行日志
            time_cost_ms = int((time.time() - start_time) * 1000)
            command_with_params = f"EXECUTEMANY: {sql} (batch_size: {len(params_list)})"
            if params_list:
                command_with_params += f" | Params: {params_list[:3]}{'...' if len(params_list) > 3 else ''}"
            write_sql_log(
                command=command_with_params,
                result=result,
                time_cost_ms=time_cost_ms
            )
            
            return result
                
        except Exception as e:
            print_exception_stack(e, "执行 SQL", "ERROR")
            error_message = str(e)
            result: SQLResult = {
                "success": False,
                "error": error_message
            }
            
            # 记录错误日志
            time_cost_ms = int((time.time() - start_time) * 1000)
            command_with_params = f"EXECUTEMANY: {sql} (batch_size: {len(params_list)})"
            if params_list:
                command_with_params += f" | Params: {params_list[:3]}{'...' if len(params_list) > 3 else ''}"
            write_sql_log(
                command=command_with_params,
                result=result,
                time_cost_ms=time_cost_ms
            )
            
            return result
    
    def rollback(self) -> SQLResult:
        """Rollback transaction"""
        try:
            conn = self.get_connection()
            conn.rollback()
            return SQLResult(success=True)
        except Exception as e:
            return SQLResult(success=False, error=str(e))
    
    def commit(self) -> SQLResult:
        """Commit transaction"""
        try:
            conn = self.get_connection()
            conn.commit()
            return SQLResult(success=True)
        except Exception as e:
            return SQLResult(success=False, error=str(e))
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None


# Convenience functions
def execute(sql: str, db_name: Optional[str] = None, params: Optional[Union[tuple, list, dict]] = None) -> SQLResult:
    """Execute SQL statement"""
    resolved_db_name = _resolve_db_name(sql, db_name)
    db = get_db(resolved_db_name)
    return db.execute(sql, params)

def executemany(sql: str, params_list: List[Union[tuple, list, dict]], db_name: Optional[str] = None) -> SQLResult:
    """Execute SQL statement multiple times"""
    resolved_db_name = _resolve_db_name(sql, db_name)
    db = get_db(resolved_db_name)
    return db.executemany(sql, params_list)

def rollback(db_name: str) -> SQLResult:
    """Rollback transaction"""
    db = get_db(db_name)
    return db.rollback()

def commit(db_name: str) -> SQLResult:
    """Commit transaction"""
    db = get_db(db_name)
    return db.commit()

def rollback_all() -> Dict[str, SQLResult]:
    """Rollback all database transactions"""
    results = {}
    db_list = get_db_list()
    for db_name, db in db_list.items():
        results[db_name] = db.rollback()
    return results

def commit_all() -> Dict[str, SQLResult]:
    """Commit all database transactions"""
    results = {}
    db_list = get_db_list()
    for db_name, db in db_list.items():
        results[db_name] = db.commit()
    return results
