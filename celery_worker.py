"""
启动Celery Worker

使用命令: python celery_worker.py
或者: celery -A app.celery_app worker --loglevel=info
"""
from app.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()

