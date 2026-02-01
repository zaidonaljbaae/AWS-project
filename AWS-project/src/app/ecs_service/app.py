"""ECS Fargate service (template).

Endpoints:
- GET /health  -> simple health probe
- GET /        -> returns numbers 1..100 (demo)

Why auth is optional here:
The original template called `common.authorization.get_current_user()` on every
request, but the repository (as provided) does not include the ORM models that
`common.authorization` imports (e.g., `models.schema_public`). That makes the
container crash at startup.

For production:
- keep `ENABLE_AUTH=true` and provide the missing models + DB schema, or
- replace the auth layer with your real one.
"""

import os

from flask import Flask, Response, request

app = Flask(__name__)


def _auth_enabled() -> bool:
    return os.getenv("ENABLE_AUTH", "false").strip().lower() in {"1", "true", "yes"}


def _maybe_auth():
    if not _auth_enabled():
        return
    # Import only when enabled, so the container can start in template mode.
    from common.authorization import get_current_user  # noqa: WPS433 (runtime import)

    if request.path == "/health":
        return
    get_current_user()

@app.before_request
def auth():
    return _maybe_auth()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return Response("\n".join(str(i) for i in range(1, 101)) + "\n", mimetype="text/plain")
