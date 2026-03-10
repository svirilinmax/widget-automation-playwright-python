import logging
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)
logger.info(f"Database directory: {DATA_DIR.absolute()}")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATA_DIR / 'test_runs.db'}"
logger.info(f"Database URL: {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db():
    """Проверка подключения к БД"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1")).fetchall()
        logger.info("Database connection OK")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
