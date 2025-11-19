from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mssql+pyodbc://(local)/test_platform?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    JMETER_RESULTS_DIR: str = "./jmeter_results"
    
    # Application
    APP_NAME: str = "Test Platform API"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

