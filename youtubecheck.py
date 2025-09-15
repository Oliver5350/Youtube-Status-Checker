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

def process_youtube_links_with_progress(file_path, sheet_name=0, status_column="Status"):
    global progress_data

    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
