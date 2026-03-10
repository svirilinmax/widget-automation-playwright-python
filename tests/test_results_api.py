import os
import tempfile
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import models
from backend.app.database import Base, get_db
from backend.app.main import app


class TestResultsAPI:
    """
    Тестовый класс для API результатов
    """

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """
        Фикстура, автоматически выполняющаяся перед каждым тестом.
        """
        # Создаем временный файл для тестовой БД
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()

        # Создаем тестовую БД
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{self.db_path}"
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
        self.TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Создаем таблицы
        Base.metadata.create_all(bind=self.engine)

        def override_get_db():
            try:
                db = self.TestingSessionLocal()
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)

        self._create_test_data()

        yield

        # Очистка после теста
        Base.metadata.drop_all(bind=self.engine)
        os.unlink(self.db_path)
        app.dependency_overrides.clear()

    def _create_test_data(self):
        """Создание тестовых данных в БД"""
        db = self.TestingSessionLocal()

        test_run = models.TestRun(
            status="completed",
            total_tests=3,
            passed_tests=2,
            failed_tests=1,
            started_at=datetime.now() - timedelta(hours=1),
            completed_at=datetime.now(),
        )
        db.add(test_run)
        db.commit()
        db.refresh(test_run)

        # Создаем тестовые результаты
        results = [
            models.TestResult(
                test_run_id=test_run.id,
                test_name="test_happy_path_generate_code",
                test_file="test_ui_constructor.py",
                status="passed",
                duration=150,
                timestamp=datetime.now(),
            ),
            models.TestResult(
                test_run_id=test_run.id,
                test_name="test_dimensions_input_validation",
                test_file="test_ui_constructor.py",
                status="passed",
                duration=200,
                timestamp=datetime.now() - timedelta(minutes=30),
            ),
            models.TestResult(
                test_run_id=test_run.id,
                test_name="test_navigate_with_invalid_url",
                test_file="test_error_handling.py",
                status="failed",
                duration=300,
                error_message="AssertionError: Expected exception not raised",
                screenshot_path="backend/test_screenshots/failure_test_navigate.png",
                timestamp=datetime.now() - timedelta(hours=1),
            ),
        ]

        for result in results:
            db.add(result)
        db.commit()
        db.close()

    def test_get_all_results(self):
        """Тест получения всех результатов с пагинацией"""
        response = self.client.get("/api/results/?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3
        assert len(data["results"]) >= 3
        assert data["limit"] == 10

    def test_get_all_results_with_filter(self):
        """Тест фильтрации результатов по статусу"""
        response = self.client.get("/api/results/?status=passed")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert all(r["status"] == "passed" for r in data["results"])

    def test_get_recent_results(self):
        """Тест получения результатов за последние N часов"""
        response = self.client.get("/api/results/recent?hours=24")
        assert response.status_code == 200
        data = response.json()
        assert data["period_hours"] == 24
        assert data["stats"]["total"] >= 3
        assert data["stats"]["passed"] >= 2
        assert data["stats"]["failed"] >= 1

    def test_get_result_by_id(self):
        """Тест получения конкретного результата по ID"""
        response = self.client.get("/api/results/")
        assert response.status_code == 200
        result_id = response.json()["results"][0]["id"]

        response = self.client.get(f"/api/results/{result_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == result_id
        assert "test_name" in data
        assert "status" in data

    def test_get_test_history(self):
        """Тест получения истории конкретного теста"""
        test_name = "test_happy_path_generate_code"
        response = self.client.get(f"/api/results/test/{test_name}")
        assert response.status_code == 200
        data = response.json()
        assert data["test_name"] == test_name
        assert data["total_runs"] >= 1
        assert data["success_rate"] > 0
        assert len(data["last_runs"]) >= 1

    def test_get_results_summary(self):
        """Тест получения сводной статистики"""
        response = self.client.get("/api/results/stats/summary?days=7")
        assert response.status_code == 200
        data = response.json()
        assert data["period_days"] == 7
        assert data["total_results"] >= 3
        assert "daily_stats" in data
        assert "top_failed_tests" in data
        assert data["success_rate"] >= 0

    def test_get_nonexistent_result(self):
        """Тест получения несуществующего результата"""
        response = self.client.get("/api/results/99999")
        assert response.status_code == 404

    def test_delete_result(self):
        """Тест удаления результата"""
        # Получаем ID для удаления
        response = self.client.get("/api/results/")
        result_id = response.json()["results"][0]["id"]

        # Удаляем
        response = self.client.delete(f"/api/results/{result_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "deleted"

        # Проверяем, что удалилось
        response = self.client.get(f"/api/results/{result_id}")
        assert response.status_code == 404

    def test_get_screenshot_for_result(self):
        """Тест получения скриншота для результата с ошибкой"""
        # Находим failed тест со скриншотом
        response = self.client.get("/api/results/?status=failed")
        assert response.status_code == 200
        failed_results = response.json()["results"]

        if failed_results:
            result_id = failed_results[0]["id"]
            response = self.client.get(f"/api/results/{result_id}/screenshot")
            assert response.status_code in [200, 404]


def test_health_endpoint():
    """Простой тест для проверки health endpoint"""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
