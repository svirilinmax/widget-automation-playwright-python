import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from .routers import results, tests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Создаем таблицы
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")

app = FastAPI(title="Widget Test Runner", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tests.router)
app.include_router(results.router)

if os.path.exists(STATIC_DIR):
    print(f"Mounting static files from: {STATIC_DIR}")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print(f"ERROR: Static directory NOT FOUND at {STATIC_DIR}")


@app.get("/")
async def root():
    return {"message": "Widget Test Runner API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
