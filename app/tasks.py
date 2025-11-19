from celery import Task
from sqlalchemy.orm import Session
from app.celery_app import celery_app
from app.database import SessionLocal
from app import models, schemas
from app.services.api_test_service import run_api_case
from app.services.ui_test_service import run_ui_case
from app.services.performance_test_service import run_performance_test
from datetime import datetime
import traceback


@celery_app.task(bind=True)
def run_api_case_task(self: Task, case_id: int):
    """执行API测试用例的Celery任务"""
    db: Session = SessionLocal()
    try:
        case = db.query(models.APITestCase).filter(models.APITestCase.id == case_id).first()
        if not case:
            raise ValueError(f"API test case {case_id} not found")
        
        # 执行测试
        result = run_api_case(case)
        
        # 创建测试报告
        report = models.TestReport(
            project_id=case.project_id,
            name=f"API Test: {case.name}",
            type="api",
            task_id=self.request.id,
            result_data=result.dict(),
            pass_rate=100.0 if result.success else 0.0,
            start_time=datetime.now(),
            duration=result.duration
        )
        db.add(report)
        db.commit()
        
        return result.dict()
    except Exception as e:
        db.rollback()
        error_msg = f"Error executing API test case: {str(e)}\n{traceback.format_exc()}"
        self.update_state(state="FAILURE", meta={"error": error_msg})
        raise
    finally:
        db.close()


@celery_app.task(bind=True)
def run_api_suite_task(self: Task, suite_id: int):
    """执行API测试套件的Celery任务"""
    db: Session = SessionLocal()
    try:
        suite = db.query(models.APITestSuite).filter(models.APITestSuite.id == suite_id).first()
        if not suite:
            raise ValueError(f"API test suite {suite_id} not found")
        
        # 获取套件中的所有用例（按顺序）
        suite_cases = sorted(suite.suite_cases, key=lambda x: x.order)
        case_ids = [sc.case_id for sc in suite_cases]
        
        if not case_ids:
            raise ValueError("Test suite is empty")
        
        # 执行所有用例
        start_time = datetime.now()
        results = []
        total_cases = len(case_ids)
        passed_cases = 0
        
        for case_id in case_ids:
            case = db.query(models.APITestCase).filter(models.APITestCase.id == case_id).first()
            if case:
                result = run_api_case(case)
                results.append({
                    "case_id": case_id,
                    "case_name": case.name,
                    "result": result.dict()
                })
                if result.success:
                    passed_cases += 1
        
        duration = (datetime.now() - start_time).total_seconds()
        pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
        
        # 创建测试报告
        report = models.TestReport(
            project_id=suite.project_id,
            name=f"API Test Suite: {suite.name}",
            type="api",
            task_id=self.request.id,
            result_data={
                "suite_id": suite_id,
                "suite_name": suite.name,
                "total_cases": total_cases,
                "passed_cases": passed_cases,
                "results": results
            },
            pass_rate=pass_rate,
            start_time=start_time,
            duration=duration
        )
        db.add(report)
        db.commit()
        
        return {
            "suite_id": suite_id,
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "pass_rate": pass_rate,
            "results": results
        }
    except Exception as e:
        db.rollback()
        error_msg = f"Error executing API test suite: {str(e)}\n{traceback.format_exc()}"
        self.update_state(state="FAILURE", meta={"error": error_msg})
        raise
    finally:
        db.close()


@celery_app.task(bind=True)
def run_ui_case_task(self: Task, case_id: int):
    """执行UI测试用例的Celery任务"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"[UI Test Task] 开始执行用例 ID: {case_id}")
    
    db: Session = SessionLocal()
    case = None
    try:
        case = db.query(models.UITestCase).filter(models.UITestCase.id == case_id).first()
        if not case:
            raise ValueError(f"UI test case {case_id} not found")
        
        logger.info(f"[UI Test Task] 用例名称: {case.name}")
        
        # 更新进度：初始化（立即更新，确保任务状态改变）
        try:
            logger.info("[UI Test Task] 更新状态: 初始化中...")
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": 0,
                    "current_step": "初始化测试环境",
                    "total_steps": 0,
                    "status": "任务已开始，正在初始化..."
                }
            )
            # 强制刷新状态
            import time as time_module
            time_module.sleep(0.1)  # 短暂延迟确保状态更新
            logger.info("[UI Test Task] 状态已更新")
        except Exception as state_error:
            # 如果更新状态失败，记录但不中断执行
            logger.warning(f"Warning: Failed to update task state: {state_error}")
            import traceback
            traceback.print_exc()
        
        # 执行测试（传入进度回调）
        def progress_callback(progress, current_step, status):
            """进度回调函数"""
            try:
                logger.info(f"[UI Test Task] 进度更新: {progress}% - {current_step} - {status}")
                # 使用 update_state 更新状态
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "progress": progress,
                        "current_step": current_step,
                        "status": status
                    }
                )
            except Exception as callback_error:
                # 如果回调失败，记录但不中断执行
                logger.warning(f"Warning: Failed to update progress: {callback_error}")
                import traceback
                traceback.print_exc()
        
        logger.info("[UI Test Task] 开始执行测试用例...")
        result = run_ui_case(case, progress_callback=progress_callback)
        logger.info(f"[UI Test Task] 测试执行完成，结果: {'成功' if result.success else '失败'}")
        
        # 创建测试报告（无论成功还是失败都创建）
        report = models.TestReport(
            project_id=case.project_id,
            name=f"UI Test: {case.name}",
            type="ui",
            task_id=self.request.id,
            result_data=result.dict(),
            pass_rate=100.0 if result.success else 0.0,
            start_time=datetime.now(),
            duration=result.duration
        )
        db.add(report)
        db.commit()
        
        return result.dict()
    except Exception as e:
        db.rollback()
        error_msg = f"Error executing UI test case: {str(e)}\n{traceback.format_exc()}"
        
        # 即使失败也创建报告（如果case存在）
        try:
            if case:
                report = models.TestReport(
                    project_id=case.project_id,
                    name=f"UI Test: {case.name} (Failed)",
                    type="ui",
                    task_id=self.request.id,
                    result_data={
                        "success": False,
                        "error_log": error_msg,
                        "duration": 0.0,
                        "steps": []
                    },
                    pass_rate=0.0,
                    start_time=datetime.now(),
                    duration=0.0
                )
                db.add(report)
                db.commit()
        except Exception as report_error:
            # 忽略报告创建错误，避免掩盖原始错误
            pass
        
        self.update_state(state="FAILURE", meta={"error": error_msg})
        raise
    finally:
        db.close()


@celery_app.task(bind=True)
def run_performance_test_task(self: Task, test_id: int):
    """执行性能测试的Celery任务"""
    db: Session = SessionLocal()
    try:
        test = db.query(models.PerformanceTest).filter(models.PerformanceTest.id == test_id).first()
        if not test:
            raise ValueError(f"Performance test {test_id} not found")
        
        # 执行测试
        start_time = datetime.now()
        result = run_performance_test(test)
        duration = (datetime.now() - start_time).total_seconds()
        
        # 更新测试状态
        test.status = "completed" if result.success else "failed"
        db.commit()
        
        # 创建测试报告
        report = models.TestReport(
            project_id=test.project_id,
            name=f"Performance Test: {test.name}",
            type="performance",
            task_id=self.request.id,
            result_data=result.dict(),
            pass_rate=100.0 if result.success else 0.0,
            start_time=start_time,
            duration=duration
        )
        db.add(report)
        db.commit()
        
        return result.dict()
    except Exception as e:
        db.rollback()
        # 更新测试状态为失败
        test = db.query(models.PerformanceTest).filter(models.PerformanceTest.id == test_id).first()
        if test:
            test.status = "failed"
            db.commit()
        
        error_msg = f"Error executing performance test: {str(e)}\n{traceback.format_exc()}"
        self.update_state(state="FAILURE", meta={"error": error_msg})
        raise
    finally:
        db.close()

