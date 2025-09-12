import os
import time
import uuid
from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
from youtubecheck import process_youtube_links

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Log storage (could later be replaced with DB)
file_records = []

@app.route("/", methods=["GET", "POST"])
def index():
    error_message = None
    if request.method == "POST":
        if "file" not in request.files:
            error_message = "No file uploaded!"
            return render_template("index.html", error=error_message)

        file = request.files["file"]
        if file.filename == "":
            error_message = "No file selected!"
            return render_template("index.html", error=error_message)

        # Generate unique names
        filename = secure_filename(file.filename)
        unique_name = f"{int(time.time())}_{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        file.save(filepath)

        try:
            # Process links
            result_df = process_youtube_links(filepath)

            # Save unique output
            output_name = f"result_{unique_name}"
            output_path = os.path.join(app.config["OUTPUT_FOLDER"], output_name)
            result_df.to_excel(output_path, index=False, engine="openpyxl")

            # Log it
            file_records.append({
                "upload": unique_name,
                "output": output_name,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            print(f"❌ Error: {e}")
            error_message = "The uploaded file is corrupted or not supported. Please upload a valid Excel file (.xlsx)."
            return render_template("index.html", error=error_message)

    return render_template("index.html", error=error_message)


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", records=file_records)


@app.route("/download/<path:filename>")
def download(filename):
    # Check both folders
    if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
        return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)
    elif os.path.exists(os.path.join(OUTPUT_FOLDER, filename)):
        return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)
    else:
        return "File not found!", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
