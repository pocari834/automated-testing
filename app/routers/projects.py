from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=schemas.Project, status_code=201)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """创建新项目"""
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("", response_model=List[schemas.Project])
def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """获取项目列表，支持按项目名分页查询"""
    query = db.query(models.Project).filter(models.Project.is_deleted == False)
    
    if name:
        query = query.filter(models.Project.name.like(f"%{name}%"))
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """获取项目详情"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.put("/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int,
    project_update: schemas.ProjectUpdate,
    db: Session = Depends(get_db)
):
    """更新项目信息"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """删除项目（软删除，标记状态为无效）"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.is_deleted == False
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project.is_deleted = True
    db.commit()
    return None

