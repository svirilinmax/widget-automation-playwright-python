import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from . import crud, schemas
from .database import SessionLocal

logger = logging.getLogger(__name__)


class PytestRunner:
    """Запуск pytest тестов и сохранение результатов"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.current_run = None
        logger.info("PytestRunner initialized")

    def run_tests(
        self,
        test_names: Optional[List[str]] = None,
        markers: Optional[List[str]] = None,
        parallel: bool = False,
        workers: int = 1,
    ) -> int:
        """
        Запустить тесты и сохранить результаты
        """
        # Создаем запись о запуске
        test_run = crud.create_test_run(self.db, schemas.TestRunCreate(status="running"))
        self.current_run = test_run
        logger.info(f"Created test run with ID: {test_run.id}")

        # Запускаем тесты в отдельном потоке
        thread = threading.Thread(
            target=self._run_tests_thread, args=(test_run.id, test_names, markers, parallel, workers)
        )
        thread.start()
        logger.debug(f"Test thread started for run {test_run.id}")

        return test_run.id

    def _run_tests_thread(
        self, run_id: int, test_names: Optional[List[str]], markers: Optional[List[str]], parallel: bool, workers: int
    ):
        """Запуск тестов в отдельном потоке"""
        db = SessionLocal()
        try:
            start_time = time.time()
            logger.info(f"Starting test run {run_id}")

            # Определяем пути
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            backend_dir = current_file.parent.parent

            reports_dir = backend_dir / "test_reports"
            reports_dir.mkdir(exist_ok=True)
            logger.debug(f"Reports directory: {reports_dir}")

            # Формируем команду pytest
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "-v",
                "--tb=short",
                "--json-report",
                f"--json-report-file={reports_dir / f'report_{run_id}.json'}",
            ]

            # Добавляем параллельный запуск если требуется
            if parallel:
                try:
                    cmd.extend(["-n", str(workers)])
                    logger.info(f"Parallel execution enabled with {workers} workers")
                except ImportError:
                    logger.warning("pytest-xdist not installed, running sequentially")
                    parallel = False

            # Если выбраны конкретные тесты
            if test_names:
                cmd.extend(test_names)
                logger.info(f"Running specific tests: {test_names}")
            elif markers:
                for marker in markers:
                    cmd.extend(["-m", marker])
                logger.info(f"Running tests with markers: {markers}")

            logger.info(f"Running command: {' '.join(cmd)}")

            # Запускаем тесты
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(project_root),
                env={**os.environ, "PYTHONPATH": str(project_root)},
                timeout=300,
            )

            logger.info(f"Tests completed with return code: {process.returncode}")
            if process.stdout:
                logger.debug(f"STDOUT: {process.stdout[:500]}")
            if process.stderr:
                logger.warning(f"STDERR: {process.stderr[:500]}")

            duration = int(time.time() - start_time)

            # Парсим JSON отчет
            report_path = reports_dir / f"report_{run_id}.json"
            passed = 0
            failed = 0
            total = 0

            if report_path.exists():
                with open(report_path, "r", encoding="utf-8") as f:
                    report_data = json.load(f)

                total = report_data.get("summary", {}).get("total", 0)
                passed = report_data.get("summary", {}).get("passed", 0)
                failed = report_data.get("summary", {}).get("failed", 0)

                logger.info(f"Results: total={total}, passed={passed}, failed={failed}")

                # Сохраняем результаты каждого теста
                for test in report_data.get("tests", []):
                    test_nodeid = test.get("nodeid", "")
                    outcome = test.get("outcome", "unknown")
                    test_duration = int(test.get("duration", 0) * 1000)

                    # Ищем скриншот если тест упал
                    screenshot_path = None
                    if outcome == "failed":
                        screenshots_dir = backend_dir / "test_screenshots"
                        if screenshots_dir.exists():
                            test_name = test_nodeid.split("::")[-1].split("[")[0]
                            for screenshot in screenshots_dir.glob(f"*{test_name}*.png"):
                                screenshot_path = str(screenshot.relative_to(project_root))
                                logger.info(f"Found screenshot for {test_name}: {screenshot_path}")
                                break

                    result = schemas.TestResultCreate(
                        test_run_id=run_id,
                        test_name=test_nodeid,
                        test_file=test_nodeid.split("::")[0] if "::" in test_nodeid else test_nodeid,
                        status=outcome,
                        duration=test_duration,
                        error_message=test.get("call", {}).get("longrepr", "") if outcome == "failed" else None,
                        screenshot_path=screenshot_path,
                    )
                    crud.create_test_result(db, result)
                    logger.debug(f"Saved result for {test_nodeid}: {outcome}")
            else:
                logger.error(f"Report file not found: {report_path}")

            # Обновляем статус запуска
            final_status = "completed" if failed == 0 else "failed"
            crud.update_test_run(
                db,
                run_id,
                status=final_status,
                completed_at=datetime.now(timezone.utc).replace(tzinfo=None),
                duration=duration,
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
            )

            logger.info(f"Test run {run_id} completed: {passed} passed, {failed} failed, status: {final_status}")

        except subprocess.TimeoutExpired:
            logger.error(f"Test run {run_id} timed out after 300 seconds")
            crud.update_test_run(
                db, run_id, status="failed", completed_at=datetime.now(timezone.utc).replace(tzinfo=None), duration=300
            )
        except Exception as e:
            logger.exception(f"Error running tests: {e}")
            crud.update_test_run(
                db, run_id, status="failed", completed_at=datetime.now(timezone.utc).replace(tzinfo=None)
            )
        finally:
            db.close()
            logger.debug(f"Database connection closed for run {run_id}")

    def get_run_status(self, run_id: int) -> Dict[str, Any]:
        """Получить статус запуска"""
        logger.debug(f"Getting status for run {run_id}")
        test_run = crud.get_test_run(self.db, run_id)
        if not test_run:
            logger.warning(f"Run {run_id} not found")
            return {
                "id": run_id,
                "status": "not_found",
                "started_at": None,
                "completed_at": None,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "duration": 0,
                "results": [],
            }

        results = crud.get_test_results(self.db, run_id)
        logger.debug(f"Found {len(results)} results for run {run_id}")

        return {
            "id": test_run.id,
            "status": test_run.status,
            "started_at": test_run.started_at.isoformat() if test_run.started_at else None,
            "completed_at": test_run.completed_at.isoformat() if test_run.completed_at else None,
            "total": test_run.total_tests,
            "passed": test_run.passed_tests,
            "failed": test_run.failed_tests,
            "duration": test_run.duration,
            "results": [
                {
                    "name": r.test_name,
                    "status": r.status,
                    "duration": r.duration,
                    "error": r.error_message,
                    "screenshot": r.screenshot_path,
                }
                for r in results
            ],
        }

    def discover_tests(self) -> List[Dict[str, Any]]:
        """Получить список всех тестов"""
        logger.info("Discovering tests")
        result = []
        try:
            # Определяем корень проекта
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent

            logger.debug(f"Project root: {project_root}")
            logger.debug(f"Tests directory: {project_root / 'tests'}")
            logger.debug(f"Tests exist: {(project_root / 'tests').exists()}")

            # Временный файл для сохранения структуры тестов
            import json
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
                tmp_file = tmp.name

            # Запускаем pytest для сбора тестов
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "--collect-only",
                "--quiet",
                "--json-report",
                f"--json-report-file={tmp_file}",
            ]

            logger.debug(f"Running command: {' '.join(cmd)}")

            output = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(project_root),
                env={**os.environ, "PYTHONPATH": str(project_root)},
                timeout=30,
            )

            logger.debug(f"Pytest return code: {output.returncode}")

            # Читаем JSON отчет
            if os.path.exists(tmp_file):
                with open(tmp_file, "r", encoding="utf-8") as f:
                    report_data = json.load(f)

                # Извлекаем тесты из JSON
                if "collectors" in report_data:
                    for collector in report_data["collectors"]:
                        nodeid = collector.get("nodeid", "")
                        if nodeid.startswith("tests/") and "result" in collector:
                            for test in collector["result"]:
                                if test.get("type") in ["Function", "Method"]:
                                    test_nodeid = test.get("nodeid", "")
                                    test_name = test.get("name", "")

                                    if test_nodeid and "::" in test_nodeid:
                                        parts = test_nodeid.split("::")
                                        test_info = {
                                            "name": test_name or parts[-1],
                                            "class": parts[1] if len(parts) > 2 else "",
                                            "file": os.path.basename(parts[0]),
                                            "full_name": test_nodeid,
                                            "path": parts[0],
                                        }
                                        result.append(test_info)
                                        logger.debug(f"Found test: {test_info['name']}")

                # Удаляем временный файл
                try:
                    os.unlink(tmp_file)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {tmp_file}: {e}")

            logger.info(f"Discovered {len(result)} tests")

        except Exception as e:
            logger.exception(f"Error during test discovery: {e}")

        return result
