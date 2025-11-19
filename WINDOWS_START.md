# Windows 快速启动指南

专门为 Windows 用户准备的启动指南。

## 前置检查

### 1. 检查 Python 安装

在 PowerShell 中运行：

```powershell
py --version
```

如果显示版本号（如 `Python 3.12.3`），说明 Python 已安装。

**注意**：Windows 上通常使用 `py` 命令而不是 `python` 命令。

### 2. 检查 SQL Server 和 Redis

确保 SQL Server 和 Redis 服务已启动。

## 快速启动步骤

### 步骤 1：创建虚拟环境

```powershell
# 在项目根目录 D:\testing
py -m venv venv
```

### 步骤 2：激活虚拟环境

```powershell
venv\Scripts\Activate.ps1
```

如果遇到执行策略错误，运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

然后重新激活：
```powershell
venv\Scripts\Activate.ps1
```

激活成功后，命令行前面会显示 `(venv)`。

### 步骤 3：安装依赖

```powershell
pip install -r requirements.txt
```

### 步骤 4：创建 .env 文件

在项目根目录创建 `.env` 文件，内容：

```env
DATABASE_URL=mssql+pymssql://sa:123456@localhost:1433/test_platform
DATABASE_ECHO=False
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
UPLOAD_DIR=./uploads
JMETER_RESULTS_DIR=./jmeter_results
APP_NAME=Test Platform API
DEBUG=True
SECRET_KEY=your-secret-key-here
```

**重要**：将 `123456` 替换为你的 SQL Server sa 密码（如果不同）。

### 步骤 5：创建数据库

**方式一：使用 SQL Server Management Studio (SSMS)**
1. 打开 SSMS，连接到 SQL Server 实例（localhost）
2. 右键点击"数据库" -> "新建数据库"
3. 数据库名称：`test_platform`
4. 点击"确定"

**方式二：使用 sqlcmd 命令行**
```powershell
sqlcmd -S localhost -U sa -P 123456 -Q "CREATE DATABASE test_platform"
```

**方式三：使用 Python 脚本（推荐）**
```powershell
# 先确保数据库已创建，然后运行：
py init_db.py
```

### 步骤 6：启动服务（需要 3 个 PowerShell 窗口）

#### 窗口 1：FastAPI 后端

```powershell
# 确保在项目根目录，且虚拟环境已激活
py run.py
```

看到类似输出表示成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

访问：http://localhost:8000/docs

#### 窗口 2：Celery Worker

```powershell
# 确保在项目根目录，且虚拟环境已激活
celery -A app.celery_app worker --loglevel=info --pool=eventlet
```

**注意**：Windows 上需要使用 `--pool=eventlet`，如果报错，先安装：
```powershell
pip install eventlet
```

#### 窗口 3：前端（可选）

```powershell
cd frontend
npm install
npm run dev
```

访问：http://localhost:3000

## 常见问题

### 问题 1：`python` 命令不可用

**解决方案**：使用 `py` 命令代替 `python`。

### 问题 2：虚拟环境激活失败

**错误**：`无法加载文件 venv\Scripts\Activate.ps1，因为在此系统上禁止运行脚本`

**解决方案**：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题 3：Celery Worker 启动失败

**错误**：`NotImplementedError: Windows does not support fork()`

**解决方案**：使用 eventlet 池：
```powershell
pip install eventlet
celery -A app.celery_app worker --loglevel=info --pool=eventlet
```

### 问题 4：SQL Server 连接失败

**检查项**：
1. SQL Server 服务是否启动（服务管理器查看 "SQL Server (MSSQLSERVER)" 或使用 `sc query MSSQLSERVER`）
2. `.env` 文件中的用户名、密码、端口是否正确（默认端口 1433）
3. 数据库是否已创建
4. SQL Server 是否允许 TCP/IP 连接（SQL Server 配置管理器 -> SQL Server 网络配置）
5. 防火墙是否允许 1433 端口

### 问题 5：Redis 连接失败

**检查项**：
1. Redis 服务是否启动
2. 如果使用 Redis for Windows，确保 `redis-server.exe` 正在运行

## 验证启动

1. **后端 API**：浏览器打开 http://localhost:8000/docs
2. **前端界面**：浏览器打开 http://localhost:3000
3. **测试连接**：在前端创建项目，如果成功则说明连接正常

## 完整命令清单

```powershell
# 1. 创建虚拟环境
py -m venv venv

# 2. 激活虚拟环境
venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动 FastAPI（窗口1）
py run.py

# 5. 启动 Celery（窗口2）
celery -A app.celery_app worker --loglevel=info --pool=eventlet

# 6. 启动前端（窗口3，可选）
cd frontend
npm install
npm run dev
```

## 提示

- 每次打开新的 PowerShell 窗口时，需要重新激活虚拟环境
- 确保 SQL Server 和 Redis 服务在后台运行
- 如果修改了代码，FastAPI 会自动重载（开发模式）
- Celery Worker 需要保持运行才能执行异步任务

