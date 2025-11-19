"""
启动Celery Worker

使用命令: python celery_worker.py
或者: celery -A app.celery_app worker --loglevel=info --pool=eventlet
"""
import sys

# 确保任务模块被导入（这样 Celery 才能找到任务）
from app import tasks  # noqa: F401

from app.celery_app import celery_app

if __name__ == "__main__":
    # 使用 worker_main 启动 worker
    # 等同于: celery -A app.celery_app worker --loglevel=info --pool=eventlet
    try:
        # 验证任务已注册
        registered_tasks = list(celery_app.tasks.keys())
        print(f"[INFO] 已注册的任务: {len(registered_tasks)} 个")
        for task_name in registered_tasks:
            if not task_name.startswith('celery.'):
                print(f"  - {task_name}")
        
        print("\n[INFO] 启动 Celery Worker...")
        print("按 Ctrl+C 停止 Worker\n")
        
        celery_app.worker_main([
            'worker',
            '--loglevel=info',
            '--pool=eventlet',
            '--concurrency=4'
        ])
    except KeyboardInterrupt:
        print("\n[INFO] Celery Worker 已停止")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] 启动 Celery Worker 失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

