from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
from app.tasks import run_api_case_task, run_api_suite_task
from app.schemas import TaskStatus

router = APIRouter(prefix="/api_tests", tags=["api_tests"])


# ============ API Test Case CRUD ============
@router.post("/cases", response_model=schemas.APITestCase, status_code=201)
def create_api_case(case: schemas.APITestCaseCreate, db: Session = Depends(get_db)):
    """创建API测试用例"""
    # 验证项目存在
    project = db.query(models.Project).filter(
        models.Project.id == case.project_id,
        models.Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_case = models.APITestCase(**case.dict())
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case


@router.get("/cases", response_model=List[schemas.APITestCase])
def get_api_cases(project_id: int = None, db: Session = Depends(get_db)):
    """获取API测试用例列表"""
    query = db.query(models.APITestCase)
    if project_id:
        query = query.filter(models.APITestCase.project_id == project_id)
    cases = query.all()
    return cases


@router.get("/cases/{case_id}", response_model=schemas.APITestCase)
def get_api_case(case_id: int, db: Session = Depends(get_db)):
    """获取API测试用例详情"""
    case = db.query(models.APITestCase).filter(models.APITestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="API test case not found")
    return case


@router.put("/cases/{case_id}", response_model=schemas.APITestCase)
def update_api_case(
    case_id: int,
    case_update: schemas.APITestCaseUpdate,
    db: Session = Depends(get_db)
):
    """更新API测试用例"""
    case = db.query(models.APITestCase).filter(models.APITestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="API test case not found")
    
    update_data = case_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
    
    db.commit()
    db.refresh(case)
    return case


@router.delete("/cases/{case_id}", status_code=204)
def delete_api_case(case_id: int, db: Session = Depends(get_db)):
    """删除API测试用例"""
    case = db.query(models.APITestCase).filter(models.APITestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="API test case not found")
    
    db.delete(case)
    db.commit()
    return None


# ============ API Test Suite CRUD ============
@router.post("/suites", response_model=schemas.APITestSuite, status_code=201)
def create_api_suite(suite: schemas.APITestSuiteCreate, db: Session = Depends(get_db)):
    """创建API测试套件"""
    # 验证项目存在
    project = db.query(models.Project).filter(
        models.Project.id == suite.project_id,
        models.Project.is_deleted == False
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 验证用例存在
    if suite.case_ids:
        existing_cases = db.query(models.APITestCase).filter(
            models.APITestCase.id.in_(suite.case_ids)
        ).count()
        if existing_cases != len(suite.case_ids):
            raise HTTPException(status_code=400, detail="Some test cases not found")
    
    db_suite = models.APITestSuite(
        name=suite.name,
        project_id=suite.project_id
    )
    db.add(db_suite)
    db.flush()
    
    # 添加用例到套件
    for order, case_id in enumerate(suite.case_ids):
        suite_case = models.APITestSuiteCase(
            suite_id=db_suite.id,
            case_id=case_id,
            order=order
        )
        db.add(suite_case)
    
    db.commit()
    db.refresh(db_suite)
    
    # 返回时包含case_ids
    result = schemas.APITestSuite.model_validate(db_suite)
    result.case_ids = suite.case_ids
    return result


@router.get("/suites", response_model=List[schemas.APITestSuite])
def get_api_suites(project_id: int = None, db: Session = Depends(get_db)):
    """获取API测试套件列表"""
    query = db.query(models.APITestSuite)
    if project_id:
        query = query.filter(models.APITestSuite.project_id == project_id)
    suites = query.all()
    
    # 填充case_ids
    result = []
    for suite in suites:
        suite_dict = schemas.APITestSuite.model_validate(suite).model_dump()
        case_ids = [
            sc.case_id for sc in sorted(suite.suite_cases, key=lambda x: x.order)
        ]
        suite_dict["case_ids"] = case_ids
        result.append(schemas.APITestSuite(**suite_dict))
    
    return result


@router.get("/suites/{suite_id}", response_model=schemas.APITestSuite)
def get_api_suite(suite_id: int, db: Session = Depends(get_db)):
    """获取API测试套件详情"""
    suite = db.query(models.APITestSuite).filter(models.APITestSuite.id == suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="API test suite not found")
    
    result = schemas.APITestSuite.model_validate(suite)
    case_ids = [sc.case_id for sc in sorted(suite.suite_cases, key=lambda x: x.order)]
    result.case_ids = case_ids
    return result


@router.put("/suites/{suite_id}", response_model=schemas.APITestSuite)
def update_api_suite(
    suite_id: int,
    suite_update: schemas.APITestSuiteUpdate,
    db: Session = Depends(get_db)
):
    """更新API测试套件"""
    suite = db.query(models.APITestSuite).filter(models.APITestSuite.id == suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="API test suite not found")
    
    update_data = suite_update.dict(exclude_unset=True)
    
    # 更新名称
    if "name" in update_data:
        suite.name = update_data["name"]
    
    # 更新用例列表
    if "case_ids" in update_data:
        # 删除旧的关联
        db.query(models.APITestSuiteCase).filter(
            models.APITestSuiteCase.suite_id == suite_id
        ).delete()
        
        # 添加新的关联
        for order, case_id in enumerate(update_data["case_ids"]):
            suite_case = models.APITestSuiteCase(
                suite_id=suite_id,
                case_id=case_id,
                order=order
            )
            db.add(suite_case)
    
    db.commit()
    db.refresh(suite)
    
    result = schemas.APITestSuite.model_validate(suite)
    case_ids = [sc.case_id for sc in sorted(suite.suite_cases, key=lambda x: x.order)]
    result.case_ids = case_ids
    return result


@router.delete("/suites/{suite_id}", status_code=204)
def delete_api_suite(suite_id: int, db: Session = Depends(get_db)):
    """删除API测试套件"""
    suite = db.query(models.APITestSuite).filter(models.APITestSuite.id == suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="API test suite not found")
    
    db.delete(suite)
    db.commit()
    return None


# ============ Test Execution ============
@router.post("/run/{case_id}", response_model=TaskStatus)
def run_api_case(case_id: int, db: Session = Depends(get_db)):
    """执行单个API用例（异步）"""
    case = db.query(models.APITestCase).filter(models.APITestCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="API test case not found")
    
    # 提交Celery任务
    task = run_api_case_task.delay(case_id)
    return TaskStatus(task_id=task.id, status="PENDING")


@router.post("/run_suite/{suite_id}", response_model=TaskStatus)
def run_api_suite(suite_id: int, db: Session = Depends(get_db)):
    """执行测试套件（异步）"""
    suite = db.query(models.APITestSuite).filter(models.APITestSuite.id == suite_id).first()
    if not suite:
        raise HTTPException(status_code=404, detail="API test suite not found")
    
    # 提交Celery任务
    task = run_api_suite_task.delay(suite_id)
    return TaskStatus(task_id=task.id, status="PENDING")

