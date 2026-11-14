
import os
import cv2
import tempfile
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cricket Video Analyzer</title>
<style>
body {
    background: #101827;
    color: white;
    font-family: Arial;
    text-align: center;
    padding: 20px;
}
.card {
    background: #202d42;
    padding: 25px;
    border-radius: 15px;
}
button {
    background: #00c853;
    padding: 14px;
    border: none;
    border-radius: 8px;
    font-size: 18px;
}
</style>
</head>
<body>
<div class="card">
<h1>🏏 Cricket Video Analyzer</h1>
<p>Upload your cricket video</p>
<form method="POST" enctype="multipart/form-data">
<input type="file" name="video" accept="video/*" required>
<br><br>
<button type="submit">Analyze Video</button>
</form>
<h3>{{ result }}</h3>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    result = ""
    if request.method == "POST":
        video = request.files.get("video")
        if not video or not video.filename:
            result = "Please select a video."
        else:
            path = None
            try:
                with tempfile.NamedTemporaryFile(
                    suffix=".mp4", delete=False
                ) as temp:
                    path = temp.name
                    video.save(temp)

                cap = cv2.VideoCapture(path)
                if cap.isOpened():
                    frames = int(
                        cap.get(cv2.CAP_PROP_FRAME_COUNT)
                    )
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    duration = frames / fps if fps > 0 else 0
                    result = (
                        f"Video uploaded successfully! "
                        f"Duration: {duration:.1f} seconds. "
                        f"Total frames: {frames}"
                    )
                else:
                    result = "Unable to read video."
                cap.release()
            except Exception:
                result = "Video processing failed."
            finally:
                if path and os.path.exists(path):
                    os.remove(path)

    return render_template_string(HTML, result=result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
