# 统一输出处理机制

## 概述

本项目实现了统一的输出处理机制，所有业务函数不再直接返回 HTTP 响应，而是通过线程变量来管理输出信息，并在请求处理完成时统一返回结果。

## 核心组件

### 1. utils/output.py 模块

提供以下核心功能：

- **`write_output(title, type, content)`**: 核心函数，将输出添加到线程变量
- **`show_info(content, title=None)`**: 快捷方法，添加信息输出
- **`show_error(content, title=None)`**: 快捷方法，添加错误输出
- **`show_warning(content, title=None)`**: 快捷方法，添加警告输出
- **`get_result()`**: 获取当前线程的 result 对象
- **`clear_result()`**: 清除当前线程的 result 对象

### 2. 线程变量管理

使用 `threading.local()` 确保每个请求线程都有独立的 result 对象：

```python
{
    "status": True/False,  # 整体状态
    "output": [            # 输出消息数组
        {"Title": "标题", "Content": "内容"}
    ],
    "error": ""            # 错误信息（如果有）
}
```

## 使用方式

### 在业务函数中使用

```python
from utils.output import show_info, show_error, show_warning

def my_business_function(param1: str, param2: int):
    """业务函数示例"""
    show_info("Function started", "Startup")
    
    try:
        # 业务逻辑
        result = process_data(param1, param2)
        show_info(f"Processed {len(result)} items", "Processing")
        
    except Exception as e:
        show_error(f"Processing failed: {str(e)}", "Error")
        return  # 提前返回
    
    show_info("Function completed successfully", "Success")
```

### 统一异常处理

在 `api/routes.py` 中的 `dynamic_endpoint` 函数实现了统一的异常处理：

```python
async def dynamic_endpoint(request: request_model = Body(...)) -> JSONResponse:
    # 清除之前的线程变量结果
    clear_result()
    
    try:
        # 执行工具函数
        await self._execute_tool_function(tool_node, request)
        
        # 获取线程变量中的结果
        result = get_result()
        return JSONResponse(content=result)
        
    except Exception as e:
        # 捕获所有异常，调用 show_error
        show_error(str(e), f"执行工具 {tool_node.name} 时发生错误")
        
        # 获取线程变量中的结果（包含错误信息）
        result = get_result()
        return JSONResponse(content=result, status_code=500)
```

## 优势

1. **统一性**: 所有业务函数使用相同的输出机制
2. **累积性**: 多个输出消息可以累积在同一个响应中
3. **异常安全**: 自动捕获所有异常并转换为错误输出
4. **线程安全**: 每个请求线程独立管理输出
5. **灵活性**: 支持多种输出类型（info, warning, error）

## 响应格式

所有 API 响应都遵循统一格式：

```json
{
    "status": true,  // 整体执行状态
    "output": [      // 输出消息数组
        {
            "Title": "消息标题",
            "Content": "消息内容"
        }
    ],
    "error": ""      // 错误信息（如果有错误）
}
```

## 示例

### 成功执行示例

```json
{
    "status": true,
    "output": [
        {"Title": "Startup", "Content": "Process started successfully"},
        {"Title": "Processing", "Content": "Data processing completed"},
        {"Title": "Success", "Content": "Operation completed successfully"}
    ],
    "error": ""
}
```

### 错误执行示例

```json
{
    "status": false,
    "output": [
        {"Title": "Startup", "Content": "Process started"},
        {"Title": "Error", "Content": "Division by zero error"}
    ],
    "error": "Division by zero error"
}
```

## 测试

运行测试脚本验证功能：

```bash
python3 debug_test/test_output_integration.py
```

## 注意事项

1. 业务函数不应该直接返回 HTTP 响应
2. 使用 `show_*` 方法来输出信息
3. 异常会被自动捕获并转换为错误输出
4. 每个请求开始时会自动清除之前的线程变量
