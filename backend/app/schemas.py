from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class TestResultBase(BaseModel):
    test_name: str
    test_file: str
    status: str
    duration: int
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    screenshot_path: Optional[str] = None
    metadata: Dict[str, Any] = {}


class TestResultCreate(TestResultBase):
    test_run_id: int


class TestResult(TestResultBase):
    id: int
    test_run_id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class TestRunBase(BaseModel):
    status: str = "pending"
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    duration: int = 0


class TestRunCreate(TestRunBase):
    pass


class TestRun(TestRunBase):
    id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_by: str
    results: List[TestResult] = []

    model_config = ConfigDict(from_attributes=True)


class TestRunSummary(BaseModel):
    id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    total_tests: int
    passed_tests: int
    failed_tests: int
    duration: int
    success_rate: float


class TestRunDetail(TestRun):
    pass


class TestList(BaseModel):
    """Список доступных тестов"""

    total: int
    tests: List[Dict[str, Any]]


class TestRunRequest(BaseModel):
    """Запрос на запуск тестов"""

    test_names: Optional[List[str]] = None
    markers: Optional[List[str]] = None
    parallel: bool = False
    workers: int = 1
