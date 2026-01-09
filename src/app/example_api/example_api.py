from __future__ import annotations

from flask import Flask, request, jsonify
import serverless_wsgi

from common.conexao_banco import get_session
from services.example_api_service import ExampleApiService
from common.authorization import get_current_user
from common.s3_helper import put_text_object, list_objects

app = Flask(__name__)
ROUTE_PREFIX = "/example_api"


@app.get(ROUTE_PREFIX + "/public/health")
def public_health():
    print("[example_api] public health hit")
    return jsonify(ok=True, auth="none", route="public/health")


@app.get(ROUTE_PREFIX + "/public/items")
def public_list_items():
    limit = int(request.args.get("limit", "20"))
    with get_session() as session:
        items = ExampleApiService(session).list_items(limit=limit)
        return jsonify(ok=True, items=[{"id": i.id, "name": i.name} for i in items])


@app.post(ROUTE_PREFIX + "/public/items")
def public_create_item():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return jsonify(ok=False, error="name is required"), 400

    with get_session() as session:
        item = ExampleApiService(session).create_item(name=name)
        print(f"[example_api] created item id={item.id}")
        return jsonify(ok=True, item={"id": item.id, "name": item.name})


@app.post(ROUTE_PREFIX + "/public/s3/put")
def public_s3_put():
    payload = request.get_json(silent=True) or {}
    key = (payload.get("key") or "tests/hello.txt").strip()
    body = payload.get("body") or "hello from lambda"
    put_text_object(key, body)
    print(f"[example_api] s3 put key={key}")
    return jsonify(ok=True, key=key)


@app.get(ROUTE_PREFIX + "/public/s3/list")
def public_s3_list():
    prefix = request.args.get("prefix", "")
    keys = list_objects(prefix=prefix, limit=20)
    return jsonify(ok=True, keys=keys)


@app.get(ROUTE_PREFIX + "/private/me")
def private_me():
    user = get_current_user()
    print("[example_api] private/me hit - user:", user)
    return jsonify(ok=True, auth="cognito", user=user)


def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
