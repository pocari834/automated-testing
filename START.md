# 完整启动步骤指南

本文档提供测试平台（后端 + 前端）的完整启动步骤。

## 前置要求

### 必需软件

1. **Python 3.8+**
   ```bash
   python --version
   ```

2. **Node.js 16+**
   ```bash
   node --version
   npm --version
   ```

3. **SQL Server 2016+**
   ```bash
   # 检查 SQL Server 服务是否运行
   # Windows: 在服务管理器中查看 "SQL Server (MSSQLSERVER)"
   # 或使用 sqlcmd 测试连接
   ```

4. **Redis 5.0+**
   ```bash
   redis-cli --version
   ```

## 一、后端启动步骤

### 1. 安装 Python 依赖

**Windows 用户注意**：如果 `python` 命令不可用，请使用 `py` 命令。

如果使用虚拟环境（推荐）：

```bash
# 创建虚拟环境
# Windows:
py -m venv venv
# Linux/Mac:
python -m venv venv

# 激活虚拟环境
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

如果不使用虚拟环境（不推荐）：

```bash
# Windows:
py -m pip install -r requirements.txt
# Linux/Mac:
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件（在项目根目录）：

```env
# 数据库配置
DATABASE_URL=mssql+pymssql://sa:123456@localhost:1433/test_platform
DATABASE_ECHO=False

# Redis 配置
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# 文件存储
UPLOAD_DIR=./uploads
JMETER_RESULTS_DIR=./jmeter_results

# 应用配置
APP_NAME=Test Platform API
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
```

**重要**：请根据实际情况修改：
- `DATABASE_URL` 中的用户名、密码、数据库名
- 其他配置项按需调整

### 3. 创建数据库

**使用 SQL Server Management Studio (SSMS):**
1. 打开 SSMS，连接到 SQL Server 实例
2. 右键点击"数据库" -> "新建数据库"
3. 数据库名称：`test_platform`
4. 点击"确定"

**或使用 sqlcmd 命令行:**
```bash
# Windows
sqlcmd -S localhost -U sa -P 123456 -Q "CREATE DATABASE test_platform"

# Linux/Mac (如果安装了 sqlcmd)
sqlcmd -S localhost -U sa -P 123456 -Q "CREATE DATABASE test_platform"
```

**或使用 Python 脚本:**
```bash
python init_db.py
```

### 4. 启动 SQL Server 和 Redis 服务

**Windows:**
```bash
# SQL Server (通常作为服务自动启动)
# 检查服务状态：在服务管理器中查看 "SQL Server (MSSQLSERVER)" 或 "SQL Server (SQLEXPRESS)"
# 或使用命令：
sc query MSSQLSERVER

# Redis (如果安装了 Redis for Windows)
redis-server
```

**Linux/Mac:**
```bash
# SQL Server (如果使用 Docker)
docker start mssql-server
# 或使用 systemd (如果作为服务安装)
sudo systemctl start mssql-server

# Redis
sudo systemctl start redis
# 或
redis-server
```

### 5. 启动 FastAPI 服务

**方式一：使用启动脚本**
```bash
# Windows (如果 python 不可用，使用 py):
py run.py
# 或
python run.py

# Linux/Mac:
python run.py
```

**方式二：使用 uvicorn 命令**
```bash
# Windows:
py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Linux/Mac:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 6. 启动 Celery Worker（新终端窗口）

```bash
celery -A app.celery_app worker --loglevel=info
```

**Windows 用户注意**：如果遇到问题，可能需要安装额外依赖：
```bash
pip install eventlet
celery -A app.celery_app worker --loglevel=info --pool=eventlet
```

## 二、前端启动步骤

### 1. 安装 Node.js 依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

如果使用 yarn：
```bash
yarn install
```

### 2. 启动开发服务器

```bash
npm run dev
```

服务启动后，访问：http://localhost:3000

### 3. 构建生产版本（可选）

```bash
npm run build
```

构建产物在 `frontend/dist` 目录。

## 三、完整启动流程（快速参考）

### 终端 1：启动 SQL Server 和 Redis
```bash
# 确保 SQL Server 和 Redis 服务运行
# Windows: 在服务管理器中检查 SQL Server 服务状态
# Linux/Mac: sudo systemctl start mssql-server redis
```

### 终端 2：启动 FastAPI 后端
```bash
# 在项目根目录
# Windows (如果 python 不可用，使用 py):
py run.py
# Linux/Mac:
python run.py
```

### 终端 3：启动 Celery Worker
```bash
# 在项目根目录
celery -A app.celery_app worker --loglevel=info
```

### 终端 4：启动前端
```bash
# 进入前端目录
cd frontend
npm run dev
```

## 四、验证启动

### 1. 检查后端 API

```bash
# 访问 API 文档
curl http://localhost:8000/docs

# 或浏览器打开
http://localhost:8000/docs
```

### 2. 检查前端

浏览器打开：http://localhost:3000

应该能看到：
- 左侧导航栏（项目管理、API测试、UI测试、性能测试、测试报告）
- 顶部标题栏
- 主内容区域

### 3. 测试 API 连接

在前端页面尝试：
1. 点击"项目管理"
2. 点击"新建项目"
3. 填写项目信息并保存

如果成功创建，说明前后端连接正常。

## 五、常见问题排查

### 问题 1：数据库连接失败

**错误信息**：`OperationalError` 或 `InterfaceError` (SQL Server 连接错误)

**解决方案**：
- 检查 SQL Server 服务是否启动（Windows: 服务管理器，Linux: `systemctl status mssql-server`）
- 检查 `.env` 中的数据库连接信息是否正确（用户名、密码、端口 1433）
- 确认数据库已创建
- 确认 SQL Server 允许 TCP/IP 连接（SQL Server 配置管理器）
- 检查防火墙是否允许 1433 端口

### 问题 2：Redis 连接失败

**错误信息**：`ConnectionError: Error connecting to Redis`

**解决方案**：
- 检查 Redis 服务是否启动
- 检查 Redis 端口是否为 6379
- 确认 `.env` 中的 Redis URL 正确

### 问题 3：Celery Worker 启动失败

**错误信息**：`ImportError` 或 `ModuleNotFoundError`

**解决方案**：
- 确保在项目根目录运行命令
- 确保已安装所有依赖：`pip install -r requirements.txt`
- Windows 用户尝试：`celery -A app.celery_app worker --loglevel=info --pool=eventlet`

### 问题 4：前端无法连接后端

**错误信息**：`Network Error` 或 `CORS Error`

**解决方案**：
- 确认后端服务运行在 http://localhost:8000
- 检查 `frontend/vite.config.js` 中的代理配置
- 确认后端 CORS 配置允许前端域名

### 问题 5：端口被占用

**错误信息**：`Address already in use`

**解决方案**：
- 后端端口 8000：修改 `run.py` 中的端口号
- 前端端口 3000：修改 `frontend/vite.config.js` 中的端口号
- 或关闭占用端口的进程

## 六、生产环境部署建议

### 后端

1. 使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
2. 使用 Nginx 作为反向代理
3. 配置 Supervisor 管理进程
4. 使用环境变量管理敏感配置
5. 配置 HTTPS

### 前端

1. 构建生产版本：`npm run build`
2. 使用 Nginx 提供静态文件服务
3. 配置 API 代理
4. 启用 Gzip 压缩
5. 配置缓存策略

## 七、开发工具推荐

- **API 测试**：Postman、Insomnia
- **数据库管理**：SQL Server Management Studio (SSMS)、Azure Data Studio、DBeaver、Navicat
- **Redis 管理**：Redis Desktop Manager、Another Redis Desktop Manager
- **代码编辑器**：VS Code、PyCharm

## 八、下一步

启动成功后，可以：

1. 创建测试项目
2. 添加 API 测试用例
3. 执行测试并查看报告
4. 探索其他功能模块

祝使用愉快！

