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
import logging

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

    kwargs: dict = {"pool_pre_ping": True}

    # Fast-fail DB connects so Lambda doesn't hit its own timeout.
    connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "3"))
    connect_args = {}
    if not db_url.startswith("sqlite"):
        # psycopg2 uses 'connect_timeout' (seconds)
        connect_args["connect_timeout"] = connect_timeout
        kwargs["connect_args"] = connect_args

    if not db_url.startswith("sqlite"):
        kwargs.update(
            pool_size=int(os.getenv("DB_POOL_SIZE", "2")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "2")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "300")),
        )

    log = logging.getLogger(__name__)
    try:
        _ENGINE = sa.create_engine(db_url, **kwargs)
    except Exception:
        # Do not leak secrets in logs.
        safe_url = db_url
        if "@" in safe_url and ":" in safe_url.split("@", 1)[0]:
            creds, rest = safe_url.split("@", 1)
            safe_url = "***@" + rest
        log.exception("Failed to create SQLAlchemy engine", extra={"db_url": safe_url})
        raise
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
