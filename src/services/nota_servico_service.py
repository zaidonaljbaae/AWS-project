# src/services/nota_servico_service.py

from typing import Dict, Any, Optional, List

from ..repositories.generic_crud_repository import GenericCrudRepository


ALLOWED_SCHEMAS = {"bmw", "fiat"} 


class NotaServicoService:
    TABLE_NAME = "nota_servico"

    def __init__(self, repo: Optional[GenericCrudRepository] = None):
        self.repo = repo or GenericCrudRepository()

    def list(
        self,
        schema: str,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if schema not in ALLOWED_SCHEMAS:
            raise ValueError(f"invalid schema: {schema}")

        return self.repo.list(
            table_name=self.TABLE_NAME,
            schema=schema,
            limit=limit,
            offset=offset,
            filters=filters or {}
        )
