import time
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/health")
def health():
    app.logger.info("ecs_test health hit")
    return jsonify(ok=True, service="ecs_test")

@app.get("/long-task")
def long_task():
    seconds = int(request.args.get("seconds", "60"))
    seconds = max(1, min(seconds, 1800))
    app.logger.info("ecs_test long-task start seconds=%s", seconds)
    time.sleep(seconds)
    app.logger.info("ecs_test long-task done seconds=%s", seconds)
    return jsonify(done=True, slept=seconds)
