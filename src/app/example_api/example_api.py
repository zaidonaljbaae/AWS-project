from __future__ import annotations

"""Flask-based Lambda.

Dependencies for this Lambda are *vendored* under ``src/app/example_api/vendor``
by the CI/CD build (see ``pipeline/buildspec-serverless.yml``).

AWS Lambda imports this module directly (the handler points here). That means
we must add ``vendor/`` to ``sys.path`` *before* importing third-party libs like
Flask.
"""

import json
import os
import sys
from datetime import datetime, timezone


def _add_vendor_to_path() -> None:
    here = os.path.dirname(__file__)
    vendor = os.path.join(here, "vendor")
    if os.path.isdir(vendor) and vendor not in sys.path:
        sys.path.insert(0, vendor)


_add_vendor_to_path()

from flask import Flask, request, jsonify  # noqa: E402
import serverless_wsgi  # noqa: E402

app = Flask(__name__)
ROUTE_PREFIX = "/api"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_request_context() -> dict:
    """Return a small, safe context snapshot (no secrets)."""
    return {
        "method": request.method,
        "path": request.path,
        "query": request.args.to_dict(flat=True),
        "headers": {
            # keep only a few useful headers
            "user-agent": request.headers.get("user-agent"),
            "x-forwarded-for": request.headers.get("x-forwarded-for"),
            "x-forwarded-proto": request.headers.get("x-forwarded-proto"),
        },
        "stage": os.getenv("STAGE", "dev"),
        "timestamp": _now_iso(),
    }


@app.get(ROUTE_PREFIX + "/health")
def health():
    print("[example_api] health hit")
    return jsonify(ok=True, service="example_api", at=_now_iso())


@app.route(ROUTE_PREFIX + "/echo", methods=["GET", "POST"]) 
def echo():
    payload = request.get_json(silent=True)
    ctx = _get_request_context()
    print("[example_api] echo", json.dumps({"ctx": ctx, "payload": payload})[:2000])
    return jsonify(ok=True, ctx=ctx, payload=payload)


@app.get(ROUTE_PREFIX + "/private/me")
def private_me():
    # This is a *placeholder* auth example.
    # In production, add a JWT authorizer in API Gateway (HTTP API) or validate tokens here.
    auth = request.headers.get("authorization")
    user = {
        "authenticated": bool(auth),
        "note": "template endpoint - integrate Cognito/JWT authorizer in production",
    }
    print("[example_api] private/me hit - auth_present:", bool(auth))
    return jsonify(ok=True, user=user, ctx=_get_request_context())


def handler(event, context):
    """AWS Lambda entrypoint."""
    return serverless_wsgi.handle_request(app, event, context)
