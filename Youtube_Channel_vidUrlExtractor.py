#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

import yt_dlp as youtube_dl

# --- Helpers ---------------------------------------------------------------

# Regex to catch most emoji ranges
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"  # dingbats
    "\U0001F900-\U0001F9FF"  # supplemental symbols
    "\U00002600-\U000026FF"  # misc symbols
    "\U00002B00-\U00002BFF"  # arrows
    "]+",
    flags=re.UNICODE
)

def sanitize_title(title: str) -> str:
    # Remove filesystem-unsafe chars
    sanitized_title = re.sub(r'[<>:"/\\|?*.#]', '', title)
    # Remove double quotes explicitly
    sanitized_title = sanitized_title.replace('"', '')
    # Strip emojis
    sanitized_title = EMOJI_PATTERN.sub('', sanitized_title)
    return sanitized_title.strip()

def normalize_channel_url(url: str) -> str:
    """
    Prefer the Videos tab so Shorts/Streams shelves don't get mixed in
    unless explicitly requested.
    """
    if re.search(r'/videos/?$', url) or re.search(r'/live/?$', url) or re.search(r'/shorts/?$', url):
        return url
    if '/watch' in url or '/playlist' in url:
        return url
    return url.rstrip('/') + '/videos'

def walk_entries(node):
    """
    yt-dlp may return nested 'entries' (shelves/sections).
    Recursively yields flat video dicts with at least id/title.
    """
    if node is None:
        return
    if isinstance(node, list):
        for x in node:
            yield from walk_entries(x)
        return
    if isinstance(node, dict):
        if node.get('_type') in (None, 'url'):
            vid = node.get('id')
            title = node.get('title')
            if vid and title:
                yield node
        if 'entries' in node and isinstance(node['entries'], list):
            for x in node['entries']:
                yield from walk_entries(x)

# --- Main ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Export all video titles and URLs from a YouTube channel.")
    parser.add_argument("--channel-url", required=True, help="Channel URL, e.g. https://www.youtube.com/@handle or .../@handle/videos")
    parser.add_argument("--out", required=True, help="Path to output text file.")
    parser.add_argument("--max-videos", type=int, default=None, help="Optional cap on number of videos to export.")
    parser.add_argument("--include-shorts", action="store_true", help="Include Shorts if present on the page.")
    parser.add_argument("--include-live", action="store_true", help="Include Live/Streams if present on the page.")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Flat extraction (fast; no media downloads)
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
    }

    target_url = normalize_channel_url(args.channel_url)

    # Filters (keep Shorts/Live out unless requested)
    def allow(entry: dict) -> bool:
        url = entry.get('url') or ''
        if not url:
            vid = entry.get('id')
            if vid:
                url = f"https://www.youtube.com/watch?v={vid}"
        is_shorts = "/shorts/" in url
        live_status = entry.get('live_status')  # "is_live" | "was_live" | "not_live" | None
        is_live = (live_status == "is_live" or live_status == "was_live")
        if not args.include_shorts and is_shorts:
            return False
        if not args.include_live and is_live:
            return False
        return True

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(target_url, download=False)

        with out_path.open("w", encoding="utf-8") as f:
            count = 0
            for entry in walk_entries(info.get("entries")):
                if args.max_videos is not None and count >= args.max_videos:
                    break
                if not allow(entry):
                    continue

                title = sanitize_title(entry.get("title") or "")
                vid = entry.get("id")
                url = entry.get("url")
                if not url:
                    if vid:
                        url = f"https://www.youtube.com/watch?v={vid}"
                    else:
                        continue  # malformed entry

                f.write(f'"{title}","{url}"\n')
                count += 1

    print(f'Saved video names and URLs to {out_path}')

if __name__ == "__main__":
    main()
