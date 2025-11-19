from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.schemas import TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str):
    """查询异步任务的状态和结果"""
    task_result = AsyncResult(task_id, app=celery_app)
    
    # 强制从 backend 获取最新状态
    status = task_result.state
    task_info = None
    
    try:
        # 使用 backend 的 get_task_meta 方法获取最新状态
        backend_meta = celery_app.backend.get_task_meta(task_id)
        if backend_meta:
            # backend_meta 结构: {'status': 'PROGRESS', 'result': {...}, 'traceback': None, ...}
            backend_status = backend_meta.get('status')
            if backend_status:
                status = backend_status
            
            # 获取 result（对于 PROGRESS 状态，result 包含 meta 信息）
            backend_result = backend_meta.get('result')
            if backend_result:
                task_info = backend_result
    except Exception as e:
        # 如果 backend 获取失败，使用默认方式
        pass
    
    # 如果从 backend 没获取到，使用 AsyncResult 的方式
    if not task_info:
        task_info = task_result.info
    
    result = None
    error = None
    progress = None
    current_step = None
    status_message = None
    
    # 获取任务元数据（包含进度信息）
    if task_info:
        if isinstance(task_info, dict):
            progress = task_info.get("progress")
            current_step = task_info.get("current_step")
            status_message = task_info.get("status")
            # 如果状态是 PROGRESS，从 info 中获取错误信息
            if status == "PROGRESS":
                error = task_info.get("error")
        elif status != "PROGRESS":
            # 如果不是进度状态，info 可能是错误信息
            error = str(task_info)
    
    # 对于 PENDING 状态，提供默认提示
    if status == "PENDING" and not status_message:
        status_message = "任务已提交，等待 Celery Worker 处理..."
    
    if task_result.ready():
        if task_result.successful():
            result = task_result.result
        else:
            if not error:
                error = str(task_result.info) if task_result.info else "任务执行失败"
    
    return TaskStatus(
        task_id=task_id,
        status=status,
        result=result,
        error=error,
        progress=progress,
        current_step=current_step,
        status_message=status_message
    )

