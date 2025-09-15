import os
import time
import uuid
from threading import Thread
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
from youtubecheck import process_youtube_links_with_progress, progress_data

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

current_result = None
processing = False

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start_process():
    global current_result, processing

    if "file" not in request.files:
        return "No file uploaded!", 400

    file = request.files["file"]
    if file.filename == "":
        return "No file selected!", 400

    filename = secure_filename(file.filename)
    unique_name = f"{int(time.time())}_{uuid.uuid4().hex}_{filename}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
    file.save(filepath)

    def background_job():
        global current_result, processing
        processing = True
        df = process_youtube_links_with_progress(filepath)
        output_name = f"result_{unique_name}"
        output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_name)
        df.to_excel(output_path, index=False, engine="openpyxl")
        current_result = output_path
        processing = False

    Thread(target=background_job).start()
    return "Processing started", 202


@app.route("/progress")
def progress():
    return jsonify(progress_data)


@app.route("/download")
def download_result():
    if current_result and os.path.exists(current_result):
        return send_file(current_result, as_attachment=True)
    return "No result available yet", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
