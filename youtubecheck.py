import pandas as pd
import requests
import time

# Shared progress data
progress_data = {"total": 0, "done": 0}

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
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

    if status_column not in df.columns:
        df[status_column] = ""

    total_links = len(df)
    progress_data = {"total": total_links, "done": 0}

    for index, row in df.iterrows():
        url = row[url_column]
        status = check_youtube_status(url)
        df.at[index, status_column] = status

        # Update progress
        progress_data["done"] += 1

        time.sleep(0.3)  # small delay to avoid blocking too fast

    return df
