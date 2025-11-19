from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult
from app.celery_app import celery_app
from app.schemas import TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/{task_id}", response_model=TaskStatus)
def get_task_status(task_id: str):
    """查询异步任务的状态和结果"""
    task_result = AsyncResult(task_id, app=celery_app)
    
    status = task_result.state
    
    result = None
    error = None
    
    if task_result.ready():
        if task_result.successful():
            result = task_result.result
        else:
            error = str(task_result.info)
    
    return TaskStatus(
        task_id=task_id,
        status=status,
        result=result,
        error=error
    )

