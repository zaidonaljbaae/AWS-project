from flask import Flask, Response, request
from ...common.authorization import get_current_user

app = Flask(__name__)

@app.before_request
def auth():
    if request.path == "/health":
        return
    get_current_user()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return Response("\n".join(str(i) for i in range(1, 101)) + "\n", mimetype="text/plain")
