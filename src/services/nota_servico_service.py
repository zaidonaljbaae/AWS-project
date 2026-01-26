from __future__ import annotations

from typing import Any, Dict, Optional
import re
import logging

import sqlalchemy as sa

from ..common.conexao_banco import get_engine
from ..repositories.generic_crud_repository import GenericCrudRepository, Page


SCHEMA_REGEX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class NotaServicoService:
    TABLE_NAME = "nota_servico"

    def __init__(self, repo: Optional[GenericCrudRepository] = None):
        engine = get_engine()
        self.repo = repo or GenericCrudRepository(engine)
        self._log = logging.getLogger(__name__)

    def list(
        self,
        schema: str,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Page:
        """
        List records from nota_servico in a dynamic schema.
        """

        # 🔐 Security: validate schema name
        if not SCHEMA_REGEX.match(schema):
            raise ValueError(f"invalid schema name: {schema}")

        # Reflect table dynamically
        try:
            table = self.repo.get_table(table_name=self.TABLE_NAME, schema=schema)
        except Exception:
            self._log.exception("Failed reflecting table", extra={"schema": schema, "table": self.TABLE_NAME})
            raise

        # Build WHERE filters safely
        where_filters = []
        for key, value in (filters or {}).items():
            if key not in table.c:
                raise ValueError(f"invalid filter column: {key}")
            where_filters.append(table.c[key] == value)

        # Delegate to repository
        try:
            return self.repo.list(table, filters=where_filters, limit=limit, offset=offset)
        except Exception:
            self._log.exception(
                "DB query failed",
                extra={"schema": schema, "table": self.TABLE_NAME, "limit": limit, "offset": offset},
            )
            raise
