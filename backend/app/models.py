from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text

from .database import Base


class TestRun(Base):
    """Модель для запуска тестов"""

    __tablename__ = "test_runs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String(50), default="pending")
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    completed_at = Column(DateTime, nullable=True)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    duration = Column(Integer, default=0)  # в секундах
    created_by = Column(String(100), default="web_interface")


class TestResult(Base):
    """Модель для результатов отдельных тестов"""

    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    test_run_id = Column(Integer, index=True)
    test_name = Column(String(255))
    test_file = Column(String(255))
    status = Column(String(50))
    duration = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    traceback = Column(Text, nullable=True)
    screenshot_path = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    test_metadata = Column(JSON, default={})
