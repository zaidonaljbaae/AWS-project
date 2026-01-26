from __future__ import annotations

from typing import Any, Dict, Optional
import re

import sqlalchemy as sa

from ..common.conexao_banco import get_engine
from ..repositories.generic_crud_repository import GenericCrudRepository, Page


SCHEMA_REGEX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class NotaServicoService:
    TABLE_NAME = "nota_servico"

    def __init__(self, repo: Optional[GenericCrudRepository] = None):
        engine = get_engine()
        self.repo = repo or GenericCrudRepository(engine)

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
        table = self.repo.get_table(
            table_name=self.TABLE_NAME,
            schema=schema,
        )

        # Build WHERE filters safely
        where_filters = []
        for key, value in (filters or {}).items():
            if key not in table.c:
                raise ValueError(f"invalid filter column: {key}")
            where_filters.append(table.c[key] == value)

        # Delegate to repository
        return self.repo.list(
            table,
            filters=where_filters,
            limit=limit,
            offset=offset,
        )
