from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.tasks import run_ui_case_task
from app.schemas import TaskStatus

router = APIRouter(prefix="/ui_tests", tags=["ui_tests"])


@router.post("/cases", response_model=schemas.UITestCase, status_code=201)
def create_ui_case(case: schemas.UITestCaseCreate, db: Session = Depends(get_db)):
    """创建UI测试用例"""
    # 验证项目存在
    project = db.query(models.Project).filter(
        models.Project.id == case.project_id,
        models.Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_case = models.UITestCase(**case.dict())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


@router.get("/cases", response_model=List[schemas.UITestCase])
def get_ui_cases(project_id: int = None, db: Session = Depends(get_db)):
    """获取UI测试用例列表"""
    query = db.query(models.UITestCase)
    if project_id:
        query = query.filter(models.UITestCase.project_id == project_id)
    cases = query.all()
    return cases


@router.get("/cases/{case_id}", response_model=schemas.UITestCase)
def get_ui_case(case_id: int, db: Session = Depends(get_db)):
    """获取UI测试用例详情"""
    case = db.query(models.UITestCase).filter(models.UITestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="UI test case not found")
    return case


@router.put("/cases/{case_id}", response_model=schemas.UITestCase)
def update_ui_case(
    case_id: int,
    case_update: schemas.UITestCaseUpdate,
    db: Session = Depends(get_db)
):
    """更新UI测试用例"""
    case = db.query(models.UITestCase).filter(models.UITestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="UI test case not found")
    
    update_data = case_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
    
    db.commit()
    db.refresh(case)
    return case


@router.delete("/cases/{case_id}", status_code=204)
def delete_ui_case(case_id: int, db: Session = Depends(get_db)):
    """删除UI测试用例"""
    case = db.query(models.UITestCase).filter(models.UITestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="UI test case not found")
    
    db.delete(case)
    db.commit()
    return None


@router.post("/run/{case_id}", response_model=TaskStatus)
def run_ui_case(case_id: int, db: Session = Depends(get_db)):
    """执行单个UI用例（异步）"""
    case = db.query(models.UITestCase).filter(models.UITestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="UI test case not found")
    
    # 提交Celery任务
    task = run_ui_case_task.delay(case_id)
    return TaskStatus(task_id=task.id, status="PENDING")

