
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "message": "Cricket AI Backend Running"
    })

@app.post("/analyze")
def analyze():
    if "video" not in request.files:
        return jsonify({
            "error": "No video uploaded"
        }), 400

    video = request.files["video"]

    if not video.filename:
        return jsonify({
            "error": "Select a video"
        }), 400

    return jsonify({
        "status": "received",
        "analysis": "Video received successfully. AI analysis is not configured yet."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
