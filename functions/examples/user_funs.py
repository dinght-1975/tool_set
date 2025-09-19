#!/usr/bin/env python3
"""
用户工具模块
提供用户相关的数据库操作功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_exe import execute, executemany, rollback, commit
from typing import Dict, Any, Optional, List


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
            执行结果字典
        """
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
        
        result = execute(sql, self.db_name, db_type=self.db_type)
        
        if result['success']:
            # 创建索引以提高查询性能
            index_sql = "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)"
            execute(index_sql, self.db_name, db_type=self.db_type)
            
            index_sql2 = "CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)"
            execute(index_sql2, self.db_name, db_type=self.db_type)
        
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
            执行结果字典
        """
        sql = "INSERT INTO users (name, email, age, status) VALUES (?, ?, ?, ?)"
        params = (name, email, age, status)
        
        return execute(sql, self.db_name, params, self.db_type)
    
    def get_user_by_name(self, name: str) -> Dict[str, Any]:
        """
        根据用户名称查询用户
        
        Args:
            name: 用户名称
            
        Returns:
            查询结果字典
        """
        sql = "SELECT * FROM users WHERE name = ?"
        params = (name,)
        
        return execute(sql, self.db_name, params, self.db_type)
    
    def get_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        根据用户邮件地址查询用户
        
        Args:
            email: 用户邮件地址
            
        Returns:
            查询结果字典
        """
        sql = "SELECT * FROM users WHERE email = ?"
        params = (email,)
        
        return execute(sql, self.db_name, params, self.db_type)
    
    def get_user_by_name_and_email(self, name: str, email: str) -> Dict[str, Any]:
        """
        根据用户名称和邮件地址查询用户
        
        Args:
            name: 用户名称
            email: 用户邮件地址
            
        Returns:
            查询结果字典
        """
        sql = "SELECT * FROM users WHERE name = ? AND email = ?"
        params = (name, email)
        
        return execute(sql, self.db_name, params, self.db_type)
    
    def search_users_by_name(self, name_pattern: str) -> Dict[str, Any]:
        """
        根据用户名称模糊查询用户
        
        Args:
            name_pattern: 用户名称模式（支持 % 通配符）
            
        Returns:
            查询结果字典
        """
        sql = "SELECT * FROM users WHERE name LIKE ?"
        params = (name_pattern,)
        
        return execute(sql, self.db_name, params, self.db_type)
    
    def get_all_users(self, limit: Optional[int] = None, offset: int = 0) -> Dict[str, Any]:
        """
        获取所有用户
        
        Args:
            limit: 限制返回的记录数
            offset: 偏移量
            
        Returns:
            查询结果字典
        """
        if limit:
            sql = "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params = (limit, offset)
        else:
            sql = "SELECT * FROM users ORDER BY created_at DESC"
            params = None
        
        return execute(sql, self.db_name, params, self.db_type)
    
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
            执行结果字典
        """
        # 构建动态更新SQL
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        
        if age is not None:
            updates.append("age = ?")
            params.append(age)
        
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        
        if not updates:
            return {'success': False, 'type': 'error', 'error': '没有提供要更新的字段', 'message': '没有提供要更新的字段'}
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(user_id)
        
        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
        
        return execute(sql, self.db_name, params, self.db_type)
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            执行结果字典
        """
        sql = "DELETE FROM users WHERE id = ?"
        params = (user_id,)
        
        return execute(sql, self.db_name, params, self.db_type)
    
    def get_user_count(self) -> Dict[str, Any]:
        """
        获取用户总数
        
        Returns:
            查询结果字典
        """
        sql = "SELECT COUNT(*) as total FROM users"
        
        return execute(sql, self.db_name, db_type=self.db_type)
    
    def get_users_by_status(self, status: str) -> Dict[str, Any]:
        """
        根据状态查询用户
        
        Args:
            status: 用户状态
            
        Returns:
            查询结果字典
        """
        sql = "SELECT * FROM users WHERE status = ? ORDER BY created_at DESC"
        params = (status,)
        
        return execute(sql, self.db_name, params, self.db_type)


# 便捷函数
def get_user_by_name_and_email(name: str, email: str) -> Dict[str, Any]:
    """
    根据用户名称和邮件地址查询用户的便捷函数
    
    Args:
        name: 用户名称
        email: 用户邮件地址
        
    Returns:
        查询结果字典
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
        执行结果字典
    """
    user_tool = UserTool()
    return user_tool.add_user(name, email, age, status)


def search_users_by_name(name_pattern: str) -> Dict[str, Any]:
    """
    根据用户名称模糊查询用户的便捷函数
    
    Args:
        name_pattern: 用户名称模式（支持 % 通配符）
        
    Returns:
        查询结果字典
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
