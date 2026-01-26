from __future__ import annotations

"""
Database connection helper.

- Uses PostgreSQL when DB_* env vars are provided
- Falls back to SQLite (memory) for local/dev
- Safe for AWS Lambda (low pool size)
"""

import os
from contextlib import contextmanager
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

_ENGINE: Optional[sa.Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _build_db_url() -> str:
    """
    Build DB URL from environment variables.
    """
    db_url = os.getenv("DB_URL")
    if db_url:
        return db_url

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if all([host, port, name, user, password]):
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

    return "sqlite+pysqlite:///:memory:"


def get_engine() -> sa.Engine:
    """
    Return a singleton SQLAlchemy Engine.
    """
    global _ENGINE, _SessionLocal

    if _ENGINE is not None:
        return _ENGINE

    db_url = _build_db_url()

    kwargs = {
        "pool_pre_ping": True,
    }

    if not db_url.startswith("sqlite"):
        kwargs.update(
            pool_size=int(os.getenv("DB_POOL_SIZE", "2")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "2")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "300")),
        )

    _ENGINE = sa.create_engine(db_url, **kwargs)
    _SessionLocal = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False)

    return _ENGINE


@contextmanager
def get_session():
    """
    SQLAlchemy session context manager.
    """
    global _SessionLocal

    if _SessionLocal is None:
        get_engine()

    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
