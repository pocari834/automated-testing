from celery import Celery
from config import settings

celery_app = Celery(
    "test_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks']  # 包含任务模块
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # 任务结果过期时间（秒）
    result_expires=3600,
    # 任务跟踪（用于进度更新）
    task_track_started=True,
    task_send_sent_event=True,
    # 确保状态更新被保存
    result_persistent=True,
)

# 自动发现任务（可选，但更可靠）
celery_app.autodiscover_tasks(['app'])

