#!/usr/bin/env python3
"""
日志管理工具
提供日志查询、统计、清理等功能
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db.exe_log import query_execution_logs, ExecutionLogger
from utils.output import show_info, show_error, show_warning


def get_logs_by_user(user: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    根据用户查询执行日志
    
    Args:
        user: 用户名
        limit: 限制条数
        
    Returns:
        List[Dict]: 日志记录列表
    """
    show_info(f"Querying logs for user: {user}", "Log Query")
    
    logs = query_execution_logs(user=user, limit=limit)
    
    if logs:
        show_info(f"Found {len(logs)} logs for user {user}", "Log Query Result")
    else:
        show_warning(f"No logs found for user {user}", "Log Query Result")
    
    return logs


def get_logs_by_time_range(start_time: datetime, end_time: Optional[datetime] = None, 
                          limit: int = 100) -> List[Dict[str, Any]]:
    """
    根据时间范围查询执行日志
    
    Args:
        start_time: 开始时间
        end_time: 结束时间，默认为当前时间
        limit: 限制条数
        
    Returns:
        List[Dict]: 日志记录列表
    """
    if end_time is None:
        end_time = datetime.now()
    
    show_info(f"Querying logs from {start_time} to {end_time}", "Log Query")
    
    logs = query_execution_logs(start_time=start_time, end_time=end_time, limit=limit)
    
    if logs:
        show_info(f"Found {len(logs)} logs in time range", "Log Query Result")
    else:
        show_warning("No logs found in time range", "Log Query Result")
    
    return logs


def get_recent_logs(hours: int = 24, limit: int = 100) -> List[Dict[str, Any]]:
    """
    获取最近几小时的执行日志
    
    Args:
        hours: 小时数
        limit: 限制条数
        
    Returns:
        List[Dict]: 日志记录列表
    """
    start_time = datetime.now() - timedelta(hours=hours)
    
    show_info(f"Getting logs from last {hours} hours", "Log Query")
    
    logs = query_execution_logs(start_time=start_time, limit=limit)
    
    if logs:
        show_info(f"Found {len(logs)} logs in last {hours} hours", "Log Query Result")
    else:
        show_warning(f"No logs found in last {hours} hours", "Log Query Result")
    
    return logs


def get_log_statistics(hours: int = 24) -> Dict[str, Any]:
    """
    获取日志统计信息
    
    Args:
        hours: 统计时间范围（小时）
        
    Returns:
        Dict: 统计信息
    """
    show_info(f"Calculating log statistics for last {hours} hours", "Log Statistics")
    
    start_time = datetime.now() - timedelta(hours=hours)
    logs = query_execution_logs(start_time=start_time, limit=10000)  # 获取更多数据用于统计
    
    if not logs:
        show_warning("No logs found for statistics", "Log Statistics")
        return {
            "total_logs": 0,
            "unique_users": 0,
            "avg_execution_time": 0,
            "error_count": 0,
            "success_count": 0
        }
    
    # 统计信息
    total_logs = len(logs)
    unique_users = set()
    total_execution_time = 0
    error_count = 0
    success_count = 0
    
    for log in logs:
        # 用户统计
        user = log.get('user_name') or log.get('user', 'unknown')
        unique_users.add(user)
        
        # 执行时间统计
        time_cost = log.get('time_cost_ms', 0)
        if isinstance(time_cost, (int, float)):
            total_execution_time += time_cost
        
        # 成功/失败统计
        result = log.get('result')
        if result:
            if isinstance(result, dict):
                if result.get('error') or result.get('success') == False:
                    error_count += 1
                else:
                    success_count += 1
            elif isinstance(result, str) and 'error' in result.lower():
                error_count += 1
            else:
                success_count += 1
        else:
            success_count += 1
    
    avg_execution_time = total_execution_time / total_logs if total_logs > 0 else 0
    
    statistics = {
        "total_logs": total_logs,
        "unique_users": len(unique_users),
        "avg_execution_time": round(avg_execution_time, 2),
        "error_count": error_count,
        "success_count": success_count,
        "error_rate": round(error_count / total_logs * 100, 2) if total_logs > 0 else 0
    }
    
    show_info(f"Statistics calculated: {statistics}", "Log Statistics")
    
    return statistics


def get_slow_queries(threshold_ms: int = 1000, limit: int = 20) -> List[Dict[str, Any]]:
    """
    获取慢查询日志
    
    Args:
        threshold_ms: 慢查询阈值（毫秒）
        limit: 限制条数
        
    Returns:
        List[Dict]: 慢查询日志列表
    """
    show_info(f"Finding slow queries (>{threshold_ms}ms)", "Slow Query Analysis")
    
    # 获取最近24小时的日志
    start_time = datetime.now() - timedelta(hours=24)
    logs = query_execution_logs(start_time=start_time, limit=10000)
    
    # 过滤慢查询
    slow_queries = []
    for log in logs:
        time_cost = log.get('time_cost_ms', 0)
        if isinstance(time_cost, (int, float)) and time_cost > threshold_ms:
            slow_queries.append(log)
    
    # 按执行时间排序
    slow_queries.sort(key=lambda x: x.get('time_cost_ms', 0), reverse=True)
    
    # 限制条数
    slow_queries = slow_queries[:limit]
    
    if slow_queries:
        show_info(f"Found {len(slow_queries)} slow queries", "Slow Query Analysis")
    else:
        show_info("No slow queries found", "Slow Query Analysis")
    
    return slow_queries


def get_user_activity_summary(user: str, days: int = 7) -> Dict[str, Any]:
    """
    获取用户活动摘要
    
    Args:
        user: 用户名
        days: 统计天数
        
    Returns:
        Dict: 用户活动摘要
    """
    show_info(f"Generating activity summary for user {user} (last {days} days)", "User Activity")
    
    start_time = datetime.now() - timedelta(days=days)
    logs = query_execution_logs(user=user, start_time=start_time, limit=10000)
    
    if not logs:
        show_warning(f"No activity found for user {user}", "User Activity")
        return {
            "total_commands": 0,
            "avg_execution_time": 0,
            "error_rate": 0,
            "most_used_commands": [],
            "activity_by_day": {}
        }
    
    # 统计信息
    total_commands = len(logs)
    total_execution_time = 0
    error_count = 0
    command_usage = {}
    daily_activity = {}
    
    for log in logs:
        # 执行时间统计
        time_cost = log.get('time_cost_ms', 0)
        if isinstance(time_cost, (int, float)):
            total_execution_time += time_cost
        
        # 错误统计
        result = log.get('result')
        if result and isinstance(result, dict) and result.get('error'):
            error_count += 1
        
        # 命令使用统计
        command = log.get('command', '')
        if command:
            # 提取命令类型（SQL 的第一个词或命令名）
            command_type = command.split()[0].upper() if command.split() else 'UNKNOWN'
            command_usage[command_type] = command_usage.get(command_type, 0) + 1
        
        # 按天统计活动
        execution_time = log.get('execution_time') or log.get('timestamp')
        if execution_time:
            if isinstance(execution_time, str):
                try:
                    execution_time = datetime.fromisoformat(execution_time.replace('Z', '+00:00'))
                except:
                    continue
            
            day_key = execution_time.strftime('%Y-%m-%d')
            daily_activity[day_key] = daily_activity.get(day_key, 0) + 1
    
    # 计算平均值
    avg_execution_time = total_execution_time / total_commands if total_commands > 0 else 0
    error_rate = error_count / total_commands * 100 if total_commands > 0 else 0
    
    # 最常用的命令
    most_used_commands = sorted(command_usage.items(), key=lambda x: x[1], reverse=True)[:5]
    
    summary = {
        "total_commands": total_commands,
        "avg_execution_time": round(avg_execution_time, 2),
        "error_rate": round(error_rate, 2),
        "most_used_commands": most_used_commands,
        "activity_by_day": daily_activity
    }
    
    show_info(f"Activity summary generated: {total_commands} commands, {error_rate:.1f}% error rate", "User Activity")
    
    return summary


def cleanup_old_logs(days: int = 30) -> bool:
    """
    清理旧日志（仅支持 SQLite 和 MySQL）
    
    Args:
        days: 保留天数
        
    Returns:
        bool: 是否清理成功
    """
    show_info(f"Cleaning up logs older than {days} days", "Log Cleanup")
    
    try:
        logger = ExecutionLogger.get_instance()
        
        if logger.config.log_type == 'file':
            show_warning("File logging does not support automatic cleanup", "Log Cleanup")
            return False
        
        # 计算删除时间点
        cutoff_time = datetime.now() - timedelta(days=days)
        
        if logger.config.log_type == 'sqlite':
            # SQLite 清理
            with logger.sqlite_conn:
                cursor = logger.sqlite_conn.cursor()
                cursor.execute(
                    "DELETE FROM execution_logs WHERE execution_time < ?",
                    (cutoff_time.isoformat(),)
                )
                deleted_count = cursor.rowcount
                
        elif logger.config.log_type == 'mysql':
            # MySQL 清理
            with logger.mysql_conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM execution_logs WHERE execution_time < %s",
                    (cutoff_time,)
                )
                deleted_count = cursor.rowcount
                logger.mysql_conn.commit()
        
        show_info(f"Cleaned up {deleted_count} old log entries", "Log Cleanup")
        return True
        
    except Exception as e:
        show_error(f"Failed to cleanup old logs: {str(e)}", "Log Cleanup Error")
        return False
