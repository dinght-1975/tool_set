#!/usr/bin/env python3
"""
Database execution wrapper module
Exposes execute, executemany, rollback, and commit methods from sql_db.py
"""

import sys
import os
from typing import Dict, Any, Optional, List, Union

# Add the parent directory to the path to import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from utils.db.sql_db import execute as sql_execute, executemany as sql_executemany, rollback as sql_rollback, commit as sql_commit
except ImportError:
    # Fallback implementation for when sql_db is not available
    def sql_execute(sql: str, db_name: Optional[str] = None, params: Optional[Union[tuple, list, dict]] = None, db_type: str = "sqlite") -> Dict[str, Any]:
        """Fallback execute function"""
        return {"success": False, "error": "Database module not available", "type": "error"}
    
    def sql_executemany(sql: str, params_list: List[Union[tuple, list, dict]], db_name: Optional[str] = None, db_type: str = "sqlite") -> Dict[str, Any]:
        """Fallback executemany function"""
        return {"success": False, "error": "Database module not available", "type": "error"}
    
    def sql_rollback(db_name: str = "all") -> Dict[str, Any]:
        """Fallback rollback function"""
        return {"success": False, "error": "Database module not available", "type": "error"}
    
    def sql_commit(db_name: str = "all") -> Dict[str, Any]:
        """Fallback commit function"""
        return {"success": False, "error": "Database module not available", "type": "error"}


def execute(sql: str, db_name: Optional[str] = None, params: Optional[Union[tuple, list, dict]] = None, db_type: str = "sqlite") -> Dict[str, Any]:
    """
    Execute SQL statement
    
    Args:
        sql: SQL statement, supports parameterized queries (using %s or named parameters)
        db_name: Database name, if None will be extracted from SQL
        params: SQL parameters, can be tuple, list or dict
               - tuple/list: for positional parameters (%s)
               - dict: for named parameters (%(name)s)
        db_type: Database type ("mysql" or "sqlite")
        
    Returns:
        Execution result dictionary
    """
    return sql_execute(sql, db_name, params, db_type)


def executemany(sql: str, params_list: List[Union[tuple, list, dict]], db_name: Optional[str] = None, db_type: str = "sqlite") -> Dict[str, Any]:
    """
    Execute SQL statement multiple times with different parameters
    
    Args:
        sql: SQL statement, supports parameterized queries
        params_list: List of parameters, each element corresponds to one execution
        db_name: Database name, if None will be extracted from SQL
        db_type: Database type ("mysql" or "sqlite")
        
    Returns:
        Execution result dictionary
    """
    return sql_executemany(sql, params_list, db_name, db_type)


def rollback(db_name: str = "all") -> Dict[str, Any]:
    """
    Rollback transaction
    
    Args:
        db_name: Database name, if "all" then rollback all connections
        
    Returns:
        Operation result dictionary
    """
    return sql_rollback(db_name)


def commit(db_name: str = "all") -> Dict[str, Any]:
    """
    Commit transaction
    
    Args:
        db_name: Database name, if "all" then commit all connections
        
    Returns:
        Operation result dictionary
    """
    return sql_commit(db_name)
