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
import json
from functools import lru_cache

import boto3

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

    # Preferred: load credentials from AWS Secrets Manager.
    secret_id = os.getenv("DB_SECRET_ARN")
    if secret_id:
        try:
            creds = _read_db_secret(secret_id)
            host = creds.get("host")
            port = str(creds.get("port")) if creds.get("port") is not None else None
            name = creds.get("dbname") or creds.get("database")
            user = creds.get("username") or creds.get("user")
            password = creds.get("password")
            if all([host, port, name, user, password]):
                return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"
        except Exception:
            # Fall back to env vars below (do not crash during import).
            logging.getLogger(__name__).exception("Failed to load DB secret")

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if all([host, port, name, user, password]):
        return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"

    return "sqlite+pysqlite:///:memory:"


@lru_cache(maxsize=2)
def _read_db_secret(secret_id: str) -> dict:
    """Read and cache a Secrets Manager JSON secret."""
    sm = boto3.client("secretsmanager")
    resp = sm.get_secret_value(SecretId=secret_id)
    s = resp.get("SecretString")
    if not s:
        raise ValueError("SecretString is empty")
    obj = json.loads(s)
    if not isinstance(obj, dict):
        raise ValueError("Secret JSON must be an object")
    # Normalize keys to lower-case for flexibility
    return {str(k).lower(): v for k, v in obj.items()}


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
