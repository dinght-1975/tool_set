import os
# 禁用 ChromaDB 遥测
os.environ["ANONYMIZED_TELEMETRY"] = "false"
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"

# 禁用 OpenTelemetry 遥测
os.environ["OTEL_PYTHON_DISABLED"] = "true"
os.environ["OTEL_TRACES_EXPORTER"] = "none"
os.environ["OTEL_METRICS_EXPORTER"] = "none"
os.environ["OTEL_LOGS_EXPORTER"] = "none"

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Dict, Any
from api.routes import router as tool_router, DynamicRouteManager
import time
import logging
import traceback
from utils.exception_handler import print_exception_stack, handle_exception
from utils.logger_config import setup_logging

# 设置日志 - 从环境变量读取配置
logger = setup_logging()

app = FastAPI(title="Lupin Studio Backend", version="0.1.0")

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录所有请求的详细信息"""
    start_time = time.time()
    
    # 记录请求开始
    logger.info(f"🚀 请求开始: {request.method} {request.url}")
    logger.info(f"📋 请求头: {dict(request.headers)}")
    
    # 如果是 POST 请求，记录请求体
    if request.method == "POST":
        try:
            body = await request.body()
            if body:
                logger.info(f"📦 请求体: {body.decode()}")
        except Exception as e:
            print_exception_stack(e, "读取请求体", "WARNING")
            logger.warning(f"⚠️ 无法读取请求体: {e}")
    
    # 处理请求
    response = await call_next(request)
    
    # 记录响应
    process_time = time.time() - start_time
    logger.info(f"✅ 请求完成: {request.method} {request.url} - 状态码: {response.status_code} - 耗时: {process_time:.3f}s")
    
    return response

# 请求预处理中间件
@app.middleware("http")
async def preprocess_request(request: Request, call_next):
    """预处理请求，处理 null 值"""
    if request.method == "POST" and "application/json" in request.headers.get("content-type", ""):
        try:
            # 读取请求体
            body = await request.body()
            if body:
                import json
                data = json.loads(body)
                
                # 检查是否有 null 值
                has_null = False
                for key, value in data.items():
                    if value is None:
                        data[key] = ""  # 将 null 转换为空字符串
                        has_null = True
                
                if has_null:
                    logger.info(f"🔄 预处理请求: 将 null 值转换为空字符串")
                    logger.info(f"📦 原始请求体: {body.decode()}")
                    logger.info(f"📦 处理后请求体: {json.dumps(data)}")
                    
                    # 创建新的请求对象
                    from starlette.requests import Request as StarletteRequest
                    from starlette.datastructures import State
                    
                    # 重新构建请求体
                    new_body = json.dumps(data).encode()
                    
                    # 这里需要特殊处理，因为 FastAPI 的请求体已经被读取
                    # 我们将在下一个中间件中处理
                    
        except Exception as e:
            print_exception_stack(e, "请求预处理", "WARNING")
            logger.warning(f"⚠️ 请求预处理失败: {e}")
    
    # 继续处理请求
    response = await call_next(request)
    return response

# Pydantic 验证错误处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理 Pydantic 验证错误"""
    logger.error(f"❌ Pydantic 验证错误: {request.method} {request.url}")
    logger.error(f"📋 错误详情: {exc.errors()}")
    
    # 尝试记录请求体
    try:
        body = await request.body()
        if body:
            logger.error(f"📦 请求体: {body.decode()}")
    except Exception as e:
        print_exception_stack(e, "读取请求体", "WARNING")
        logger.warning(f"⚠️ 无法读取请求体: {e}")
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": "验证失败"
        }
    )

# HTTP 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理 HTTP 异常"""
    logger.error(f"❌ HTTP 异常: {request.method} {request.url} - 状态码: {exc.status_code}")
    logger.error(f"📋 异常详情: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含工具相关路由
app.include_router(tool_router)

# 创建动态路由管理器，使用共享的 ChromaDB 管理器
dynamic_route_manager = DynamicRouteManager(app)

@app.on_event("startup")
async def startup_event():
    """应用启动时注册动态路由"""
    print("🚀 正在注册动态路由...")
    dynamic_route_manager.register_dynamic_routes()
    print("✅ 动态路由注册完成")


@app.get("/")
def root():
    return {"ok": True, "service": "lupin-studio-backend"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "lupin-studio-backend"}


