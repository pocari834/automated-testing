from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import projects, api_tests, ui_tests, performance_tests, reports, tasks
from config import settings

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(projects.router)
app.include_router(api_tests.router)
app.include_router(ui_tests.router)
app.include_router(performance_tests.router)
app.include_router(reports.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {
        "message": "Test Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}

