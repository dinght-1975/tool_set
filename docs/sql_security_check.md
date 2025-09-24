# SQL 安全检查功能

## 概述

为 `sql_query` 函数添加了安全检查功能，确保只能执行查询语句，防止恶意或意外的数据修改操作。

## 安全策略

### 允许的语句类型
- **SELECT**: 数据查询语句
- **WITH**: 公共表表达式 (CTE)
- **EXPLAIN**: 查询计划分析
- **PRAGMA**: SQLite 特定的元数据查询

### 禁止的语句类型
- **INSERT**: 插入数据
- **UPDATE**: 更新数据
- **DELETE**: 删除数据
- **DROP**: 删除表/索引等对象
- **CREATE**: 创建表/索引等对象
- **ALTER**: 修改表结构
- **TRUNCATE**: 清空表
- **GRANT/REVOKE**: 权限管理
- **COMMIT/ROLLBACK**: 事务控制
- **SAVEPOINT/RELEASE**: 保存点操作
- **EXEC/EXECUTE/CALL**: 存储过程执行
- **DECLARE/SET**: 变量声明和赋值
- **BEGIN/END**: 事务块

## 实现细节

### 1. SQL 预处理
```python
def _is_query_only(sql: str) -> bool:
    # 移除注释和多余空白
    # 先处理多行注释
    sql_clean = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    # 再处理单行注释
    sql_clean = re.sub(r'--.*$', '', sql_clean, flags=re.MULTILINE)
    # 最后处理多余空白
    sql_clean = re.sub(r'\s+', ' ', sql_clean.strip())
```

### 2. 安全检查逻辑
1. **白名单检查**: 检查 SQL 是否以允许的语句开头
2. **黑名单检查**: 检查 SQL 是否包含禁止的关键词
3. **大小写不敏感**: 支持各种大小写组合

### 3. 错误处理
- 安全检查失败时立即返回错误
- 提供清晰的错误信息
- 通过 `show_error` 记录安全违规

## 使用示例

### 允许的查询
```python
# 基本查询
sql_query("SELECT * FROM users WHERE age > ?", "test_db", (25,))

# 带注释的查询
sql_query("-- 查询活跃用户\nSELECT * FROM users WHERE status = 'active'")

# 多行注释查询
sql_query("/* 复杂查询 */\nSELECT u.name, u.email FROM users u WHERE u.age > 18")

# CTE 查询
sql_query("WITH active_users AS (SELECT * FROM users WHERE status = 'active') SELECT * FROM active_users")

# 元数据查询
sql_query("PRAGMA table_info(users)")

# 查询计划
sql_query("EXPLAIN SELECT * FROM users WHERE id = ?", "test_db", (1,))
```

### 被拦截的修改语句
```python
# 这些语句会被安全检查拦截
sql_query("INSERT INTO users (name) VALUES ('test')")  # 被拦截
sql_query("UPDATE users SET name = 'new' WHERE id = 1")  # 被拦截
sql_query("DELETE FROM users WHERE id = 1")  # 被拦截
sql_query("DROP TABLE users")  # 被拦截
sql_query("CREATE TABLE test (id INT)")  # 被拦截
```

## 安全特性

### 1. 注释处理
- 支持单行注释 (`--`)
- 支持多行注释 (`/* */`)
- 注释不会影响安全检查

### 2. 大小写不敏感
- 支持各种大小写组合
- `SELECT`, `select`, `Select` 都被识别为查询语句

### 3. 关键词检测
- 使用正则表达式进行精确匹配
- 避免误判（如 `SELECT` 不会匹配 `SELECTED`）

### 4. 错误信息
- 提供清晰的错误说明
- 通过输出系统记录安全违规

## 测试验证

创建了完整的测试套件验证功能：

1. **允许查询测试**: 验证各种查询语句通过安全检查
2. **禁止语句测试**: 验证修改语句被正确拦截
3. **边界情况测试**: 验证空字符串、注释等特殊情况
4. **错误处理测试**: 验证错误信息正确显示

## 配置说明

### 允许的语句类型
可以通过修改 `allowed_starts` 列表来调整允许的语句类型：

```python
allowed_starts = ['select', 'with', 'explain', 'pragma']
```

### 禁止的关键词
可以通过修改 `forbidden_keywords` 列表来调整禁止的关键词：

```python
forbidden_keywords = [
    'insert', 'update', 'delete', 'drop', 'create', 'alter', 'truncate',
    'grant', 'revoke', 'commit', 'rollback', 'savepoint', 'release',
    'exec', 'execute', 'call', 'declare', 'set', 'begin', 'end'
]
```

## 注意事项

1. **SQLite 兼容性**: 移除了 SQLite 不支持的 `DESCRIBE`, `DESC`, `SHOW` 语句
2. **性能考虑**: 安全检查在 SQL 执行前进行，避免不必要的数据库操作
3. **安全性**: 这是第一道防线，不能替代其他安全措施
4. **可扩展性**: 可以根据需要调整安全策略

## 总结

SQL 安全检查功能为 `sql_query` 函数提供了强大的安全保护，确保只能执行查询操作，有效防止数据被意外或恶意修改。通过白名单和黑名单相结合的方式，既保证了功能的灵活性，又确保了系统的安全性。
