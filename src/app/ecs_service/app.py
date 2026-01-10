from flask import Flask, Response

app = Flask(__name__)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return Response(
        "\n".join(str(i) for i in range(1, 101)) + "\n",
        mimetype="text/plain",
    )
