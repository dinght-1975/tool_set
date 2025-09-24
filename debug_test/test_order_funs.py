#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 order_funs.py 中的函数功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from functions.crm.order.order_funs import get_order_data, get_order_status, check_order_exists


def test_order_functions():
    """测试订单相关函数"""
    print("=== 测试订单管理函数 ===")
    
    # 测试用的订单ID
    test_order_id = "TEST123456"
    
    print(f"\n1. 测试 get_order_data 函数")
    print(f"订单ID: {test_order_id}")
    try:
        result = get_order_data(test_order_id)
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {e}")
    
    print(f"\n2. 测试 get_order_status 函数")
    print(f"订单ID: {test_order_id}")
    try:
        result = get_order_status(test_order_id)
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {e}")
    
    print(f"\n3. 测试 check_order_exists 函数")
    print(f"订单ID: {test_order_id}")
    try:
        result = check_order_exists(test_order_id)
        print(f"结果: {result}")
    except Exception as e:
        print(f"错误: {e}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_order_functions()
