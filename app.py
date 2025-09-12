import os
from flask import Flask, request, render_template, send_file
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

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        try:
            # Process links
            result_df = process_youtube_links(filepath)

            # Save output
            output_path = os.path.join(app.config["OUTPUT_FOLDER"], "result.xlsx")
            result_df.to_excel(output_path, index=False, engine="openpyxl")

            return send_file(output_path, as_attachment=True)

        except Exception as e:
            print(f"❌ Error: {e}")
            error_message = "The uploaded file is corrupted or not supported. Please upload a valid Excel file (.xlsx)."
            return render_template("index.html", error=error_message)

    return render_template("index.html", error=error_message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
