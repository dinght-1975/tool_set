"""
Output utility module for handling different types of output messages.
"""

import threading
from typing import Union, List, Dict, Any, Optional

# Thread-local storage for result object
_thread_local = threading.local()


def _get_or_create_result() -> Dict[str, Any]:
    """
    Get existing result from thread local storage or create a new one.
    
    Returns:
        Dict[str, Any]: Result object with status, output, and error fields
    """
    if not hasattr(_thread_local, 'result'):
        _thread_local.result = {
            "status": True,
            "output": [],
            "error": ""
        }
    return _thread_local.result


def write_output(title: str, type: str, content: Union[str, List, Dict]) -> None:
    """
    Write output with specified title, type, and content to thread-local result object.
    
    Args:
        title (str): The title of the output message
        type (str): The type of output (info, error, warning)
        content (Union[str, List, Dict]): The content to output
    """
    result = _get_or_create_result()
    
    # Add to output array
    result["output"].append({"Title": title, "Content": content})
    
    # Update status and error based on type
    if type == "error":
        result["status"] = False
        result["error"] = str(content)


def show_info(content: Union[str, List, Dict], title: Optional[str] = None) -> None:
    """
    Create an info output message.
    
    Args:
        content (Union[str, List, Dict]): The content to output
        title (Optional[str]): The title of the output message
    """
    write_output(title or "Info", "info", content)


def show_error(content: Union[str, List, Dict], title: Optional[str] = None) -> None:
    """
    Create an error output message.
    
    Args:
        content (Union[str, List, Dict]): The content to output
        title (Optional[str]): The title of the output message
    """
    write_output(title or "Error", "error", content)


def show_warning(content: Union[str, List, Dict], title: Optional[str] = None) -> None:
    """
    Create a warning output message.
    
    Args:
        content (Union[str, List, Dict]): The content to output
        title (Optional[str]): The title of the output message
    """
    write_output(title or "Warning", "warning", content)


def get_result() -> Dict[str, Any]:
    """
    Get the current thread-local result object.
    
    Returns:
        Dict[str, Any]: Current result object with status, output, and error fields
    """
    return _get_or_create_result()


def clear_result() -> None:
    """
    Clear the current thread-local result object.
    """
    if hasattr(_thread_local, 'result'):
        delattr(_thread_local, 'result')
