from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from flask import Flask, request, jsonify
import serverless_wsgi

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
