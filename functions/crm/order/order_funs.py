#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRM Order Management Functions
订单管理相关功能函数
"""

from utils.output import show_info, show_error, show_warning
from utils.db.sql_db import execute
from typing import Dict, Any, Optional


def get_order_data(customer_order_id: str) -> Dict[str, Any]:
    """
    获取订单数据
    
    Args:
        customer_order_id (str): 客户订单ID
        
    Returns:
        Dict[str, Any]: 订单数据字典，包含以下字段：
            - bill_id: 账单ID
            - cust_id: 客户ID
            - user_id: 用户ID
            - create_date: 创建日期
            - done_date: 完成日期
            - business_id: 业务ID
            - tenant_id: 租户ID
            - region_id: 区域ID
            - status: 订单状态
            - remark: 备注
            - completed: 是否已完成
    """
    try:
        show_info(f"正在获取订单数据，订单ID: {customer_order_id}")
        
        # 初始化订单数据
        order_data = {
            'customer_order_id': customer_order_id,
            'bill_id': '',
            'cust_id': 0,
            'user_id': 0,
            'create_date': None,
            'done_date': None,
            'business_id': 0,
            'tenant_id': 0,
            'region_id': 0,
            'status': 0,
            'remark': '',
            'completed': False
        }
        
        # 首先尝试从ord数据库获取订单数据
        sql_query = "SELECT * FROM ord.ord_cust_21 WHERE customer_order_id = ?"
        result = execute(sql_query, 'ord', (customer_order_id,))
        
        if result and result.get('row_count', 0) > 0:
            # 从ord数据库获取到数据
            row = result['data'][0]
            order_data.update({
                'bill_id': row.get('BILL_ID', ''),
                'cust_id': row.get('CUST_ID', 0),
                'user_id': row.get('USER_ID', 0),
                'create_date': row.get('CREATE_DATE'),
                'done_date': row.get('DONE_DATE'),
                'business_id': row.get('BUSINESS_ID', 0),
                'status': row.get('ORDER_STATE', 0),
                'remark': row.get('REMARKS', '')
            })
            
            # 获取租户和区域信息
            if order_data['bill_id']:
                tenant_region = _get_tenant_region(order_data['bill_id'])
                if tenant_region:
                    order_data['tenant_id'] = tenant_region.get('tenant_id', 0)
                    order_data['region_id'] = tenant_region.get('region_id', 0)
            
            show_info(f"成功从ord数据库获取订单数据: {order_data['bill_id']}")
            
        else:
            # 从ord数据库未获取到数据，尝试从ods数据库获取
            order_data['completed'] = True
            sql_query = "SELECT * FROM crm_ord.ord_cust_f_21 WHERE customer_order_id = ?"
            result = execute(sql_query, 'ods', (customer_order_id,))
            
            if result and result.get('row_count', 0) > 0:
                # 从ods数据库获取到数据
                row = result['data'][0]
                order_data.update({
                    'bill_id': row.get('BILL_ID', ''),
                    'cust_id': row.get('CUST_ID', 0),
                    'user_id': row.get('USER_ID', 0),
                    'create_date': row.get('CREATE_DATE'),
                    'done_date': row.get('DONE_DATE'),
                    'business_id': row.get('BUSINESS_ID', 0),
                    'status': row.get('ORDER_STATE', 0),
                    'remark': row.get('REMARKS', '')
                })
                
                # 获取租户和区域信息
                if order_data['bill_id']:
                    tenant_region = _get_tenant_region(order_data['bill_id'])
                    if tenant_region:
                        order_data['tenant_id'] = tenant_region.get('tenant_id', 0)
                        order_data['region_id'] = tenant_region.get('region_id', 0)
                
                show_info(f"成功从ods数据库获取订单数据: {order_data['bill_id']}")
            else:
                show_warning(f"未找到订单数据，订单ID: {customer_order_id}")
                return order_data
        
        return order_data
        
    except Exception as e:
        show_error(f"获取订单数据时发生错误: {str(e)}")
        return {
            'customer_order_id': customer_order_id,
            'error': str(e),
            'completed': False
        }


def _get_tenant_region(bill_id: str) -> Optional[Dict[str, int]]:
    """
    获取租户和区域信息
    
    Args:
        bill_id (str): 账单ID
        
    Returns:
        Optional[Dict[str, int]]: 包含tenant_id和region_id的字典，如果获取失败返回None
    """
    try:
        # 这里需要根据实际的opcomm.getTenReg函数实现
        # 暂时返回默认值，实际实现需要调用相应的函数
        show_info(f"获取租户和区域信息，账单ID: {bill_id}")
        
        # TODO: 实现实际的租户和区域信息获取逻辑
        # 这里应该调用类似 opcomm.getTenReg(bill_id) 的函数
        return {
            'tenant_id': 0,
            'region_id': 0
        }
        
    except Exception as e:
        show_error(f"获取租户和区域信息时发生错误: {str(e)}")
        return None


def get_order_status(customer_order_id: str) -> Dict[str, Any]:
    """
    获取订单状态
    
    Args:
        customer_order_id (str): 客户订单ID
        
    Returns:
        Dict[str, Any]: 订单状态信息
    """
    try:
        show_info(f"正在获取订单状态，订单ID: {customer_order_id}")
        
        order_data = get_order_data(customer_order_id)
        
        if 'error' in order_data:
            return {
                'customer_order_id': customer_order_id,
                'status': 'error',
                'message': order_data['error']
            }
        
        return {
            'customer_order_id': customer_order_id,
            'status': order_data.get('status', 0),
            'completed': order_data.get('completed', False),
            'create_date': order_data.get('create_date'),
            'done_date': order_data.get('done_date'),
            'remark': order_data.get('remark', '')
        }
        
    except Exception as e:
        show_error(f"获取订单状态时发生错误: {str(e)}")
        return {
            'customer_order_id': customer_order_id,
            'status': 'error',
            'message': str(e)
        }


def check_order_exists(customer_order_id: str) -> bool:
    """
    检查订单是否存在
    
    Args:
        customer_order_id (str): 客户订单ID
        
    Returns:
        bool: 订单是否存在
    """
    try:
        show_info(f"正在检查订单是否存在，订单ID: {customer_order_id}")
        
        order_data = get_order_data(customer_order_id)
        
        if 'error' in order_data:
            return False
        
        # 如果订单有bill_id，说明订单存在
        return bool(order_data.get('bill_id'))
        
    except Exception as e:
        show_error(f"检查订单是否存在时发生错误: {str(e)}")
        return False
