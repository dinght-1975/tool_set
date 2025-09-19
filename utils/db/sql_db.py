#!/usr/bin/env python3
"""
Simple SQL database wrapper
Provides basic database operations for tool_set
"""

import sqlite3
import os
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from utils.exception_handler import print_exception_stack


class SimpleSQLDB:
    """Simple SQL database wrapper"""
    
    def __init__(self, db_name: str = "cache", db_type: str = "sqlite"):
        self.db_name = db_name
        self.db_type = db_type
        self.connections = {}
    
    def get_connection(self, db_name: str = None) -> sqlite3.Connection:
        """Get database connection"""
        if db_name is None:
            db_name = self.db_name
        
        if db_name not in self.connections:
            if self.db_type == "sqlite":
                # Create database file in project directory
                db_path = Path(__file__).parent.parent.parent / f"{db_name}.db"
                self.connections[db_name] = sqlite3.connect(str(db_path))
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        
        return self.connections[db_name]
    
    def execute(self, sql: str, db_name: str = None, params: Optional[Union[tuple, list, dict]] = None) -> Dict[str, Any]:
        """Execute SQL statement"""
        try:
            conn = self.get_connection(db_name)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Check if it's a SELECT statement
            if sql.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Convert to list of dictionaries
                data = [dict(zip(columns, row)) for row in results]
                
                return {
                    "success": True,
                    "type": "select",
                    "data": data,
                    "row_count": len(data),
                    "columns": columns
                }
            else:
                # For INSERT, UPDATE, DELETE
                conn.commit()
                return {
                    "success": True,
                    "type": "modify",
                    "row_count": cursor.rowcount,
                    "lastrowid": cursor.lastrowid
                }
                
        except Exception as e:
            print_exception_stack(e, "执行 SQL", "ERROR")
            return {
                "success": False,
                "type": "error",
                "error": str(e),
                "message": f"Database operation failed: {str(e)}"
            }
    
    def executemany(self, sql: str, params_list: List[Union[tuple, list, dict]], db_name: str = None) -> Dict[str, Any]:
        """Execute SQL statement multiple times"""
        try:
            conn = self.get_connection(db_name)
            cursor = conn.cursor()
            
            cursor.executemany(sql, params_list)
            conn.commit()
            
            return {
                "success": True,
                "type": "modify",
                "row_count": cursor.rowcount
            }
                
        except Exception as e:
            print_exception_stack(e, "执行 SQL", "ERROR")
            return {
                "success": False,
                "type": "error",
                "error": str(e),
                "message": f"Database operation failed: {str(e)}"
            }
    
    def rollback(self, db_name: str = "all") -> Dict[str, Any]:
        """Rollback transaction"""
        try:
            if db_name == "all":
                for conn in self.connections.values():
                    conn.rollback()
            else:
                conn = self.get_connection(db_name)
                conn.rollback()
            
            return {
                "success": True,
                "type": "rollback",
                "message": "Transaction rolled back successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "type": "error",
                "error": str(e),
                "message": f"Rollback failed: {str(e)}"
            }
    
    def commit(self, db_name: str = "all") -> Dict[str, Any]:
        """Commit transaction"""
        try:
            if db_name == "all":
                for conn in self.connections.values():
                    conn.commit()
            else:
                conn = self.get_connection(db_name)
                conn.commit()
            
            return {
                "success": True,
                "type": "commit",
                "message": "Transaction committed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "type": "error",
                "error": str(e),
                "message": f"Commit failed: {str(e)}"
            }
    
    def close_all(self):
        """Close all connections"""
        for conn in self.connections.values():
            conn.close()
        self.connections.clear()


# Global database instance
_db_instance = None

def get_db_instance() -> SimpleSQLDB:
    """Get global database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SimpleSQLDB()
    return _db_instance


# Convenience functions
def execute(sql: str, db_name: Optional[str] = None, params: Optional[Union[tuple, list, dict]] = None, db_type: str = "sqlite") -> Dict[str, Any]:
    """Execute SQL statement"""
    db = get_db_instance()
    return db.execute(sql, db_name, params)

def executemany(sql: str, params_list: List[Union[tuple, list, dict]], db_name: Optional[str] = None, db_type: str = "sqlite") -> Dict[str, Any]:
    """Execute SQL statement multiple times"""
    db = get_db_instance()
    return db.executemany(sql, params_list)

def rollback(db_name: str = "all") -> Dict[str, Any]:
    """Rollback transaction"""
    db = get_db_instance()
    return db.rollback(db_name)

def commit(db_name: str = "all") -> Dict[str, Any]:
    """Commit transaction"""
    db = get_db_instance()
    return db.commit(db_name)
