import logging
import sys
from pathlib import Path

import uvicorn
from app.database import check_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(Path(__file__).parent / "app.log")],
)

logger = logging.getLogger(__name__)

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent.parent))


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Starting Widget Test Runner Backend")
    logger.info("=" * 50)

    if not check_db():
        logger.error("Database check failed. Trying to initialize...")
        from app.database import Base, engine

        Base.metadata.create_all(bind=engine)
        if check_db():
            logger.info("Database initialized successfully")
        else:
            logger.error("Failed to initialize database")

    logger.info("Starting server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, log_level="info")
