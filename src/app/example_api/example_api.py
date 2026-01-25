# src/app/example_api/example_api.py

from flask import Blueprint, request, jsonify

from ...services.nota_servico_service import NotaServicoService

bp = Blueprint("example_api", __name__)

nota_servico_service = NotaServicoService()


@bp.get("/api/nota-servico")
def list_nota_servico():

    schema = request.args.get("schema", "nota_avulsa")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

    if schema not in {"nota_avulsa", "nota_fiscal"}:
        return jsonify({"error": "invalid schema"}), 400

    try:
        items = nota_servico_service.list(schema=schema, limit=limit, offset=offset)
        return jsonify({"schema": schema, "count": len(items), "items": items}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
