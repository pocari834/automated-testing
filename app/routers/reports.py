from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=List[schemas.TestReport])
def get_reports(
    project_id: Optional[int] = None,
    report_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取报告列表"""
    query = db.query(models.TestReport)
    
    if project_id:
        query = query.filter(models.TestReport.project_id == project_id)
    
    if report_type:
        query = query.filter(models.TestReport.type == report_type)
    
    reports = query.order_by(models.TestReport.created_at.desc()).all()
    return reports


@router.get("/{report_id}", response_model=schemas.TestReport)
def get_report(report_id: int, db: Session = Depends(get_db)):
    """获取详细报告"""
    report = db.query(models.TestReport).filter(
        models.TestReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Test report not found")
    
    return report

