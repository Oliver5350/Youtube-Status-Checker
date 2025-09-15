import pandas as pd
import requests
import time
from threading import Lock

# Shared progress data with thread safety
progress_data = {"total": 0, "done": 0, "error": None}
progress_lock = Lock()

def check_youtube_status(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text.lower()
            if "this video is private" in content:
                return "Private"
            elif "video unavailable" in content or "this video is no longer available" in content:
                return "Removed"
            elif "this channel does not exist" in content:
                return "Inactive"
            else:
                return "Active"
        else:
            return "Inactive"
    except Exception:
        return "Inactive"

def process_youtube_links_with_progress(file_path, sheet_name="Sheet1", url_column="YouTube Link", status_column="Status"):
    global progress_data

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
    except Exception as e:
        with progress_lock:
            progress_data["error"] = f"❌ Could not read Excel: {e}"
        return None

    if url_column not in df.columns:
        with progress_lock:
            progress_data["error"] = f"❌ Column '{url_column}' not found in Excel."
        return None

    if status_column not in df.columns:
        df[status_column] = ""

    total_links = len(df)

    with progress_lock:
        progress_data = {"total": total_links, "done": 0, "error": None}

    for index, row in df.iterrows():
        url = row[url_column]
        status = check_youtube_status(url)
        df.at[index, status_column] = status

        with progress_lock:
            progress_data["done"] += 1

        time.sleep(0.3)  # tweak if needed

    return df
