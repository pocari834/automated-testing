from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from app.database import get_db
from app import models, schemas
from app.tasks import run_performance_test_task
from app.schemas import TaskStatus
from config import settings

router = APIRouter(prefix="/performance_tests", tags=["performance_tests"])


@router.post("", response_model=schemas.PerformanceTest, status_code=201)
def create_performance_test(
    test: schemas.PerformanceTestCreate,
    db: Session = Depends(get_db)
):
    """创建性能测试"""
    # 验证项目存在
    project = db.query(models.Project).filter(
        models.Project.id == test.project_id,
        models.Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_test = models.PerformanceTest(**test.dict())
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


@router.get("", response_model=List[schemas.PerformanceTest])
def get_performance_tests(project_id: int = None, db: Session = Depends(get_db)):
    """获取性能测试列表"""
    query = db.query(models.PerformanceTest)
    if project_id:
        query = query.filter(models.PerformanceTest.project_id == project_id)
    tests = query.all()
    return tests


@router.get("/{test_id}", response_model=schemas.PerformanceTest)
def get_performance_test(test_id: int, db: Session = Depends(get_db)):
    """获取性能测试详情"""
    test = db.query(models.PerformanceTest).filter(
        models.PerformanceTest.id == test_id
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Performance test not found")
    return test


@router.put("/{test_id}", response_model=schemas.PerformanceTest)
def update_performance_test(
    test_id: int,
    test_update: schemas.PerformanceTestUpdate,
    db: Session = Depends(get_db)
):
    """更新性能测试"""
    test = db.query(models.PerformanceTest).filter(
        models.PerformanceTest.id == test_id
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Performance test not found")
    
    update_data = test_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test, field, value)
    
    db.commit()
    db.refresh(test)
    return test


@router.delete("/{test_id}", status_code=204)
def delete_performance_test(test_id: int, db: Session = Depends(get_db)):
    """删除性能测试"""
    test = db.query(models.PerformanceTest).filter(
        models.PerformanceTest.id == test_id
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Performance test not found")
    
    # 删除JMX文件
    if test.jmx_file_path and os.path.exists(test.jmx_file_path):
        os.remove(test.jmx_file_path)
    
    db.delete(test)
    db.commit()
    return None


@router.post("/upload/{test_id}", response_model=schemas.PerformanceTest)
async def upload_jmx_file(
    test_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """上传JMeter的JMX脚本文件"""
    test = db.query(models.PerformanceTest).filter(
        models.PerformanceTest.id == test_id
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Performance test not found")
    
    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 保存文件
    file_path = os.path.join(settings.UPLOAD_DIR, f"{test_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 更新数据库
    test.jmx_file_path = file_path
    test.status = "ready"
    db.commit()
    db.refresh(test)
    
    return test


@router.post("/run/{test_id}", response_model=TaskStatus)
def run_performance_test(test_id: int, db: Session = Depends(get_db)):
    """执行性能测试（异步）"""
    test = db.query(models.PerformanceTest).filter(
        models.PerformanceTest.id == test_id
    ).first()
    if not test:
        raise HTTPException(status_code=404, detail="Performance test not found")
    
    if not test.jmx_file_path or not os.path.exists(test.jmx_file_path):
        raise HTTPException(status_code=400, detail="JMX file not uploaded")
    
    # 更新状态为运行中
    test.status = "running"
    db.commit()
    
    # 提交Celery任务
    task = run_performance_test_task.delay(test_id)
    return TaskStatus(task_id=task.id, status="PENDING")

