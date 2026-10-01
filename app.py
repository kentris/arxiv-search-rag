from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "https://kentris.github.io",
                "http://localhost:5000",
                "http://127.0.0.1:5000"
            ]
        }
    }
)


@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Backend is running"
    })


@app.get("/api/hello")
def hello():
    return jsonify({
        "message": "Hello from Flask!"
    })


@app.post("/api/example")
def example():
    data = request.get_json()

    return jsonify({
        "received": data
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
