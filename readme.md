# Tool Set

A Python project for managing and executing various tools and utilities.

## Project Structure

```
tool_set/
├── README.md
├── requirements.txt
├── main.py
├── config.py
├── db/
│   ├── __init__.py
│   └── db_exe.py
├── examples/
│   ├── __init__.py
│   ├── linux_funs.py
│   └── user_funs.py
├── utils/
│   └── __init__.py
└── api/
    ├── __init__.py
    └── routes.py
```

## Installation

### 方法1：使用虚拟环境（推荐）

1. 创建并激活虚拟环境：
```bash
# 自动创建虚拟环境并安装依赖
./activate_venv.sh

# 或者手动创建
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行服务器：
```bash
# 使用虚拟环境运行
python run_with_venv.py

# 或者手动激活虚拟环境后运行
source .venv/bin/activate
python run_server.py
```

### 方法2：直接安装（不推荐）

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行服务器：
```bash
python main.py
```

## Features

- Dynamic tool execution
- Database operations
- Linux command execution
- User management tools
- RESTful API endpoints

## API Documentation

The API will be available at `http://localhost:8000/docs` when the server is running.
