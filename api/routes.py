#!/usr/bin/env python3
"""
工具相关 API 路由
整合所有工具相关的 API 端点定义
"""

import asyncio
import importlib
import inspect
from functools import wraps
from fastapi import APIRouter, HTTPException, Query, Path as FastAPIPath, Body, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional, Callable, Union
from pydantic import BaseModel, create_model, validator, Field
import sys
from pathlib import Path
from utils.exception_handler import print_exception_stack, safe_execute
from utils.output import show_error, get_result, clear_result

# 添加项目根目录到 Python 路径（如果还没有添加）
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from schemas.tool_node import ToolNode, ToolParameter, ToolResponse
from services.tool_service import ToolService


# 创建路由器
router = APIRouter(prefix="/apis", tags=["apis"])

# ==================== 系统状态 API ====================

@router.get("/health/status", summary="获取系统健康状态")
async def get_system_health() -> Dict[str, Any]:
    """获取系统健康状态"""
    try:
        
        
        return {
            "status": "healthy" ,
            "services": {
                "chromadb": "connected" ,
                "recently_used": "connected"
            },
            "timestamp": "2025-08-30T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-08-30T00:00:00Z"
        }


# ==================== 动态路由管理器 ====================

class DynamicRouteManager:
    """动态路由管理器"""
    
    def __init__(self, router: APIRouter):
        self.router = router
        self.registered_routes: Dict[str, Any] = {}
        self.dynamic_models: Dict[str, Any] = {}
        self.tool_service = ToolService()

    
    def create_dynamic_model(self, tool_node: ToolNode, is_request: bool = True) -> type:
        """根据 ToolNode 的参数定义创建动态的 Pydantic 模型"""
        model_name = f"{tool_node.name}_{'Request' if is_request else 'Response'}"
        
        if model_name in self.dynamic_models:
            return self.dynamic_models[model_name]
        
        if is_request and tool_node.parameters:
            # 创建请求模型
            fields = {}
            for param in tool_node.parameters:
                # 使用智能类型推断
                param_type = self._infer_parameter_type(param.name, param.type, param.description)
                
                # 处理用户界面未填写参数的情况（null 值）
                if param.required:
                    # 必需参数：允许 null，但提供默认值
                    if param_type == str:
                        # 字符串类型：null 转换为空字符串
                        fields[param.name] = (Union[str, None], Field(default="", description=param.description))
                    elif param_type == bool:
                        # 布尔类型：null 转换为 False
                        fields[param.name] = (Union[bool, None], Field(default=False, description=param.description))
                    elif param_type == int:
                        # 整数类型：null 转换为 0
                        fields[param.name] = (Union[int, None], Field(default=0, description=param.description))
                    else:
                        # 其他类型：允许 null，使用 None 作为默认值
                        fields[param.name] = (Union[param_type, None], Field(default=None, description=param.description))
                else:
                    # 可选参数：允许 null，转换为 None
                    optional_type = Union[param_type, None]
                    default_value = param.default if param.default is not None else None
                    fields[param.name] = (optional_type, Field(default=default_value, description=param.description))
            
            # 创建模型
            model = create_model(model_name, **fields)
            
            # 添加验证器来处理 null 值转换
            @validator('*', pre=True)
            def convert_null_to_defaults(cls, v, field):
                """将 null 值转换为合适的默认值"""
                if v is None:
                    # 根据字段类型提供默认值
                    if field.type_ == str or (hasattr(field.type_, '__origin__') and str in field.type_.__args__):
                        return ""  # 字符串类型：null → 空字符串
                    elif field.type_ == bool or (hasattr(field.type_, '__origin__') and bool in field.type_.__args__):
                        return False  # 布尔类型：null → False
                    elif field.type_ == int or (hasattr(field.type_, '__origin__') and int in field.type_.__args__):
                        return 0  # 整数类型：null → 0
                    else:
                        return None  # 其他类型：保持 None
                return v
            
            # 将验证器添加到模型
            model.__validators__ = getattr(model, '__validators__', {})
            model.__validators__['convert_null_to_defaults'] = convert_null_to_defaults
            
        else:
            # 创建响应模型
            if tool_node.response and tool_node.response.response_schema:
                # 如果有响应模式，使用它
                model = create_model(model_name, result=(Any, ...))
            else:
                # 默认响应模型
                model = create_model(model_name, 
                                   success=(bool, True),
                                   result=(Any, ...),
                                   message=(str, ""))
        
        self.dynamic_models[model_name] = model
        return model
    
    def _get_python_type(self, type_str: str) -> type:
        """将字符串类型转换为 Python 类型"""
        type_mapping = {
            "string": str,
            "number": (int, float),
            "boolean": bool,
            "array": List,
            "object": Dict[str, Any]
        }
        return type_mapping.get(type_str, Any)
    
    def _infer_parameter_type(self, param_name: str, param_type: str, param_description: str) -> type:
        """智能推断参数类型"""
        # 首先尝试从类型字符串推断
        if param_type in ["boolean", "bool"]:
            return bool
        elif param_type in ["number", "int", "float"]:
            return Union[int, float]
        elif param_type in ["array", "list"]:
            return List
        elif param_type in ["object", "dict"]:
            return Dict[str, Any]
        elif param_type in ["string", "str"]:
           return str
        else:
            return Any
    
    def create_dynamic_endpoint(self, tool_node: ToolNode) -> Callable:
        """为工具节点创建动态的 API 端点"""
        
        # 创建请求和响应模型
        request_model = self.create_dynamic_model(tool_node, is_request=True)
        response_model = self.create_dynamic_model(tool_node, is_request=False)
        
        # 生成端点函数
        async def dynamic_endpoint(request: request_model = Body(...)) -> JSONResponse:
            # 清除之前的线程变量结果
            clear_result()
            
            # 清除执行日志线程变量
            from utils.exe_log import ExecutionLogger
            ExecutionLogger.clear_thread_logs()
            
            try:
                # 记录工具使用
                await self._record_tool_usage(tool_node)
                
                # 执行工具函数
                await self._execute_tool_function(tool_node, request)
                
                # 获取线程变量中的结果
                result = get_result()
                
                # 获取执行日志并添加到响应中
                execution_logs = ExecutionLogger.get_thread_logs()
                if execution_logs:
                    result["execution_logs"] = execution_logs
                
                # 返回线程变量中的结果
                return JSONResponse(content=result)
                    
            except Exception as e:
                # 捕获所有异常，调用 show_error
                show_error(str(e), f"执行工具 {tool_node.name} 时发生错误")
                print_exception_stack(e, "执行工具函数", "ERROR")
                
                # 获取线程变量中的结果（包含错误信息）
                result = get_result()
                
                # 获取执行日志并添加到响应中
                execution_logs = ExecutionLogger.get_thread_logs()
                if execution_logs:
                    result["execution_logs"] = execution_logs
                
                # 返回错误结果
                return JSONResponse(content=result, status_code=500)
        
        # 设置函数元数据
        dynamic_endpoint.__name__ = f"execute_{tool_node.name}"
        dynamic_endpoint.__doc__ = f"执行工具: {tool_node.name}\n\n{tool_node.description}"
        
        return dynamic_endpoint
    
    async def _record_tool_usage(self, tool_node: ToolNode):
        """记录工具使用情况"""
        try:
            # 这里可以调用服务来记录工具使用
            # 例如：recently_used_service.add_recently_used_tool(tool_node.id, tool_node.name)
            pass
        except Exception:
            # 记录失败不影响主要功能
            pass
    
    async def _execute_tool_function(self, tool_node: ToolNode, request: Any) -> None:
        """执行工具函数"""
        try:
            # 根据 module_path 和 function_name 动态导入和执行函数
            if not tool_node.module_path or not tool_node.function_name:
                raise ValueError("工具缺少模块路径或函数名称")
            
            # 解析模块路径
            module_path = tool_node.module_path.replace('/', '.').replace('.py', '')
            # 动态导入模块
            module = importlib.import_module(module_path)
            
            # 获取函数
            if hasattr(module, tool_node.function_name):
                func = getattr(module, tool_node.function_name)
                
                # 检查是否是异步函数
                if asyncio.iscoroutinefunction(func):
                    # 异步函数
                    if tool_node.parameters:
                        # 有参数的情况
                        kwargs = request.dict() if hasattr(request, 'dict') else request
                        await func(**kwargs)
                    else:
                        # 无参数的情况
                        await func()
                else:
                    # 同步函数
                    if tool_node.parameters:
                        # 有参数的情况
                        kwargs = request.dict() if hasattr(request, 'dict') else request
                        func(**kwargs)
                    else:
                        # 无参数的情况
                        func()
            else:
                raise ValueError(f"模块 {module_path} 中未找到函数 {tool_node.function_name}")
                
        except Exception as e:
            print_exception_stack(e, "执行工具函数", "ERROR")
            raise Exception(f"执行工具函数失败: {str(e)}")
    
    def register_dynamic_routes(self):
        """注册所有动态路由"""
        try:
            # 获取所有工具
            tools = self.tool_service.get_all_tools()
            
            for tool in tools:
                if tool.type == "function" and tool.function_name:
                    # 为工具类型的节点创建动态路由
                    endpoint_func = self.create_dynamic_endpoint(tool)
                    
                    # 创建路由路径：使用 module_path + function_name
                    if tool.module_path and tool.function_name:
                        # 清理模块路径，移除 .py 后缀和 pyservices 前缀
                        route_path = f"/{tool.module_path}/{tool.function_name}"
                    else:
                        # 回退到使用工具名称
                        route_path = f"/{tool.name}"
                    
                    print(f"🔍 调试: 正在注册路由 {route_path} 到路由器 {self.router}")
                    
                    # 注册路由
                    self.router.add_api_route(
                        path=route_path,
                        endpoint=endpoint_func,
                        methods=["POST"],
                        summary=f"执行工具: {tool.name}",
                        description=tool.description,
                        tags=["dynamic-tools"]
                    )
                    
                    print(f"🔍 调试: 路由注册完成，检查路由器状态")
                    
                    self.registered_routes[tool.id] = {
                        "path": route_path,
                        "tool": tool,
                        "endpoint": endpoint_func
                    }
                    
                    print(f"✅ 注册动态路由: {route_path} -> {tool.name}")
            
            print(f"🎯 成功注册 {len(self.registered_routes)} 个动态路由")
            
        except Exception as e:
            print_exception_stack(e, "注册动态路由", "ERROR")
            print(f"❌ 注册动态路由失败: {e}")
    
    def get_registered_routes(self) -> Dict[str, Any]:
        """获取已注册的动态路由信息"""
        return {
            tool_id: {
                "path": info["path"],
                "tool_name": info["tool"].name,
                "description": info["tool"].description,
                "parameters": info["tool"].parameters,
                "response": info["tool"].response
            }
            for tool_id, info in self.registered_routes.items()
        }




