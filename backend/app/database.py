"""Database wiring: engine, session factory, ORM base class, and the get_db dependency."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL

# The engine owns the connection pool to Postgres. Create it once per app.
engine = create_engine(DATABASE_URL)

# A factory that hands out new Session objects (one per request).
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Every ORM model inherits from this. Base.metadata knows about all tables."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: open a session for the request, always close it afterwards."""
    db = SessionLocal()
    try:
        yield db  # <- the route function runs while we are paused here
    finally:
        db.close()


# Shortcut type: writing `db: DbSession` in a route = "inject a Session from get_db".
DbSession = Annotated[Session, Depends(get_db)]
