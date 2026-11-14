
import os
import cv2
import tempfile
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cricket Video Analyzer</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    background: #101827;
    color: white;
    font-family: Arial, sans-serif;
    padding: 20px;
}
.container {
    max-width: 600px;
    margin: 35px auto;
    padding: 25px;
    background: #1e293b;
    border-radius: 18px;
    text-align: center;
}
h1 { color: #38bdf8; }
input {
    width: 100%;
    margin: 20px 0;
}
button {
    background: #22c55e;
    color: white;
    padding: 15px 25px;
    border: none;
    border-radius: 10px;
    font-size: 17px;
    cursor: pointer;
}
button:disabled { opacity: 0.5; }
video {
    width: 100%;
    margin-top: 20px;
    border-radius: 10px;
}
#result {
    margin-top: 20px;
    text-align: left;
    line-height: 1.8;
}
</style>
</head>
<body>
<div class="container">
<h1>🏏 Cricket Video Analyzer</h1>
<p>Upload your cricket video for basic analysis</p>

<input type="file" id="videoFile" accept="video/*">

<video id="preview" controls style="display:none"></video>

<button id="analyzeBtn" onclick="analyzeVideo()">
Analyze Video
</button>

<div id="result"></div>
</div>

<script>
const fileInput = document.getElementById("videoFile");
const preview = document.getElementById("preview");
const result = document.getElementById("result");
const button = document.getElementById("analyzeBtn");

fileInput.addEventListener("change", function() {
    const file = this.files[0];
    if (!file) return;
    if (preview.src.startsWith("blob:")) {
        URL.revokeObjectURL(preview.src);
    }
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
    result.textContent = "";
});

async function analyzeVideo() {
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a cricket video");
        return;
    }

    const formData = new FormData();
    formData.append("video", file);

    button.disabled = true;
    result.textContent = "Analyzing video...";

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            result.textContent = data.error || "Analysis failed";
            return;
        }

        result.innerHTML = `
            <h3>Analysis Results</h3>
            <p>Duration: ${data.duration} seconds</p>
            <p>FPS: ${data.fps}</p>
            <p>Resolution: ${data.resolution}</p>
            <p>Total Frames: ${data.total_frames}</p>
            <p>Frames Sampled: ${data.frames_sampled}</p>
            <p>Average Motion Score: ${data.motion_score}</p>
            <p>${data.message}</p>
        `;
    } catch (error) {
        result.textContent = "Unable to analyze video.";
    } finally {
        button.disabled = false;
    }
}
</script>
</body>
</html>
"""

@app.get("/")
def home():
    return HTML, 200, {"Content-Type": "text/html; charset=utf-8"}

@app.post("/analyze")
def analyze():
    if "video" not in request.files:
        return jsonify({"error": "No video uploaded"}), 400

    video = request.files["video"]

    if not video.filename:
        return jsonify({"error": "Select a video"}), 400

    filename = secure_filename(video.filename)
    extension = os.path.splitext(filename)[1].lower()

    if extension not in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        return jsonify({"error": "Unsupported video format"}), 400

    path = None
    cap = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=extension, delete=False
        ) as temp:
            path = temp.name
            video.save(temp)

        cap = cv2.VideoCapture(path)

        if not cap.isOpened():
            return jsonify({"error": "Cannot read video"}), 400

        fps = cap.get(cv2.CAP_PROP_FPS)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if fps <= 0 or total <= 0:
            return jsonify({"error": "Invalid video metadata"}), 400

        duration = total / fps

        previous = None
        motion_scores = []
        sampled = 0

        step = max(1, total // 100)

        for index in range(0, total, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            success, frame = cap.read()

            if not success:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (160, 90))
            gray = cv2.GaussianBlur(gray, (5, 5), 0)

            if previous is not None:
                difference = cv2.absdiff(previous, gray)
                motion_scores.append(float(difference.mean()))

            previous = gray
            sampled += 1

            if sampled >= 100:
                break

        motion = (
            sum(motion_scores) / len(motion_scores)
            if motion_scores else 0
        )

        return jsonify({
            "status": "success",
            "duration": round(duration, 2),
            "fps": round(fps, 2),
            "resolution": f"{width} x {height}",
            "total_frames": total,
            "frames_sampled": sampled,
            "motion_score": round(motion, 2),
            "message": "Basic video analysis completed successfully."
        })

    except Exception:
        app.logger.exception("Video analysis failed")
        return jsonify({"error": "Video processing failed"}), 500

    finally:
        if cap is not None:
            cap.release()
        if path and os.path.exists(path):
            os.remove(path)


@app.errorhandler(413)
def too_large(error):
    return jsonify({"error": "Maximum video size is 50 MB"}), 413


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
