from __future__ import annotations

"""Generic CRUD repository for reflected SQLAlchemy Tables.

Why Table-based?
- You asked to keep the model as a reflected ``Table(...autoload_with=engine...)``.
- We also want to support dynamic schemas (schema name comes from the API).

This repository keeps things intentionally small: list, get, create, update, delete.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple
import logging

import sqlalchemy as sa
from sqlalchemy.engine import Engine


@dataclass(frozen=True)
class Page:
    items: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int


class GenericCrudRepository:
    def __init__(self, engine: Engine):
        self.engine = engine
        self._table_cache: Dict[Tuple[str, str], sa.Table] = {}

    def get_table(self, table_name: str, schema: str) -> sa.Table:
        key = (schema, table_name)
        if key in self._table_cache:
            return self._table_cache[key]

        metadata = sa.MetaData()
        log = logging.getLogger(__name__)
        try:
            table = sa.Table(table_name, metadata, schema=schema, autoload_with=self.engine)
        except Exception:
            log.exception(
                "Failed to reflect table",
                extra={"schema": schema, "table_name": table_name},
            )
            raise
        self._table_cache[key] = table
        return table

    def list(
        self,
        table: sa.Table,
        *,
        filters: Optional[Iterable[sa.ColumnElement[bool]]] = None,
        order_by: Optional[List[sa.ClauseElement]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page:
        filters = list(filters or [])
        order_by = order_by or [table.c.created_at.desc()] if hasattr(table.c, "created_at") else []

        where_clause = sa.and_(*filters) if filters else sa.true()
        base_stmt = sa.select(table).where(where_clause)

        if order_by:
            base_stmt = base_stmt.order_by(*order_by)

        count_stmt = sa.select(sa.func.count()).select_from(table).where(where_clause)

        log = logging.getLogger(__name__)
        try:
            with self.engine.connect() as conn:
                total = int(conn.execute(count_stmt).scalar() or 0)
                rows = conn.execute(base_stmt.limit(limit).offset(offset)).mappings().all()
        except Exception:
            log.exception("DB query failed", extra={"limit": limit, "offset": offset})
            raise

        return Page(items=[dict(r) for r in rows], total=total, limit=limit, offset=offset)

    def get_by_id(self, table: sa.Table, id_value: Any) -> Optional[Dict[str, Any]]:
        pk = list(table.primary_key.columns)
        if len(pk) != 1:
            raise ValueError("Table must have exactly one primary key column")
        stmt = sa.select(table).where(pk[0] == id_value)
        with self.engine.connect() as conn:
            row = conn.execute(stmt).mappings().first()
        return dict(row) if row else None

    def create(self, table: sa.Table, data: Dict[str, Any]) -> Dict[str, Any]:
        stmt = table.insert().values(**data).returning(*table.c)
        with self.engine.begin() as conn:
            row = conn.execute(stmt).mappings().first()
        if not row:
            raise RuntimeError("Insert failed")
        return dict(row)

    def update(self, table: sa.Table, id_value: Any, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pk = list(table.primary_key.columns)
        if len(pk) != 1:
            raise ValueError("Table must have exactly one primary key column")
        stmt = (
            table.update()
            .where(pk[0] == id_value)
            .values(**data)
            .returning(*table.c)
        )
        with self.engine.begin() as conn:
            row = conn.execute(stmt).mappings().first()
        return dict(row) if row else None

    def delete(self, table: sa.Table, id_value: Any) -> bool:
        pk = list(table.primary_key.columns)
        if len(pk) != 1:
            raise ValueError("Table must have exactly one primary key column")
        stmt = table.delete().where(pk[0] == id_value)
        with self.engine.begin() as conn:
            res = conn.execute(stmt)
        return (res.rowcount or 0) > 0
