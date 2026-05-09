import yt_dlp
import csv
import os
import time
import random

destination_path = "/home/comrade-stu/smb/stuart/Leninka/Audiobooks"  # Replace with your desired output path
input_csv_file = f"{destination_path}/youtubeVideoURLs.txt"  # Replace with your input CSV file path

# Function to download audio (with retries)
def download_audio(url, output_path, filename, max_attempts=4, base_backoff=2.0):
    temp_dir = os.path.join(output_path, ".yt-dlp-tmp")
    os.makedirs(temp_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        # <-- IMPORTANT: keep relative; no absolute path here
        'outtmpl': f'{filename}.%(ext)s',
        'paths': {
            'home': output_path,  # final MP3 goes here
            'temp': temp_dir,     # .part/.ytdl/.frag go here
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '128',  # target spoken word bitrate
        }, {
            # safeguard: don’t re-encode if source bitrate <= target
            'key': 'FFmpegMetadata',
        }],
        'concurrent_fragment_downloads': 8,

        # --- yt-dlp resiliency knobs (minimal additions) ---
        'retries': 10,                   # HTTP retries per request
        'fragment_retries': 10,          # per-fragment retries (HLS/DASH)
        'extractor_retries': 3,          # retries on metadata/extraction
        'socket_timeout': 30,            # seconds
        'skip_unavailable_fragments': True,
        # 'verbose': True,               # optional: to confirm paths/logs
    }

    last_err = None
    for attempt in range(1, max_attempts + 1):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"[OK] ({attempt}/{max_attempts}) {filename}.mp3")
            return
        except yt_dlp.utils.DownloadError as e:
            last_err = e
            print(f"[WARN] DownloadError on attempt {attempt}/{max_attempts} for '{filename}': {e}")
        except Exception as e:
            last_err = e
            print(f"[WARN] Unexpected error on attempt {attempt}/{max_attempts} for '{filename}': {e}")

        # exponential backoff with jitter (except after last attempt)
        if attempt < max_attempts:
            sleep_s = (base_backoff ** (attempt - 1)) + random.uniform(0.0, 0.75)
            print(f"    Retrying in {sleep_s:.2f}s...")
            time.sleep(sleep_s)

    # If we got here, all attempts failed
    raise RuntimeError(f"Failed to download '{filename}' after {max_attempts} attempts") from last_err


# Function to read the CSV file and download audio for each entry
def process_csv(input_file, output_path):
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for idx, row in enumerate(reader, start=1):
            # Basic robustness: skip short/blank rows
            if not row or len(row) < 2:
                print(f"[SKIP] Row {idx} is empty or malformed: {row}")
                continue
            video_name = row[0].strip()
            video_url = row[1].strip()  # Use full URL directly
            if not video_name or not video_url:
                print(f"[SKIP] Row {idx} missing name or URL: {row}")
                continue
            try:
                download_audio(video_url, output_path, video_name)
            except Exception as e:
                print(f"[FAIL] Could not download '{video_name}' ({video_url}): {e}")


# Example usage
process_csv(input_csv_file, destination_path)
"""
Make sure to replace input_csv_file and destination_path with the appropriate paths for your setup.
"""
