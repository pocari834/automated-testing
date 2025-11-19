# 自动化测试平台

基于 Python FastAPI 的测试平台后端服务，支持 API 测试、Web UI 测试和性能测试。

## 技术栈

- **后端框架**: FastAPI
- **数据库**: SQL Server + SQLAlchemy
- **消息队列**: Redis + Celery
- **测试工具**: Pytest + Requests + Playwright + JMeter

## 项目结构

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 主应用
│   ├── config.py            # 配置管理
│   ├── database.py          # 数据库连接
│   ├── models.py            # SQLAlchemy 模型
│   ├── schemas.py           # Pydantic 模型
│   ├── celery_app.py        # Celery 应用
│   ├── tasks.py             # Celery 任务
│   ├── routers/             # API 路由
│   │   ├── projects.py
│   │   ├── api_tests.py
│   │   ├── ui_tests.py
│   │   ├── performance_tests.py
│   │   ├── reports.py
│   │   └── tasks.py
│   └── services/            # 业务逻辑
│       ├── api_test_service.py
│       ├── ui_test_service.py
│       └── performance_test_service.py
├── config.py
├── requirements.txt
├── run.py                   # 启动脚本
├── celery_worker.py        # Celery Worker 启动脚本
└── README.md
```

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
# 数据库配置
DATABASE_URL=mssql+pymssql://sa:123456@localhost:1433/test_platform

# Redis 配置
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 文件存储
UPLOAD_DIR=./uploads
JMETER_RESULTS_DIR=./jmeter_results
```

### 3. 初始化数据库

```bash
# 创建数据库（使用 SQL Server Management Studio 或 sqlcmd）
# 在 SQL Server Management Studio 中执行：
CREATE DATABASE test_platform;
# 或使用 sqlcmd：
# sqlcmd -S localhost -U sa -P 123456 -Q "CREATE DATABASE test_platform"

# 数据库表会在首次启动时自动创建
```

### 4. 启动服务

#### 启动 FastAPI 服务

```bash
python run.py
# 或
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 启动 Celery Worker

```bash
celery -A app.celery_app worker --loglevel=info
# 或
python celery_worker.py
```

## API 文档

启动服务后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心功能模块

### 1. 项目管理

- `POST /projects` - 创建项目
- `GET /projects` - 获取项目列表（支持分页和名称搜索）
- `GET /projects/{project_id}` - 获取项目详情
- `PUT /projects/{project_id}` - 更新项目
- `DELETE /projects/{project_id}` - 删除项目（软删除）

### 2. API 测试管理

#### 测试用例 CRUD

- `POST /api_tests/cases` - 创建 API 测试用例
- `GET /api_tests/cases` - 获取用例列表
- `GET /api_tests/cases/{case_id}` - 获取用例详情
- `PUT /api_tests/cases/{case_id}` - 更新用例
- `DELETE /api_tests/cases/{case_id}` - 删除用例

#### 测试套件 CRUD

- `POST /api_tests/suites` - 创建测试套件
- `GET /api_tests/suites` - 获取套件列表
- `GET /api_tests/suites/{suite_id}` - 获取套件详情
- `PUT /api_tests/suites/{suite_id}` - 更新套件
- `DELETE /api_tests/suites/{suite_id}` - 删除套件

#### 执行测试

- `POST /api_tests/run/{case_id}` - 执行单个用例（异步）
- `POST /api_tests/run_suite/{suite_id}` - 执行测试套件（异步）

### 3. Web UI 测试管理

- `POST /ui_tests/cases` - 创建 UI 测试用例
- `GET /ui_tests/cases` - 获取用例列表
- `GET /ui_tests/cases/{case_id}` - 获取用例详情
- `PUT /ui_tests/cases/{case_id}` - 更新用例
- `DELETE /ui_tests/cases/{case_id}` - 删除用例
- `POST /ui_tests/run/{case_id}` - 执行 UI 用例（异步）

### 4. 性能测试管理

- `POST /performance_tests` - 创建性能测试
- `GET /performance_tests` - 获取测试列表
- `GET /performance_tests/{test_id}` - 获取测试详情
- `PUT /performance_tests/{test_id}` - 更新测试
- `DELETE /performance_tests/{test_id}` - 删除测试
- `POST /performance_tests/upload/{test_id}` - 上传 JMX 文件
- `POST /performance_tests/run/{test_id}` - 执行性能测试（异步）

### 5. 测试报告

- `GET /reports` - 获取报告列表
- `GET /reports/{report_id}` - 获取详细报告

### 6. 任务查询

- `GET /tasks/{task_id}` - 查询异步任务状态和结果

## 使用示例

### 创建项目

```bash
curl -X POST "http://localhost:8000/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的测试项目",
    "description": "项目描述"
  }'
```

### 创建 API 测试用例

```bash
curl -X POST "http://localhost:8000/api_tests/cases" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "name": "测试登录接口",
    "method": "POST",
    "url": "https://api.example.com/login",
    "headers": {"Content-Type": "application/json"},
    "body": {"username": "test", "password": "123456"},
    "assertions": {
      "status_code": 200,
      "response_json": {
        "code": 0
      }
    }
  }'
```

### 执行 API 测试

```bash
# 提交任务
curl -X POST "http://localhost:8000/api_tests/run/1"

# 返回: {"task_id": "xxx-xxx-xxx", "status": "PENDING"}

# 查询任务状态
curl "http://localhost:8000/tasks/xxx-xxx-xxx"
```

## Docker 配置（UI 测试）

UI 测试需要在 Docker 容器中运行。创建 `Dockerfile.playwright`:

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0

WORKDIR /app

RUN pip install pytest playwright

# 安装浏览器
RUN playwright install chromium
RUN playwright install-deps chromium

CMD ["pytest"]
```

构建镜像：

```bash
docker build -f Dockerfile.playwright -t playwright-test:latest .
```

设置环境变量启用 Docker 执行：

```bash
export USE_DOCKER_FOR_UI_TESTS=true
export PLAYWRIGHT_DOCKER_IMAGE=playwright-test:latest
```

## JMeter 配置

确保系统已安装 JMeter，并设置环境变量：

```bash
export JMETER_HOME=/path/to/jmeter
```

或在配置文件中指定 JMeter 路径。

## 注意事项

1. **数据库连接**: 确保 SQL Server 服务已启动，数据库已创建
2. **Redis 服务**: Celery 需要 Redis 作为消息队列，确保 Redis 已启动
3. **文件权限**: 确保 `uploads` 和 `jmeter_results` 目录有写入权限
4. **UI 测试**: 本地执行需要安装 Playwright 和浏览器，或使用 Docker 容器
5. **性能测试**: 需要安装 JMeter 并配置环境变量

## 开发建议

1. 使用虚拟环境管理依赖
2. 生产环境应配置具体的 CORS 域名
3. 添加认证和授权机制
4. 配置日志系统
5. 添加单元测试和集成测试
6. 使用环境变量管理敏感配置

## 许可证

MIT License

