#!/usr/bin/env python3
"""
带环境变量配置的启动脚本
"""

import os
from pathlib import Path

# 加载环境变量
def load_env_file(env_file: str = "config.env"):
    """加载环境变量文件"""
    env_path = Path(__file__).parent / env_file
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ 已加载环境变量文件: {env_file}")
    else:
        print(f"⚠️ 环境变量文件不存在: {env_file}")

# 加载环境变量
load_env_file()

# 导入并启动主应用
if __name__ == "__main__":
    import uvicorn
    from main import app
    
    print("🚀 启动Lupin Studio Backend服务...")
    print(f"📊 日志级别: {os.getenv('LOG_LEVEL', 'INFO')}")
    print(f"🔍 SQL调试: {os.getenv('ENABLE_SQL_DEBUG', 'false')}")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="debug" if os.getenv('LOG_LEVEL', 'INFO').upper() == 'DEBUG' else "info"
    )
