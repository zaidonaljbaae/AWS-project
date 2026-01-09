# from __future__ import annotations

# import os
# from contextlib import contextmanager
# from typing import Dict, Optional

# import sqlalchemy as sa
# from sqlalchemy.orm import sessionmaker

# from .secrets_manager import get_secret

# _ENGINE: Optional[sa.Engine] = None
# _SessionLocal: Optional[sessionmaker] = None


# def _load_db_secret() -> Dict[str, str]:
#     """Reads DB credentials from Secrets Manager.

#     Expected secret JSON keys (RDS default):
#       - username
#       - password
#       - host
#       - port (optional)
#       - dbname (optional)
#     """
#     secret_arn = os.getenv("DB_SECRET_ARN")
#     if not secret_arn:
#         raise RuntimeError("DB_SECRET_ARN is not set")
#     return get_secret(secret_arn)


# def _build_engine() -> sa.Engine:
#     secret = _load_db_secret()
#     user = secret.get("username") or secret.get("user") or "postgres"
#     pwd = secret["password"]
#     host = secret["host"]
#     port = int(str(secret.get("port", "5432")))
#     dbname = os.getenv("DB_NAME") or secret.get("dbname") or "postgres"

#     url = sa.engine.URL.create(
#         drivername="postgresql+psycopg2",
#         username=user,
#         password=pwd,
#         host=host,
#         port=port,
#         database=dbname,
#     )

#     # Lambda: keep pool small; ECS: override via env if needed.
#     pool_size = int(os.getenv("DB_POOL_SIZE", "2"))
#     max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "2"))
#     pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "300"))

#     return sa.create_engine(
#         url,
#         pool_size=pool_size,
#         max_overflow=max_overflow,
#         pool_recycle=pool_recycle,
#         pool_pre_ping=True,
#         connect_args={"sslmode": "require"},
#     )


# def get_engine() -> sa.Engine:
#     global _ENGINE, _SessionLocal
#     if _ENGINE is None:
#         _ENGINE = _build_engine()
#         _SessionLocal = sessionmaker(bind=_ENGINE, autoflush=False, autocommit=False)
#     return _ENGINE


# @contextmanager
# def get_session():
#     """SQLAlchemy session context manager."""
#     global _SessionLocal
#     if _SessionLocal is None:
#         get_engine()
#     session = _SessionLocal()  # type: ignore[misc]
#     try:
#         yield session
#         session.commit()
#     except Exception:
#         session.rollback()
#         raise
#     finally:
#         session.close()

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

_ENGINE: Optional[sa.Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def _required_env(name: str) -> str:
    """Fetch required env var with a clear error."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is not set")
    return value


def _build_engine() -> sa.Engine:
    # --- Read DB connection settings from ENV ---
    user = os.getenv("DB_USER", "postgres")
    pwd = _required_env("DB_PASSWORD")
    host = _required_env("DB_HOST")
    port = int(os.getenv("DB_PORT", "5432"))
    dbname = os.getenv("DB_NAME", "postgres")

    # --- SSL (recommended with RDS) ---
    # Use "require" by default; allow override (e.g. "disable" locally)
    sslmode = os.getenv("DB_SSLMODE", "require")

    url = sa.engine.URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=pwd,
        host=host,
        port=port,
        database=dbname,
    )

    # --- Pooling defaults (Lambda-friendly) ---
    # You can override these in ECS for higher throughput.
    pool_size = int(os.getenv("DB_POOL_SIZE", "2"))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "2"))
    pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "300"))

    return sa.create_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
        pool_pre_ping=True,
        connect_args={"sslmode": sslmode},
    )


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
