#!/usr/bin/env python3
"""
日志配置模块
统一管理项目的日志配置
"""

import logging
import os
from typing import Optional

def setup_logging(level: Optional[str] = None, enable_sql_debug: Optional[bool] = None, enable_console: bool = True):
    """
    设置项目日志配置
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_sql_debug: 是否启用SQL调试日志，None时从环境变量读取
        enable_console: 是否启用控制台输出，默认True
    """
    # 从环境变量获取日志级别，如果没有则使用传入的参数
    log_level = level or os.getenv('LOG_LEVEL', 'INFO')
    
    # 从环境变量获取SQL调试设置
    if enable_sql_debug is None:
        enable_sql_debug = os.getenv('ENABLE_SQL_DEBUG', 'false').lower() in ('true', '1', 'yes')
    
    # 从环境变量获取控制台输出设置
    if enable_console is None:
        enable_console = os.getenv('ENABLE_CONSOLE_LOG', 'true').lower() in ('true', '1', 'yes')
    
    # 如果启用SQL调试，强制设置为DEBUG级别
    if enable_sql_debug:
        log_level = 'DEBUG'
    
    # 转换日志级别
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 清除现有的处理器
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # 设置根logger级别
    root_logger.setLevel(numeric_level)
    
    # 创建控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_formatter = logging.Formatter(log_format)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
    
    # 如果启用SQL调试，特别设置SQL相关的logger
    if enable_sql_debug:
        sql_logger = logging.getLogger('utils.db.sql_db')
        sql_logger.setLevel(logging.DEBUG)
    
    return logging.getLogger(__name__)

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的logger
    
    Args:
        name: logger名称
        
    Returns:
        logging.Logger: logger实例
    """
    return logging.getLogger(name)

# 默认配置
def default_setup():
    """默认日志配置"""
    return setup_logging(enable_sql_debug=True)
