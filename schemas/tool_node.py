from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any, Union
from datetime import datetime


class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str = Field(..., description="参数名称")
    type: Literal["string", "number", "boolean", "array", "object"] = Field(..., description="参数类型")
    description: str = Field(..., description="参数描述")
    required: bool = Field(default=True, description="是否必需")
    enum: Optional[List[Any]] = Field(default=None, description="枚举值列表")
    default: Optional[Any] = Field(default=None, description="默认值")
    min_value: Optional[Union[int, float]] = Field(default=None, description="最小值")
    max_value: Optional[Union[int, float]] = Field(default=None, description="最大值")
    pattern: Optional[str] = Field(default=None, description="正则表达式模式")


class ToolResponse(BaseModel):
    """工具返回值定义"""
    type: Literal["string", "number", "boolean", "array", "object"] = Field(..., description="返回值类型")
    description: str = Field(..., description="返回值描述")
    response_schema: Optional[Dict[str, Any]] = Field(default=None, description="返回值结构定义")
    success_field: Optional[str] = Field(default="success", description="成功标识字段名")
    result_field: Optional[str] = Field(default="result", description="结果字段名")
    message_field: Optional[str] = Field(default="message", description="消息字段名")


class ToolNode(BaseModel):
    id: str = Field(..., description="工具唯一标识")
    name: str = Field(..., description="工具名称")
    title: str = Field(..., description="工具显示标题")
    description: str = Field(..., description="工具功能描述")
    icon: str = Field(..., description="工具图标")
    type: Literal["folder", "module", "function"] = Field(..., description="节点类型")
    
    # LLM function call 相关字段
    parameters: Optional[List[ToolParameter]] = Field(default=None, description="工具参数列表")
    response: Optional[ToolResponse] = Field(default=None, description="工具返回值定义")
    
    # 工具执行相关字段
    function_name: Optional[str] = Field(default=None, description="对应的函数名称")
    category: Optional[str] = Field(default=None, description="工具分类")
    tags: Optional[List[str]] = Field(default=None, description="工具标签")
    
    # 新增字段
    module_path: Optional[str] = Field(default=None, description="工具在tools目录下的python模块路径")
    modified_at: Optional[datetime] = Field(default=None, description="修改时间")
    last_called_at: Optional[datetime] = Field(default=None, description="最近一次调用的时间")
    call_count: int = Field(default=0, description="调用的次数")
    
    # 递归结构
    parent: Optional[str] = Field(default=None, description="父节点ID，为空表示第一级节点")
    children: Optional[List[str]] = Field(default=None, description="子节点列表")


# Rebuild forward refs for recursive model
ToolNode.model_rebuild()
