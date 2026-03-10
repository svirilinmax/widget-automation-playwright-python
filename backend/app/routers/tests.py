import subprocess
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas, test_runner
from ..database import get_db

router = APIRouter(prefix="/api/tests", tags=["tests"])

_runner = None


def get_runner(db: Session = Depends(get_db)):
    global _runner
    if _runner is None:
        _runner = test_runner.PytestRunner(db)
    return _runner


@router.get("/list", response_model=schemas.TestList)
async def list_tests():
    """Получить список доступных тестов"""
    try:
        db = next(get_db())
        runner = test_runner.PytestRunner(db)
        tests = runner.discover_tests()
        print(f"Returning {len(tests)} tests")
        return {"total": len(tests), "tests": tests}
    except Exception as e:
        print(f"Error in list_tests: {e}")
        import traceback

        traceback.print_exc()
        return {"total": 0, "tests": []}


@router.post("/run")
async def run_tests(request: schemas.TestRunRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Запустить тесты"""
    runner = test_runner.PytestRunner(db)

    # Создаем запись о запуске
    test_run = crud.create_test_run(db, schemas.TestRunCreate(status="pending"))

    # Запускаем тесты в фоне
    background_tasks.add_task(
        runner._run_tests_thread, test_run.id, request.test_names, request.markers, request.parallel, request.workers
    )

    return {"run_id": test_run.id, "status": "started"}


@router.get("/run/{run_id}")
async def get_run_status(run_id: int, db: Session = Depends(get_db)):
    """Получить статус запуска тестов"""
    runner = test_runner.PytestRunner(db)
    status = runner.get_run_status(run_id)
    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])
    return status


@router.get("/runs", response_model=List[schemas.TestRunSummary])
async def get_test_runs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить историю запусков"""
    runs = crud.get_test_runs(db, skip=skip, limit=limit)
    result = []
    for run in runs:
        success_rate = (run.passed_tests / run.total_tests * 100) if run.total_tests > 0 else 0
        result.append(
            schemas.TestRunSummary(
                id=run.id,
                status=run.status,
                started_at=run.started_at,
                completed_at=run.completed_at,
                total_tests=run.total_tests,
                passed_tests=run.passed_tests,
                failed_tests=run.failed_tests,
                duration=run.duration,
                success_rate=round(success_rate, 2),
            )
        )
    return result


@router.get("/run/{run_id}/results")
async def get_test_results(run_id: int, db: Session = Depends(get_db)):
    """Получить результаты конкретного запуска"""
    results = crud.get_test_results(db, run_id)
    return results


@router.delete("/run/{run_id}")
async def delete_run(run_id: int, db: Session = Depends(get_db)):
    """Удалить запись о запуске"""
    success = crud.delete_test_run(db, run_id)
    if not success:
        raise HTTPException(status_code=404, detail="Run not found")
    return {"status": "deleted"}


@router.get("/screenshot/{filename}")
async def get_screenshot(filename: str):
    """Получить скриншот по имени файла"""
    import os

    from fastapi.responses import FileResponse

    screenshot_path = os.path.join("test_screenshots", filename)
    if not os.path.exists(screenshot_path):
        raise HTTPException(status_code=404, detail="Screenshot not found")

    return FileResponse(screenshot_path)


@router.get("/debug")
async def debug_tests():
    """Отладочный эндпоинт для проверки обнаружения тестов"""
    import os
    import sys
    from pathlib import Path

    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent

    result = {
        "current_file": str(current_file),
        "project_root": str(project_root),
        "cwd": os.getcwd(),
        "pythonpath": os.environ.get("PYTHONPATH", ""),
        "files_in_tests": [],
    }

    tests_dir = project_root / "tests"
    result["tests_dir"] = str(tests_dir)
    result["tests_dir_exists"] = tests_dir.exists()

    if tests_dir.exists():
        result["files_in_tests"] = [f.name for f in tests_dir.glob("test_*.py")]
        result["all_files"] = [f.name for f in tests_dir.glob("*")]

    possible_paths = [
        project_root / "tests",
        Path.cwd() / "tests",
        Path.cwd().parent / "tests",
    ]

    result["possible_paths"] = {str(p): p.exists() for p in possible_paths}

    try:
        output = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-vv"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=10,
            env={**os.environ, "PYTHONPATH": str(project_root)},
        )
        result["pytest_stdout"] = output.stdout[:1000]
        result["pytest_stderr"] = output.stderr[:1000]
        result["pytest_returncode"] = output.returncode
    except Exception as e:
        result["pytest_error"] = str(e)

    # Проверяем можно ли импортировать тесты
    try:
        sys.path.insert(0, str(project_root))
        import tests

        result["can_import_tests"] = True
        result["tests_module"] = str(tests.__file__)
    except Exception as e:
        result["can_import_tests"] = False
        result["import_error"] = str(e)

    return result
