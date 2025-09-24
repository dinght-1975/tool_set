#!/usr/bin/env python3
"""
用户工具模块
提供用户相关的数据库操作功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_funs import sql_query
from typing import Optional, Dict, Any, List
from utils.output import show_info, show_error, show_warning


class UserTool:
    """用户工具类"""
    
    def __init__(self):
        """
        初始化用户工具
        使用 db_exe 模块进行数据库操作
        """
        self.db_name = "cache"
        self.db_type = "sqlite"
    
    def create_user_table(self) -> Dict[str, Any]:
        """
        创建用户表
        
        Returns:
            Dict[str, Any]: 执行结果字典
        """
        show_info("Creating user table", "Database Setup")
        
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            age INTEGER,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        result = sql_query(sql, self.db_name, db_type=self.db_type)
        
        if result['success']:
            # 创建索引以提高查询性能
            show_info("Creating indexes for better performance", "Database Setup")
            index_sql = "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"
            sql_query(index_sql, self.db_name, db_type=self.db_type)
            
            index_sql2 = "CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)"
            sql_query(index_sql2, self.db_name, db_type=self.db_type)
            
            show_info("User table and indexes created successfully", "Database Setup")
        
        return result
    
    def add_user(self, name: str, email: str, age: Optional[int] = None, status: str = "active") -> Dict[str, Any]:
        """
        添加用户
        
        Args:
            name: 用户名称
            email: 用户邮件地址
            age: 用户年龄（可选）
            status: 用户状态，默认为 'active'
            
        Returns:
            Dict[str, Any]: 执行结果字典
        """
        show_info(f"Adding user: {name} ({email})", "User Management")
        
        sql = "INSERT INTO users (name, email, age, status) VALUES (?, ?, ?, ?)"
        params = (name, email, age, status)
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success']:
            show_info(f"User {name} added successfully", "User Management")
        
        return result
    
    def get_user_by_name(self, name: str) -> Dict[str, Any]:
        """
        根据用户名称查询用户
        
        Args:
            name: 用户名称
            
        Returns:
            Dict[str, Any]: 查询结果字典
        """
        show_info(f"Searching for user by name: {name}", "User Query")
        
        sql = "SELECT * FROM users WHERE name = ?"
        params = (name,)
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success'] and result.get('data'):
            show_info(f"Found {len(result['data'])} user(s) with name '{name}'", "Query Result")
        
        return result
    
    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        根据用户邮件地址查询用户
        
        Args:
            email: 用户邮件地址
            
        Returns:
            Dict[str, Any]: 查询结果字典
        """
        show_info(f"Searching for user by email: {email}", "User Query")
        
        sql = "SELECT * FROM users WHERE email = ?"
        params = (email,)
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success'] and result.get('data'):
            show_info(f"Found {len(result['data'])} user(s) with email '{email}'", "Query Result")
        
        return result
    
    def get_user_by_name_and_email(self, name: str, email: str) -> Dict[str, Any]:
        """
        根据用户名称和邮件地址查询用户
        
        Args:
            name: 用户名称
            email: 用户邮件地址
            
        Returns:
            Dict[str, Any]: 查询结果字典
        """
        show_info(f"Searching for user by name and email: {name} ({email})", "User Query")
        
        sql = "SELECT * FROM users WHERE name = ? AND email = ?"
        params = (name, email)
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success'] and result.get('data'):
            show_info(f"Found {len(result['data'])} user(s) with name '{name}' and email '{email}'", "Query Result")
        
        return result
    
    def search_users_by_name(self, name_pattern: str) -> Dict[str, Any]:
        """
        根据用户名称模糊查询用户
        
        Args:
            name_pattern: 用户名称模式（支持 % 通配符）
            
        Returns:
            Dict[str, Any]: 查询结果字典
        """
        show_info(f"Searching users by name pattern: {name_pattern}", "User Search")
        
        sql = "SELECT * FROM users WHERE name LIKE ?"
        params = (name_pattern,)
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success'] and result.get('data'):
            show_info(f"Found {len(result['data'])} user(s) matching pattern '{name_pattern}'", "Search Result")
        
        return result
    
    def get_all_users(self, limit: Optional[int] = None, offset: int = 0) -> Dict[str, Any]:
        """
        获取所有用户
        
        Args:
            limit: 限制返回的记录数
            offset: 偏移量
            
        Returns:
            Dict[str, Any]: 查询结果字典
        """
        show_info(f"Getting all users (limit: {limit}, offset: {offset})", "User Query")
        
        if limit:
            sql = "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params = (limit, offset)
        else:
            sql = "SELECT * FROM users ORDER BY created_at DESC"
            params = None
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success'] and result.get('data'):
            show_info(f"Retrieved {len(result['data'])} user(s)", "Query Result")
        
        return result
    
    def update_user(self, user_id: int, name: Optional[str] = None, email: Optional[str] = None, 
                   age: Optional[int] = None, status: Optional[str] = None) -> Dict[str, Any]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            name: 新的用户名称（可选）
            email: 新的邮件地址（可选）
            age: 新的年龄（可选）
            status: 新的状态（可选）
            
        Returns:
            Dict[str, Any]: 执行结果字典
        """
        show_info(f"Updating user ID: {user_id}", "User Update")
        
        # 构建动态更新SQL
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
            show_info(f"  - Name: {name}", "Update Fields")
        
        if email is not None:
            updates.append("email = ?")
            params.append(email)
            show_info(f"  - Email: {email}", "Update Fields")
        
        if age is not None:
            updates.append("age = ?")
            params.append(age)
            show_info(f"  - Age: {age}", "Update Fields")
        
        if status is not None:
            updates.append("status = ?")
            params.append(status)
            show_info(f"  - Status: {status}", "Update Fields")
        
        if not updates:
            show_error("No fields provided for update", "Update Error")
            return {'success': False, 'type': 'error', 'error': '没有提供要更新的字段', 'message': '没有提供要更新的字段'}
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success']:
            show_info(f"User {user_id} updated successfully", "User Update")
        
        return result
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 执行结果字典
        """
        show_info(f"Deleting user ID: {user_id}", "User Deletion")
        
        sql = "DELETE FROM users WHERE id = ?"
        params = (user_id,)
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success']:
            show_info(f"User {user_id} deleted successfully", "User Deletion")
        
        return result
    
    def get_user_count(self) -> Dict[str, Any]:
        """
        获取用户总数
        
        Returns:
            Dict[str, Any]: 查询结果字典
        """
        show_info("Getting total user count", "User Statistics")
        
        sql = "SELECT COUNT(*) as total FROM users"
        
        result = sql_query(sql, self.db_name, db_type=self.db_type)
        
        if result['success'] and result.get('data'):
            count = result['data'][0]['total'] if result['data'] else 0
            show_info(f"Total user count: {count}", "Statistics Result")
        
        return result
    
    def get_users_by_status(self, status: str) -> Dict[str, Any]:
        """
        根据状态查询用户
        
        Args:
            status: 用户状态
            
        Returns:
            Dict[str, Any]: 查询结果字典
        """
        show_info(f"Getting users with status: {status}", "User Query")
        
        sql = "SELECT * FROM users WHERE status = ? ORDER BY created_at DESC"
        params = (status,)
        
        result = sql_query(sql, self.db_name, params, self.db_type)
        
        if result['success'] and result.get('data'):
            show_info(f"Found {len(result['data'])} user(s) with status '{status}'", "Query Result")
        
        return result


# 便捷函数
def get_user_by_name_and_email(name: str, email: str) -> Dict[str, Any]:
    """
    根据用户名称和邮件地址查询用户的便捷函数
    
    Args:
        name: 用户名称
        email: 用户邮件地址
        
    Returns:
        Dict[str, Any]: 查询结果字典
    """
    user_tool = UserTool()
    return user_tool.get_user_by_name_and_email(name, email)


def add_user(name: str, email: str, age: Optional[int] = None, status: str = "active") -> Dict[str, Any]:
    """
    添加用户的便捷函数
    
    Args:
        name: 用户名称
        email: 用户邮件地址
        age: 用户年龄（可选）
        status: 用户状态，默认为 'active'
        
    Returns:
        Dict[str, Any]: 执行结果字典
    """
    user_tool = UserTool()
    return user_tool.add_user(name, email, age, status)


def search_users_by_name(name_pattern: str) -> Dict[str, Any]:
    """
    根据用户名称模糊查询用户的便捷函数
    
    Args:
        name_pattern: 用户名称模式（支持 % 通配符）
        
    Returns:
        Dict[str, Any]: 查询结果字典
    """
    user_tool = UserTool()
    return user_tool.search_users_by_name(name_pattern)
    


# 测试函数
def test_user_tool():
    """测试用户工具功能"""
    print("=== 测试用户工具功能 ===")
    
    user_tool = UserTool()
    
    # 创建用户表
    print("\n1. 创建用户表")
    result = user_tool.create_user_table()
    print(f"创建表结果: {result}")
    
    # 添加测试用户
    print("\n2. 添加测试用户")
    users = [
        ("张三", "zhangsan@example.com", 25, "active"),
        ("李四", "lisi@example.com", 30, "active"),
        ("王五", "wangwu@example.com", 28, "inactive"),
        ("赵六", "zhaoliu@example.com", 35, "active")
    ]
    
    for name, email, age, status in users:
        result = user_tool.add_user(name, email, age, status)
        print(f"添加用户 {name}: {result}")
    
    # 根据名称和邮件查询用户
    print("\n3. 根据名称和邮件查询用户")
    result = user_tool.get_user_by_name_and_email("张三", "zhangsan@example.com")
    print(f"查询结果: {result}")
    
    # 根据名称查询用户
    print("\n4. 根据名称查询用户")
    result = user_tool.get_user_by_name("李四")
    print(f"查询结果: {result}")
    
    # 根据邮件查询用户
    print("\n5. 根据邮件查询用户")
    result = user_tool.get_user_by_email("wangwu@example.com")
    print(f"查询结果: {result}")
    
    # 模糊查询用户
    print("\n6. 模糊查询用户（名称包含'三'）")
    result = user_tool.search_users_by_name("%三%")
    print(f"查询结果: {result}")
    
    # 获取所有用户
    print("\n7. 获取所有用户")
    result = user_tool.get_all_users(limit=10)
    print(f"查询结果: {result}")
    
    # 根据状态查询用户
    print("\n8. 查询活跃用户")
    result = user_tool.get_users_by_status("active")
    print(f"查询结果: {result}")
    
    # 获取用户总数
    print("\n9. 获取用户总数")
    result = user_tool.get_user_count()
    print(f"查询结果: {result}")
    
    # 更新用户信息
    print("\n10. 更新用户信息")
    result = user_tool.update_user(1, name="张三丰", age=26)
    print(f"更新结果: {result}")
    
    # 验证更新
    print("\n11. 验证更新结果")
    result = user_tool.get_user_by_name_and_email("张三丰", "zhangsan@example.com")
    print(f"查询结果: {result}")


if __name__ == "__main__":
    test_user_tool()
