# src/app/example_api/example_api.py
from __future__ import annotations

from datetime import datetime, timezone
import logging
import os

from flask import Flask, request, jsonify
import serverless_wsgi

from ...services.nota_servico_service import NotaServicoService
from ...common.authorization import authenticate

# -----------------------------------------------------------------------------
# App configuration
# -----------------------------------------------------------------------------

ROUTE_PREFIX = "/api"

app = Flask(__name__)
nota_servico_service = NotaServicoService()

# Ensure logs show up in CloudWatch with a predictable level.
logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))

authenticate(app)

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def now_iso() -> str:
    """Return current UTC time in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.get(f"{ROUTE_PREFIX}/nota-servico")
def list_nota_servico():
    schema = request.args.get("schema", "public")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    try:
        page = nota_servico_service.list(schema=schema, limit=limit, offset=offset)
        return jsonify(
            {
                "schema": schema,
                "count": len(page.items),
                "total": page.total,
                "limit": page.limit,
                "offset": page.offset,
                "items": page.items,
            }
        ), 200
    except Exception as exc:
        app.logger.exception(
            "Failed to list nota_servico",
            extra={
                "schema": schema,
                "limit": limit,
                "offset": offset,
                "query_string": request.query_string.decode("utf-8", errors="ignore"),
            },
        )
        return jsonify({"error": str(exc)}), 500


@app.get(f"{ROUTE_PREFIX}/health")
def health():
    return jsonify(ok=True, service="example_api", at=now_iso())


# -----------------------------------------------------------------------------
# AWS Lambda entrypoint
# -----------------------------------------------------------------------------

def handler(event, context):
    """AWS Lambda entrypoint."""
    return serverless_wsgi.handle_request(app, event, context)
