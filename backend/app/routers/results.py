import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("/")
async def get_all_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    test_name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Получить все результаты с фильтрацией
    """
    # Базовая фильтрация
    query = db.query(models.TestResult)

    if status:
        query = query.filter(models.TestResult.status == status)
    if test_name:
        query = query.filter(models.TestResult.test_name.contains(test_name))

    total = query.count()
    results = query.order_by(models.TestResult.timestamp.desc()).offset(skip).limit(limit).all()

    return {"total": total, "results": results, "skip": skip, "limit": limit}


@router.get("/recent")
async def get_recent_results(hours: int = Query(24, ge=1, le=720), db: Session = Depends(get_db)):
    """
    Получить результаты за последние N часов
    """
    since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours)
    results = (
        db.query(models.TestResult)
        .filter(models.TestResult.timestamp >= since)
        .order_by(models.TestResult.timestamp.desc())
        .all()
    )

    # Группировка по статусам
    stats = {
        "total": len(results),
        "passed": len([r for r in results if r.status == "passed"]),
        "failed": len([r for r in results if r.status == "failed"]),
        "skipped": len([r for r in results if r.status == "skipped"]),
        "error": len([r for r in results if r.status == "error"]),
    }

    return {
        "period_hours": hours,
        "since": since,
        "stats": stats,
        "results": results[:50],  # Ограничиваем до 50 последних
    }


@router.get("/{result_id}")
async def get_result_by_id(result_id: int, db: Session = Depends(get_db)):
    """
    Получить конкретный результат по ID
    """
    result = db.query(models.TestResult).filter(models.TestResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/test/{test_name}")
async def get_test_history(test_name: str, limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db)):
    """
    Получить историю запусков конкретного теста
    """
    results = (
        db.query(models.TestResult)
        .filter(models.TestResult.test_name == test_name)
        .order_by(models.TestResult.timestamp.desc())
        .limit(limit)
        .all()
    )

    # Статистика по тесту
    total_runs = db.query(models.TestResult).filter(models.TestResult.test_name == test_name).count()

    success_runs = (
        db.query(models.TestResult)
        .filter(models.TestResult.test_name == test_name, models.TestResult.status == "passed")
        .count()
    )

    success_rate = (success_runs / total_runs * 100) if total_runs > 0 else 0

    return {
        "test_name": test_name,
        "total_runs": total_runs,
        "success_rate": round(success_rate, 2),
        "last_runs": results,
        "average_duration": sum(r.duration for r in results) / len(results) if results else 0,
    }


@router.get("/{result_id}/screenshot")
async def get_result_screenshot(result_id: int, db: Session = Depends(get_db)):
    """
    Получить скриншот для результата
    """
    import os

    from fastapi.responses import FileResponse

    result = db.query(models.TestResult).filter(models.TestResult.id == result_id).first()
    if not result or not result.screenshot_path:
        raise HTTPException(status_code=404, detail="Screenshot not found")

    if not os.path.exists(result.screenshot_path):
        raise HTTPException(status_code=404, detail="Screenshot file not found")

    return FileResponse(
        result.screenshot_path, media_type="image/png", filename=os.path.basename(result.screenshot_path)
    )


@router.get("/stats/summary")
async def get_results_summary(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    """
    Получить сводную статистику по результатам
    """
    since = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

    # Все результаты за период
    results = db.query(models.TestResult).filter(models.TestResult.timestamp >= since).all()

    # Статистика по дням
    daily_stats = {}
    for result in results:
        day = result.timestamp.date().isoformat()
        if day not in daily_stats:
            daily_stats[day] = {"total": 0, "passed": 0, "failed": 0}

        daily_stats[day]["total"] += 1
        if result.status == "passed":
            daily_stats[day]["passed"] += 1
        elif result.status == "failed":
            daily_stats[day]["failed"] += 1

    # Топ проблемных тестов
    failed_tests = {}
    for result in results:
        if result.status == "failed":
            failed_tests[result.test_name] = failed_tests.get(result.test_name, 0) + 1

    top_failed = sorted(failed_tests.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "period_days": days,
        "since": since,
        "total_results": len(results),
        "daily_stats": daily_stats,
        "top_failed_tests": [{"test": t, "failures": c} for t, c in top_failed],
        "success_rate": (
            round(len([r for r in results if r.status == "passed"]) / len(results) * 100) if results else 0
        ),
    }


@router.delete("/{result_id}")
async def delete_result(result_id: int, db: Session = Depends(get_db)):
    """
    Удалить конкретный результат
    """
    result = db.query(models.TestResult).filter(models.TestResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    # Опционально удаляем файл скриншота
    if result.screenshot_path and os.path.exists(result.screenshot_path):
        try:
            os.remove(result.screenshot_path)
        except Exception as e:
            print(f"Error deleting screenshot: {e}")

    db.delete(result)
    db.commit()

    return {"status": "deleted", "id": result_id}


@router.delete("/cleanup/old")
async def cleanup_old_results(days: int = Query(30, ge=1), db: Session = Depends(get_db)):
    """
    Очистить старые результаты (запускать по расписанию)
    """
    before = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)

    # Находим старые результаты
    old_results = db.query(models.TestResult).filter(models.TestResult.timestamp < before).all()

    deleted_count = len(old_results)

    # Удаляем скриншоты
    for result in old_results:
        if result.screenshot_path and os.path.exists(result.screenshot_path):
            try:
                os.remove(result.screenshot_path)
            except Exception:
                pass

    # Удаляем из БД
    db.query(models.TestResult).filter(models.TestResult.timestamp < before).delete()

    db.commit()

    return {"status": "cleaned", "deleted_count": deleted_count, "older_than_days": days}
