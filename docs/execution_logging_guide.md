# 执行日志记录系统使用指南

## 概述

执行日志记录系统提供了统一的日志记录功能，支持多种存储方式：MySQL、SQLite、文件。系统会自动记录 SQL 执行和命令执行的详细信息，包括执行时间、结果、错误等。

## 功能特性

### 1. 多种存储方式
- **MySQL**: 适合生产环境，支持高并发
- **SQLite**: 适合开发和小型应用
- **文件**: 适合日志分析和审计

### 2. 自动日志记录
- SQL 查询自动记录
- 命令执行自动记录
- 装饰器支持

### 3. 丰富的查询功能
- 按用户查询
- 按时间范围查询
- 统计信息
- 慢查询分析

## 配置

### 环境变量配置

#### SQLite 配置（默认）
```bash
export LOG_TYPE=sqlite
export SQLITE_FILE_PATH=./execution_logs.db
```

#### MySQL 配置
```bash
export LOG_TYPE=mysql
export DB_IP=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASSWORD=your_password
export DB_NAME=execution_logs
```

#### 文件配置
```bash
export LOG_TYPE=file
export LOG_FILE_DIR=./logs
```

### 配置文件示例

复制 `config_example.env` 为 `.env` 并修改相应配置：

```bash
cp config_example.env .env
```

## 使用方法

### 1. 基本使用

#### 直接写入日志
```python
from utils.db.exe_log import write_execution_log
from datetime import datetime

# 写入执行日志
success = write_execution_log(
    user="john_doe",
    command="SELECT * FROM users WHERE age > 25",
    result={"data": [{"id": 1, "name": "John"}]},
    execution_time=datetime.now(),
    time_cost_ms=150
)
```

#### 查询日志
```python
from utils.db.exe_log import query_execution_logs
from datetime import datetime, timedelta

# 查询用户日志
user_logs = query_execution_logs(user="john_doe", limit=50)

# 查询时间范围日志
start_time = datetime.now() - timedelta(hours=24)
recent_logs = query_execution_logs(start_time=start_time, limit=100)
```

### 2. 自动日志记录（已集成）

现在所有通过 `sql_db.py` 执行的 SQL 语句都会自动记录日志，无需手动添加装饰器：

```python
from utils.db.sql_db import execute, executemany
from utils.db.exe_log import ExecutionLogger

# 设置当前用户
ExecutionLogger.set_current_user("api_user")

# 执行 SQL，自动记录日志
result = execute("SELECT * FROM users WHERE id = ?", params=(1,))

# 批量执行，自动记录日志
batch_data = [("user1", "email1"), ("user2", "email2")]
result = executemany("INSERT INTO users (name, email) VALUES (?, ?)", batch_data)
```

### 3. 自动记录（已集成）

`sql_query` 函数已经集成了自动日志记录：

```python
from functions.db.db_funs import sql_query

# 执行 SQL 查询，自动记录日志
result = sql_query("SELECT * FROM users", "test_db")
```

## 日志管理工具

### 1. 基本查询功能

```python
from functions.examples.log_manager import *

# 按用户查询日志
user_logs = get_logs_by_user("john_doe", limit=50)

# 查询最近24小时的日志
recent_logs = get_recent_logs(hours=24, limit=100)

# 查询时间范围日志
start_time = datetime.now() - timedelta(days=7)
end_time = datetime.now()
range_logs = get_logs_by_time_range(start_time, end_time, limit=200)
```

### 2. 统计功能

```python
# 获取日志统计信息
stats = get_log_statistics(hours=24)
print(f"总日志数: {stats['total_logs']}")
print(f"唯一用户数: {stats['unique_users']}")
print(f"平均执行时间: {stats['avg_execution_time']}ms")
print(f"错误率: {stats['error_rate']}%")

# 获取慢查询
slow_queries = get_slow_queries(threshold_ms=1000, limit=20)
for query in slow_queries:
    print(f"慢查询: {query['command']} - {query['time_cost_ms']}ms")

# 获取用户活动摘要
user_activity = get_user_activity_summary("john_doe", days=7)
print(f"用户活动: {user_activity['total_commands']} 条命令")
print(f"最常用命令: {user_activity['most_used_commands']}")
```

### 3. 日志清理

```python
# 清理30天前的日志
cleanup_success = cleanup_old_logs(days=30)
if cleanup_success:
    print("日志清理完成")
```

## 数据库表结构

### MySQL 表结构
```sql
CREATE TABLE execution_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,
    command TEXT NOT NULL,
    result TEXT,
    execution_time DATETIME NOT NULL,
    time_cost_ms INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_time (user_name, execution_time),
    INDEX idx_execution_time (execution_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### SQLite 表结构
```sql
CREATE TABLE execution_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    command TEXT NOT NULL,
    result TEXT,
    execution_time TEXT NOT NULL,
    time_cost_ms INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_time ON execution_logs(user_name, execution_time);
CREATE INDEX idx_execution_time ON execution_logs(execution_time);
```

### 文件日志格式（JSONL）
```json
{"timestamp": "2025-09-22T13:58:53.975220", "user": "john_doe", "command": "SELECT * FROM users", "result": {"data": [{"id": 1}]}, "time_cost_ms": 150}
```

## 性能考虑

### 1. 索引优化
- 用户+时间复合索引
- 执行时间索引
- 根据查询模式调整索引

### 2. 日志轮转
- 定期清理旧日志
- 使用分区表（MySQL）
- 按日期分割文件

### 3. 异步记录
- 对于高频操作，考虑异步记录
- 批量写入优化

## 监控和告警

### 1. 慢查询监控
```python
# 定期检查慢查询
slow_queries = get_slow_queries(threshold_ms=5000, limit=10)
if slow_queries:
    # 发送告警
    send_alert(f"发现 {len(slow_queries)} 个慢查询")
```

### 2. 错误率监控
```python
# 检查错误率
stats = get_log_statistics(hours=1)
if stats['error_rate'] > 10:  # 错误率超过10%
    send_alert(f"错误率过高: {stats['error_rate']}%")
```

### 3. 用户活动监控
```python
# 监控异常用户活动
user_activity = get_user_activity_summary("suspicious_user", days=1)
if user_activity['total_commands'] > 1000:  # 命令数过多
    send_alert(f"用户 {user} 活动异常: {user_activity['total_commands']} 条命令")
```

## 最佳实践

### 1. 配置管理
- 使用环境变量管理配置
- 不同环境使用不同配置
- 敏感信息加密存储

### 2. 日志级别
- 生产环境记录所有执行
- 开发环境可选择性记录
- 测试环境记录关键操作

### 3. 存储选择
- 开发环境：SQLite
- 测试环境：SQLite 或文件
- 生产环境：MySQL

### 4. 定期维护
- 定期清理旧日志
- 监控存储空间
- 备份重要日志

## 故障排除

### 1. 连接问题
- 检查数据库连接配置
- 验证网络连通性
- 检查权限设置

### 2. 性能问题
- 检查索引使用情况
- 分析慢查询
- 考虑分库分表

### 3. 存储问题
- 监控磁盘空间
- 检查文件权限
- 定期清理日志

## 扩展功能

### 1. 自定义字段
可以扩展日志记录字段：
- 客户端IP
- 请求ID
- 业务模块
- 操作类型

### 2. 日志分析
- 集成 ELK Stack
- 使用 Grafana 可视化
- 自定义分析脚本

### 3. 告警集成
- 邮件告警
- 钉钉/企业微信通知
- 短信告警

这个执行日志记录系统为您的应用提供了完整的操作审计和性能监控能力，帮助您更好地了解系统运行状况和用户行为。
