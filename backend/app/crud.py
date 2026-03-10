from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


# TestRun CRUD
def create_test_run(db: Session, test_run: schemas.TestRunCreate) -> models.TestRun:
    db_test_run = models.TestRun(**test_run.model_dump())
    db.add(db_test_run)
    db.commit()
    db.refresh(db_test_run)
    return db_test_run


def get_test_run(db: Session, test_run_id: int) -> Optional[models.TestRun]:
    stmt = select(models.TestRun).where(models.TestRun.id == test_run_id)
    return db.execute(stmt).scalar_one_or_none()


def get_test_runs(db: Session, skip: int = 0, limit: int = 100) -> List[models.TestRun]:
    stmt = select(models.TestRun).order_by(models.TestRun.started_at.desc()).offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def update_test_run(db: Session, test_run_id: int, **kwargs) -> Optional[models.TestRun]:
    db_test_run = get_test_run(db, test_run_id)
    if db_test_run:
        for key, value in kwargs.items():
            setattr(db_test_run, key, value)
        db.commit()
        db.refresh(db_test_run)
    return db_test_run


def delete_test_run(db: Session, test_run_id: int) -> bool:
    db_test_run = get_test_run(db, test_run_id)
    if db_test_run:
        db.delete(db_test_run)
        db.commit()
        return True
    return False


# TestResult CRUD
def create_test_result(db: Session, result: schemas.TestResultCreate) -> models.TestResult:
    db_result = models.TestResult(**result.model_dump())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def get_test_results(db: Session, test_run_id: int) -> List[models.TestResult]:
    return db.query(models.TestResult).filter(models.TestResult.test_run_id == test_run_id).all()


def get_recent_test_results(db: Session, limit: int = 50) -> List[models.TestResult]:
    return db.query(models.TestResult).order_by(models.TestResult.timestamp.desc()).limit(limit).all()
