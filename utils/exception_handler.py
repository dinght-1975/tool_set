"""
异常处理工具模块
提供统一的异常处理和堆栈打印功能
"""
import traceback
import logging
from typing import Any, Optional, Callable
import functools

# 设置日志
logger = logging.getLogger(__name__)

def print_exception_stack(exc: Exception, context: str = "", level: str = "ERROR") -> None:
    """
    打印异常堆栈信息
    
    Args:
        exc: 异常对象
        context: 异常发生的上下文描述
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # 获取异常类型和消息
    exc_type = type(exc).__name__
    exc_msg = str(exc)
    
    # 获取完整的堆栈跟踪
    stack_trace = traceback.format_exc()
    
    # 构建日志消息
    log_msg = f"❌ 异常发生"
    if context:
        log_msg += f" - {context}"
    log_msg += f"\n异常类型: {exc_type}\n异常消息: {exc_msg}\n堆栈跟踪:\n{stack_trace}"
    
    # 根据级别打印日志
    if level.upper() == "DEBUG":
        logger.debug(log_msg)
    elif level.upper() == "INFO":
        logger.info(log_msg)
    elif level.upper() == "WARNING":
        logger.warning(log_msg)
    elif level.upper() == "CRITICAL":
        logger.critical(log_msg)
    else:  # ERROR
        logger.error(log_msg)
    
    # 同时打印到控制台（用于调试）
    print(log_msg)

def handle_exception(
    context: str = "",
    level: str = "ERROR",
    return_value: Any = None,
    reraise: bool = False
) -> Callable:
    """
    异常处理装饰器
    
    Args:
        context: 异常发生的上下文描述
        level: 日志级别
        return_value: 异常时返回的值
        reraise: 是否重新抛出异常
    
    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                print_exception_stack(exc, context, level)
                
                if reraise:
                    raise
                else:
                    return return_value
        return wrapper
    return decorator

def safe_execute(
    func: Callable,
    *args,
    context: str = "",
    level: str = "ERROR",
    return_value: Any = None,
    reraise: bool = False,
    **kwargs
) -> Any:
    """
    安全执行函数，捕获并处理异常
    
    Args:
        func: 要执行的函数
        *args: 函数的位置参数
        context: 异常发生的上下文描述
        level: 日志级别
        return_value: 异常时返回的值
        reraise: 是否重新抛出异常
        **kwargs: 函数的关键字参数
    
    Returns:
        函数执行结果或异常时的返回值
    """
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        print_exception_stack(exc, context, level)
        
        if reraise:
            raise
        else:
            return return_value

class ExceptionHandler:
    """异常处理器类"""
    
    def __init__(self, context: str = "", level: str = "ERROR"):
        self.context = context
        self.level = level
    
    def handle(self, exc: Exception, custom_context: str = "") -> None:
        """处理异常"""
        context = custom_context or self.context
        print_exception_stack(exc, context, self.level)
    
    def safe_execute(self, func: Callable, *args, return_value: Any = None, reraise: bool = False, **kwargs) -> Any:
        """安全执行函数"""
        return safe_execute(
            func, *args, 
            context=self.context, 
            level=self.level, 
            return_value=return_value, 
            reraise=reraise, 
            **kwargs
        )

# 创建默认的异常处理器实例
default_handler = ExceptionHandler("默认异常处理器", "ERROR")

# 便捷函数
def log_exception(exc: Exception, context: str = "", level: str = "ERROR") -> None:
    """记录异常"""
    print_exception_stack(exc, context, level)

def safe_call(func: Callable, *args, context: str = "", return_value: Any = None, **kwargs) -> Any:
    """安全调用函数"""
    return safe_execute(func, *args, context=context, return_value=return_value, **kwargs)
