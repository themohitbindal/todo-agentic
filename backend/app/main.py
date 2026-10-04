"""App entry point. Run with:  uvicorn app.main:app --reload  (from the backend folder)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers the tables on Base.metadata)
from app.config import CORS_ORIGINS
from app.database import Base, engine
from app.routers import todos


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once on startup. Creates missing tables.
    # (Phase 3 replaces this with Alembic migrations.)
    Base.metadata.create_all(bind=engine)
    yield
    # Code after `yield` runs once on shutdown.


app = FastAPI(title="Todo API", version="0.1.0", lifespan=lifespan)

# Browser security: allow the React dev server (another origin) to call us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todos.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
