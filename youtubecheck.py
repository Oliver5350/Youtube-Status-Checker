import pandas as pd
import requests
import time

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

def process_youtube_links(file_path, sheet_name="Sheet1", url_column="YouTube Link", status_column="Status"):
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")

    if status_column not in df.columns:
        df[status_column] = ""

    total_links = len(df)

    for index, row in df.iterrows():
        url = row[url_column]
        current_status = row.get(status_column)

        if pd.isna(current_status) or current_status == "":
            print(f"Checking {index + 1}/{total_links}: {url}")
            status = check_youtube_status(url)
            df.at[index, status_column] = status
            time.sleep(2)  # avoid blocking

    return df
