from __future__ import annotations

"""Database helper (template).

Goal:
- Never crash just because DB env vars are missing.
- Provide a clean upgrade path to real DBs (RDS/Aurora).

How it works:
- If DB_URL env var is set, SQLAlchemy uses it.
- Otherwise, it falls back to SQLite in-memory (useful for local dev/tests).

Example DB_URL:
  postgresql+psycopg2://USER:PASSWORD@HOST:5432/DBNAME
"""

import os
from contextlib import contextmanager
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

_ENGINE: Optional[sa.Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _build_engine() -> sa.Engine:
    db_url = os.getenv("DB_URL", "").strip()

    if not db_url:
        # Safe default: in-memory DB (no external dependencies)
        db_url = "sqlite+pysqlite:///:memory:"

    # Pooling defaults (Lambda-friendly). Override in ECS when needed.
    pool_size = int(os.getenv("DB_POOL_SIZE", "2"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "2"))
    pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "300"))

    # SQLite doesn't support pool_size/max_overflow the same way; SQLAlchemy handles it,
    # but we keep settings only for non-sqlite connections.
    kwargs = {
        "pool_pre_ping": True,
    }

    if not db_url.startswith("sqlite"):
        kwargs.update(
            {
                "pool_size": pool_size,
                "max_overflow": max_overflow,
                "pool_recycle": pool_recycle,
            }
        )

    return sa.create_engine(db_url, **kwargs)


def get_engine() -> sa.Engine:
    global _ENGINE, _SessionLocal
    if _ENGINE is None:
        _ENGINE = _build_engine()
        _SessionLocal = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False)
    return _ENGINE


@contextmanager
def get_session():
    """SQLAlchemy session context manager."""
    global _SessionLocal
    if _SessionLocal is None:
        get_engine()

    session = _SessionLocal()  # type: ignore[misc]
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
