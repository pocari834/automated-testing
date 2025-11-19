from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ Project Schemas ============
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Project(ProjectBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ API Test Case Schemas ============
class APITestCaseBase(BaseModel):
    name: str
    method: str
    url: str
    headers: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    assertions: Optional[Dict[str, Any]] = None


class APITestCaseCreate(APITestCaseBase):
    project_id: int


class APITestCaseUpdate(BaseModel):
    name: Optional[str] = None
    method: Optional[str] = None
    url: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    assertions: Optional[Dict[str, Any]] = None


class APITestCase(APITestCaseBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ API Test Suite Schemas ============
class APITestSuiteBase(BaseModel):
    name: str


class APITestSuiteCreate(APITestSuiteBase):
    project_id: int
    case_ids: List[int] = []


class APITestSuiteUpdate(BaseModel):
    name: Optional[str] = None
    case_ids: Optional[List[int]] = None


class APITestSuite(APITestSuiteBase):
    id: int
    project_id: int
    case_ids: List[int] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ UI Test Case Schemas ============
class UITestCaseBase(BaseModel):
    name: str
    script: str


class UITestCaseCreate(UITestCaseBase):
    project_id: int


class UITestCaseUpdate(BaseModel):
    name: Optional[str] = None
    script: Optional[str] = None


class UITestCase(UITestCaseBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ Performance Test Schemas ============
class PerformanceTestBase(BaseModel):
    name: str


class PerformanceTestCreate(PerformanceTestBase):
    project_id: int


class PerformanceTestUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None


class PerformanceTest(PerformanceTestBase):
    id: int
    project_id: int
    jmx_file_path: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ Test Report Schemas ============
class TestReportBase(BaseModel):
    name: str
    type: str  # api, ui, performance


class TestReportCreate(TestReportBase):
    project_id: int
    task_id: Optional[str] = None


class TestReport(TestReportBase):
    id: int
    project_id: int
    task_id: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    pass_rate: Optional[float] = None
    start_time: Optional[datetime] = None
    duration: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Task Schemas ============
class TaskStatus(BaseModel):
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# ============ Test Execution Result Schemas ============
class APITestResult(BaseModel):
    success: bool
    duration: float
    response_data: Optional[Dict[str, Any]] = None
    status_code: Optional[int] = None
    assertion_errors: List[str] = []


class UITestResult(BaseModel):
    success: bool
    duration: float
    screenshot_path: Optional[str] = None
    error_log: Optional[str] = None


class PerformanceTestResult(BaseModel):
    success: bool
    duration: float
    metrics: Optional[Dict[str, Any]] = None  # 平均响应时间、95%分位值、吞吐量、错误率
    html_report_path: Optional[str] = None
    error: Optional[str] = None

