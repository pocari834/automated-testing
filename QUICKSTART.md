# 快速启动指南

## 前置要求

1. Python 3.8+
2. SQL Server 2016+
3. Redis 5.0+

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

创建 `.env` 文件（参考 `.env.example`）：

```env
DATABASE_URL=mssql+pymssql://sa:123456@localhost:1433/test_platform
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 3. 创建数据库

**使用 SQL Server Management Studio:**
```sql
CREATE DATABASE test_platform;
```

**或使用 sqlcmd:**
```bash
sqlcmd -S localhost -U sa -P 123456 -Q "CREATE DATABASE test_platform"
```

**或使用 Python 脚本:**
```bash
python init_db.py
```

### 4. 启动服务

#### 终端 1: 启动 FastAPI

```bash
python run.py
```

访问 http://localhost:8000/docs 查看 API 文档

#### 终端 2: 启动 Celery Worker

```bash
celery -A app.celery_app worker --loglevel=info
```

### 5. 测试 API

```bash
# 创建项目
curl -X POST "http://localhost:8000/projects" \
  -H "Content-Type: application/json" \
  -d '{"name": "测试项目", "description": "这是一个测试项目"}'

# 获取项目列表
curl "http://localhost:8000/projects"
```

## 功能测试流程

### API 测试

1. 创建项目
2. 创建 API 测试用例
3. 执行测试用例（返回 task_id）
4. 查询任务状态获取结果
5. 查看测试报告

### UI 测试

1. 创建 UI 测试用例（编写 Playwright 脚本）
2. 执行测试用例
3. 查看执行结果和截图

### 性能测试

1. 创建性能测试
2. 上传 JMX 文件
3. 执行性能测试
4. 查看性能指标和 HTML 报告

## 常见问题

### SQL Server 连接失败

- 检查 SQL Server 服务是否启动（Windows: 服务管理器，Linux: `systemctl status mssql-server`）
- 确认数据库用户（sa）和密码（123456）正确
- 确认数据库已创建
- 确认 SQL Server 允许 TCP/IP 连接（默认端口 1433）
- 检查防火墙设置

### Redis 连接失败

- 检查 Redis 服务是否启动
- 确认 Redis URL 配置正确

### Celery 任务不执行

- 确认 Celery Worker 已启动
- 检查 Redis 连接是否正常
- 查看 Celery Worker 日志

### UI 测试执行失败

- 本地执行需要安装 Playwright: `playwright install chromium`
- 或使用 Docker 容器执行（设置环境变量 `USE_DOCKER_FOR_UI_TESTS=true`）

### 性能测试执行失败

- 确认已安装 JMeter
- 设置环境变量 `JMETER_HOME` 指向 JMeter 安装目录
- 或确保 `jmeter` 命令在系统 PATH 中

