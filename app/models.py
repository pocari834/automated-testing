from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    api_cases = relationship("APITestCase", back_populates="project", cascade="all, delete-orphan")
    api_suites = relationship("APITestSuite", back_populates="project", cascade="all, delete-orphan")
    ui_cases = relationship("UITestCase", back_populates="project", cascade="all, delete-orphan")
    performance_tests = relationship("PerformanceTest", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("TestReport", back_populates="project", cascade="all, delete-orphan")


class APITestCase(Base):
    __tablename__ = "api_test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    url = Column(Text, nullable=False)
    headers = Column(JSON, nullable=True)
    params = Column(JSON, nullable=True)
    body = Column(JSON, nullable=True)
    assertions = Column(JSON, nullable=True)  # 断言规则
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="api_cases")
    suite_cases = relationship("APITestSuiteCase", back_populates="test_case")


class APITestSuite(Base):
    __tablename__ = "api_test_suites"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="api_suites")
    suite_cases = relationship("APITestSuiteCase", back_populates="test_suite", cascade="all, delete-orphan")


class APITestSuiteCase(Base):
    """关联表：测试套件和测试用例的多对多关系"""
    __tablename__ = "api_test_suite_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("api_test_suites.id"), nullable=False)
    case_id = Column(Integer, ForeignKey("api_test_cases.id"), nullable=False)
    order = Column(Integer, default=0)  # 执行顺序
    
    # Relationships
    test_suite = relationship("APITestSuite", back_populates="suite_cases")
    test_case = relationship("APITestCase", back_populates="suite_cases")


class UITestCase(Base):
    __tablename__ = "ui_test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    script = Column(Text, nullable=False)  # Playwright Python脚本代码
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="ui_cases")


class PerformanceTest(Base):
    __tablename__ = "performance_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    jmx_file_path = Column(String(500), nullable=True)
    status = Column(String(20), default="ready")  # ready, running, completed, failed
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="performance_tests")


class TestReport(Base):
    __tablename__ = "test_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)  # api, ui, performance
    task_id = Column(String(255), nullable=True)  # Celery任务ID
    result_data = Column(JSON, nullable=True)  # 详细的测试结果
    pass_rate = Column(Float, nullable=True)  # 通过率
    start_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # 耗时（秒）
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="reports")

