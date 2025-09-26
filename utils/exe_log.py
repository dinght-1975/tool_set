#!/usr/bin/env python3
"""
执行日志记录模块
支持多种存储方式：MySQL, SQLite, 文件
"""

import os
import json
import sqlite3
import pymysql
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from utils.output import show_info, show_error, show_warning
from utils.exception_handler import print_exception_stack


class DateTimeEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，处理 datetime 对象"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class ExecutionLogConfig:
    """执行日志配置管理"""
    
    def __init__(self):
        self.log_type = os.getenv('LOG_TYPE', 'file').lower()
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        if self.log_type not in ['mysql', 'sqlite', 'file']:
            raise ValueError(f"Invalid LOG_TYPE: {self.log_type}. Must be one of: mysql, sqlite, file")
        
        if self.log_type == 'mysql':
            required_vars = ['DB_IP', 'DB_PORT', 'DB_USER', 'DB_PASSWORD']
            missing = [var for var in required_vars if not os.getenv(var)]
            if missing:
                raise ValueError(f"Missing required environment variables for MySQL: {missing}")
        
        elif self.log_type == 'sqlite':
            if not os.getenv('SQLITE_FILE_PATH'):
                # 使用默认路径
                os.environ['SQLITE_FILE_PATH'] = str(Path(__file__).parent.parent.parent / 'execution_logs.db')
        
        elif self.log_type == 'file':
            if not os.getenv('LOG_FILE_DIR'):
                # 使用默认目录：当前路径下的 execution_logs
                os.environ['LOG_FILE_DIR'] = str(Path.cwd() / 'execution_logs')
    
    def get_mysql_config(self) -> Dict[str, Any]:
        """获取 MySQL 配置"""
        return {
            'host': os.getenv('DB_IP'),
            'port': int(os.getenv('DB_PORT', 3306)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME', 'execution_logs'),
            'charset': 'utf8mb4'
        }
    
    def get_sqlite_config(self) -> str:
        """获取 SQLite 文件路径"""
        return os.getenv('SQLITE_FILE_PATH')
    
    def get_file_config(self) -> str:
        """获取文件日志目录"""
        return os.getenv('LOG_FILE_DIR')


class ExecutionLogger:
    """执行日志记录器"""
    
    # 线程本地存储
    _thread_local = threading.local()
    
    def __init__(self):
        self.config = ExecutionLogConfig()
        self._init_storage()
        # 初始化线程变量存储执行日志
        if not hasattr(self._thread_local, 'exe_logs'):
            self._thread_local.exe_logs = []
    
    @classmethod
    def get_instance(cls) -> 'ExecutionLogger':
        """
        获取当前线程的 ExecutionLogger 实例
        如果不存在则创建一个新的
        """
        if not hasattr(cls._thread_local, 'logger'):
            cls._thread_local.logger = cls()
        return cls._thread_local.logger
    
    @staticmethod
    def write_log(command: str, result: Any = None, 
                  execution_time: Optional[datetime] = None, time_cost_ms: int = 0, 
                  command_type: str = "unknown") -> bool:
        """
        写入执行日志的静态方法
        
        Args:
            command: 执行的命令/SQL
            result: 执行结果
            execution_time: 执行时间，默认为当前时间
            time_cost_ms: 执行耗时（毫秒）
            command_type: 命令类型 (sql, linux, ftp, etc.)
            
        Returns:
            bool: 是否写入成功
        """
        logger = ExecutionLogger.get_instance()
        # 从线程变量获取用户信息
        user = logger._get_current_user()
        return logger._write_log_impl(user, command, result, execution_time, time_cost_ms, command_type)
    
    @staticmethod
    def set_current_user(user: str) -> None:
        """
        设置当前线程的用户信息
        
        Args:
            user: 用户名称
        """
        logger = ExecutionLogger.get_instance()
        logger._thread_local.current_user = user
    
    @staticmethod
    def get_thread_logs() -> List[Dict[str, Any]]:
        """
        获取当前线程的执行日志
        
        Returns:
            List[Dict]: 当前线程的执行日志列表
        """
        logger = ExecutionLogger.get_instance()
        return getattr(logger._thread_local, 'exe_logs', [])
    
    @staticmethod
    def clear_thread_logs() -> None:
        """清除当前线程的执行日志"""
        logger = ExecutionLogger.get_instance()
        logger._thread_local.exe_logs = []
    
    @staticmethod
    def query_logs(user: Optional[str] = None, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询执行日志的静态方法
        
        Args:
            user: 用户过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制条数
            
        Returns:
            List[Dict]: 日志记录列表
        """
        logger = ExecutionLogger.get_instance()
        return logger.query_logs(user, start_time, end_time, limit)
    
    def _init_storage(self):
        """初始化存储"""
        try:
            if self.config.log_type == 'mysql':
                self._init_mysql()
            elif self.config.log_type == 'sqlite':
                self._init_sqlite()
            elif self.config.log_type == 'file':
                self._init_file()
            
            show_info(f"Execution logger initialized with {self.config.log_type} storage", "Logger Init")
            
        except Exception as e:
            print_exception_stack(e, "初始化执行日志存储", "ERROR")
            show_error(f"Failed to initialize execution logger: {str(e)}", "Logger Init Error")
    
    def _init_mysql(self):
        """初始化 MySQL 存储"""
        config = self.config.get_mysql_config()
        
        # 创建数据库连接
        self.mysql_conn = pymysql.connect(**config)
        
        # 创建日志表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS execution_logs (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            command TEXT NOT NULL,
            result TEXT,
            execution_time DATETIME NOT NULL,
            time_cost_ms INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_user_time (user_name, execution_time),
            INDEX idx_execution_time (execution_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        
        with self.mysql_conn.cursor() as cursor:
            cursor.execute(create_table_sql)
            self.mysql_conn.commit()
    
    def _init_sqlite(self):
        """初始化 SQLite 存储"""
        db_path = self.config.get_sqlite_config()
        
        # 确保目录存在
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 创建数据库连接
        self.sqlite_conn = sqlite3.connect(db_path)
        
        # 创建日志表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS execution_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            command TEXT NOT NULL,
            result TEXT,
            execution_time TEXT NOT NULL,
            time_cost_ms INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        with self.sqlite_conn:
            self.sqlite_conn.execute(create_table_sql)
            # 创建索引
            self.sqlite_conn.execute("CREATE INDEX IF NOT EXISTS idx_user_time ON execution_logs(user_name, execution_time)")
            self.sqlite_conn.execute("CREATE INDEX IF NOT EXISTS idx_execution_time ON execution_logs(execution_time)")
    
    def _init_file(self):
        """初始化文件存储"""
        log_dir = self.config.get_file_config()
        
        # 确保目录存在
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        self.log_dir = Path(log_dir)
    
    def _write_log_impl(self, user: str, command: str, result: Any = None, 
                       execution_time: Optional[datetime] = None, time_cost_ms: int = 0, 
                       command_type: str = "unknown") -> bool:
        """
        写入执行日志
        
        Args:
            user: 执行用户
            command: 执行的命令/SQL
            result: 执行结果
            execution_time: 执行时间，默认为当前时间
            time_cost_ms: 执行耗时（毫秒）
            command_type: 命令类型 (sql, linux, ftp, etc.)
            
        Returns:
            bool: 是否写入成功
        """
        try:
            if execution_time is None:
                execution_time = datetime.now()
            
            # 处理结果数据
            if result is not None:
                if isinstance(result, (dict, list)):
                    result_str = json.dumps(result, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
                else:
                    result_str = str(result)
            else:
                result_str = None
            
            # 保存到线程变量 - 使用处理后的结果字符串
            self._save_to_thread_logs(user, command, result_str, execution_time, time_cost_ms, command_type)
            
            if self.config.log_type == 'mysql':
                return self._write_mysql_log(user, command, result_str, execution_time, time_cost_ms, command_type)
            elif self.config.log_type == 'sqlite':
                return self._write_sqlite_log(user, command, result_str, execution_time, time_cost_ms, command_type)
            elif self.config.log_type == 'file':
                return self._write_file_log(user, command, result_str, execution_time, time_cost_ms, command_type)
            
        except Exception as e:
            print_exception_stack(e, "写入执行日志", "ERROR")
            show_error(f"Failed to write execution log: {str(e)}", "Log Write Error")
            return False
    
    def _write_mysql_log(self, user: str, command: str, result: str, 
                        execution_time: datetime, time_cost_ms: int, command_type: str = "unknown") -> bool:
        """写入 MySQL 日志"""
        try:
            sql = """
            INSERT INTO execution_logs (user_name, command, result, execution_time, time_cost_ms, command_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            with self.mysql_conn.cursor() as cursor:
                cursor.execute(sql, (user, command, result, execution_time, time_cost_ms, command_type))
                self.mysql_conn.commit()
            
            return True
            
        except Exception as e:
            print_exception_stack(e, "写入 MySQL 日志", "ERROR")
            return False
    
    def _write_sqlite_log(self, user: str, command: str, result: str, 
                         execution_time: datetime, time_cost_ms: int, command_type: str = "unknown") -> bool:
        """写入 SQLite 日志"""
        try:
            sql = """
            INSERT INTO execution_logs (user_name, command, result, execution_time, time_cost_ms, command_type)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            with self.sqlite_conn:
                self.sqlite_conn.execute(sql, (user, command, result, 
                                             execution_time.isoformat(), time_cost_ms, command_type))
            
            return True
            
        except Exception as e:
            print_exception_stack(e, "写入 SQLite 日志", "ERROR")
            return False
    
    def _write_file_log(self, user: str, command: str, result: str, 
                       execution_time: datetime, time_cost_ms: int, command_type: str = "unknown") -> bool:
        """写入文件日志"""
        try:
            # 按日期创建日志文件
            date_str = execution_time.strftime('%Y-%m-%d')
            log_file = self.log_dir / f"execution_logs_{date_str}.jsonl"
            
            # 构建日志条目
            log_entry = {
                'timestamp': execution_time.isoformat(),
                'user': user,
                'command': command,
                'result': result,
                'time_cost_ms': time_cost_ms,
                'command_type': command_type
            }
            
            # 写入文件
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False, cls=DateTimeEncoder) + '\n')
            
            return True
            
        except Exception as e:
            print_exception_stack(e, "写入文件日志", "ERROR")
            return False
    
    def _query_logs_impl(self, user: Optional[str] = None, 
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询执行日志
        
        Args:
            user: 用户过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制条数
            
        Returns:
            List[Dict]: 日志记录列表
        """
        try:
            if self.config.log_type == 'mysql':
                return self._query_mysql_logs(user, start_time, end_time, limit)
            elif self.config.log_type == 'sqlite':
                return self._query_sqlite_logs(user, start_time, end_time, limit)
            elif self.config.log_type == 'file':
                return self._query_file_logs(user, start_time, end_time, limit)
            
        except Exception as e:
            print_exception_stack(e, "查询执行日志", "ERROR")
            show_error(f"Failed to query execution logs: {str(e)}", "Log Query Error")
            return []
    
    def _query_mysql_logs(self, user: Optional[str], start_time: Optional[datetime],
                         end_time: Optional[datetime], limit: int) -> List[Dict[str, Any]]:
        """查询 MySQL 日志"""
        conditions = []
        params = []
        
        if user:
            conditions.append("user_name = %s")
            params.append(user)
        
        if start_time:
            conditions.append("execution_time >= %s")
            params.append(start_time)
        
        if end_time:
            conditions.append("execution_time <= %s")
            params.append(end_time)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
        SELECT id, user_name, command, result, execution_time, time_cost_ms, created_at
        FROM execution_logs
        WHERE {where_clause}
        ORDER BY execution_time DESC
        LIMIT %s
        """
        params.append(limit)
        
        with self.mysql_conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def _query_sqlite_logs(self, user: Optional[str], start_time: Optional[datetime],
                          end_time: Optional[datetime], limit: int) -> List[Dict[str, Any]]:
        """查询 SQLite 日志"""
        conditions = []
        params = []
        
        if user:
            conditions.append("user_name = ?")
            params.append(user)
        
        if start_time:
            conditions.append("execution_time >= ?")
            params.append(start_time.isoformat())
        
        if end_time:
            conditions.append("execution_time <= ?")
            params.append(end_time.isoformat())
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f"""
        SELECT id, user_name, command, result, execution_time, time_cost_ms, created_at
        FROM execution_logs
        WHERE {where_clause}
        ORDER BY execution_time DESC
        LIMIT ?
        """
        params.append(limit)
        
        with self.sqlite_conn:
            cursor = self.sqlite_conn.cursor()
            cursor.execute(sql, params)
            
            # 转换为字典列表
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _query_file_logs(self, user: Optional[str], start_time: Optional[datetime],
                        end_time: Optional[datetime], limit: int) -> List[Dict[str, Any]]:
        """查询文件日志"""
        logs = []
        
        # 获取所有日志文件
        log_files = sorted(self.log_dir.glob("execution_logs_*.jsonl"), reverse=True)
        
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if len(logs) >= limit:
                            break
                        
                        try:
                            log_entry = json.loads(line.strip())
                            
                            # 应用过滤条件
                            if user and log_entry.get('user') != user:
                                continue
                            
                            if start_time:
                                entry_time = datetime.fromisoformat(log_entry['timestamp'])
                                if entry_time < start_time:
                                    continue
                            
                            if end_time:
                                entry_time = datetime.fromisoformat(log_entry['timestamp'])
                                if entry_time > end_time:
                                    continue
                            
                            logs.append(log_entry)
                            
                        except json.JSONDecodeError:
                            continue
                            
            except Exception as e:
                print_exception_stack(e, f"读取日志文件 {log_file}", "WARNING")
                continue
        
        return logs[:limit]
    
    def write_log(self, command: str, result: Any = None, 
                  execution_time: Optional[datetime] = None, time_cost_ms: int = 0, 
                  command_type: str = "unknown") -> bool:
        """
        写入执行日志的公共方法
        
        Args:
            command: 执行的命令/SQL
            result: 执行结果
            execution_time: 执行时间，默认为当前时间
            time_cost_ms: 执行耗时（毫秒）
            command_type: 命令类型 (sql, linux, ftp, etc.)
            
        Returns:
            bool: 是否写入成功
        """
        # 从线程变量获取用户信息
        user = self._get_current_user()
        return self._write_log_impl(user, command, result, execution_time, time_cost_ms, command_type)
    
    def _get_current_user(self) -> str:
        """
        从线程变量获取当前用户
        如果线程变量中没有用户信息，返回默认值
        """
        try:
            # 尝试从线程变量获取用户信息
            if hasattr(self._thread_local, 'current_user'):
                return self._thread_local.current_user
            else:
                # 如果没有设置用户，返回默认值
                return "system"
        except:
            return "system"
    
    def _save_to_thread_logs(self, user: str, command: str, result: Any, 
                           execution_time: datetime, time_cost_ms: int, command_type: str = "unknown") -> None:
        """保存执行日志到线程变量"""
        log_entry = {
            'user': user,
            'command': command,
            'result': result,
            'execution_time': execution_time.isoformat(),
            'time_cost_ms': time_cost_ms,
            'command_type': command_type
        }
        self._thread_local.exe_logs.append(log_entry)
    
    def query_logs(self, user: Optional[str] = None, 
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询执行日志的公共方法
        
        Args:
            user: 用户过滤
            start_time: 开始时间
            end_time: 结束时间
            limit: 限制条数
            
        Returns:
            List[Dict]: 日志记录列表
        """
        return self._query_logs_impl(user, start_time, end_time, limit)


def get_execution_logger() -> ExecutionLogger:
    """获取当前线程的执行日志记录器实例"""
    return ExecutionLogger.get_instance()

def write_execution_log(command: str, result: Any = None, 
                       execution_time: Optional[datetime] = None, time_cost_ms: int = 0, 
                       command_type: str = "unknown") -> bool:
    """
    写入执行日志的便捷函数
    
    Args:
        command: 执行的命令/SQL
        result: 执行结果
        execution_time: 执行时间，默认为当前时间
        time_cost_ms: 执行耗时（毫秒）
        command_type: 命令类型 (sql, linux, ftp, etc.)
        
    Returns:
        bool: 是否写入成功
    """
    logger = ExecutionLogger.get_instance()
    return logger.write_log(command, result, execution_time, time_cost_ms, command_type)

def write_sql_log(command: str, result: Any = None, 
                  execution_time: Optional[datetime] = None, time_cost_ms: int = 0) -> bool:
    """
    写入 SQL 执行日志的便捷函数
    
    Args:
        command: 执行的 SQL 命令
        result: 执行结果
        execution_time: 执行时间，默认为当前时间
        time_cost_ms: 执行耗时（毫秒）
        
    Returns:
        bool: 是否写入成功
    """
    return write_execution_log(command, result, execution_time, time_cost_ms, "sql")

def query_execution_logs(user: Optional[str] = None, 
                        start_time: Optional[datetime] = None,
                        end_time: Optional[datetime] = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
    """
    查询执行日志的便捷函数
    
    Args:
        user: 用户过滤
        start_time: 开始时间
        end_time: 结束时间
        limit: 限制条数
        
    Returns:
        List[Dict]: 日志记录列表
    """
    logger = ExecutionLogger.get_instance()
    return logger.query_logs(user, start_time, end_time, limit)
