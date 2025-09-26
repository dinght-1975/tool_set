"""
Output utility module for handling different types of output messages.
"""

import threading
import json
from typing import Union, List, Dict, Any, Optional

# Thread-local storage for output list
_thread_local = threading.local()


def _get_or_create_output_list() -> List[Dict[str, Any]]:
    """
    Get existing output list from thread local storage or create a new one.
    
    Returns:
        List[Dict[str, Any]]: List of output items
    """
    if not hasattr(_thread_local, 'output_list'):
        _thread_local.output_list = []
    return _thread_local.output_list


def write_output(title: str, type: str, content: Union[str, List, Dict]) -> None:
    """
    Write output with specified title, type, and content to thread-local output list.
    
    Args:
        title (str): The title of the output message
        type (str): The type of output (info, error, warning)
        content (Union[str, List, Dict]): The content to output
    """
    output_list = _get_or_create_output_list()
    
    # Add to output list with title, type, and content
    output_list.append({
        "Title": title,
        "Type": type,
        "Content": content
    })


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


def get_output_data() -> Dict[str, Any]:
    """
    Get the current thread-local output data.
    
    Returns:
        Dict[str, Any]: Current output data with status, output, and error fields
    """
    output_list = _get_or_create_output_list()
    return output_list


def clear_output() -> None:
    """
    Clear the current thread-local output list.
    """
    if hasattr(_thread_local, 'output_list'):
        delattr(_thread_local, 'output_list')


def create_function_link(function_id: str, title: str, params: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a function link string that can be displayed as a clickable link in the UI.
    
    Args:
        function_id (str): The ID of the function to link to
        title (str): The display title for the link
        params (Optional[Dict[str, Any]]): Default parameters to pass to the function
        
    Returns:
        str: A formatted link string that can be parsed by the frontend
    """
    link_data = {
        "type": "function_link",
        "function_id": function_id,
        "title": title,
        "params": params or {}
    }
    
    # Return as a special formatted string that the frontend can parse
    return f"🔗 FUNCTION_LINK: {json.dumps(link_data, ensure_ascii=False)}"


def write_function_link(function_id: str, title: str, params: Optional[Dict[str, Any]] = None) -> None:
    """
    Create a function link and write it to the output as an info message.
    
    Args:
        function_id (str): The ID of the function to link to
        title (str): The display title for the link
        params (Optional[Dict[str, Any]]): Default parameters to pass to the function
    """
    link_string = create_function_link(function_id, title, params)
    show_info(link_string, "Function Link")
