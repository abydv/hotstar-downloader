import os
import subprocess
import time
from urllib.parse import urlparse

BASE_DIR = os.getcwd()
URL_FILE = os.path.join(BASE_DIR, "hotstar_urls.tt")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
LOG_FILE = os.path.join(DOWNLOAD_DIR, "downloaded.log")

# Cookie lookup: env HOTSTAR_COOKIES -> cookies/hotstar.txt -> None
COOKIE_FILE = os.environ.get("HOTSTAR_COOKIES") or os.path.join(BASE_DIR, "cookies", "hotstar.txt")

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

downloaded = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        downloaded = {line.strip() for line in f if line.strip()}

def mark_downloaded(url: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")
    downloaded.add(url)

def download_url(url: str):
    parsed = urlparse(url)
    # Use netloc as subdir to avoid collisions
    domain_dir = parsed.netloc.replace('.', '_')
    out_dir = os.path.join(DOWNLOAD_DIR, domain_dir)
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "yt-dlp",
        # best video + audio, fallback to best
        "-f", "bestvideo*+bestaudio/best",
        "--merge-output-format", "mp4",
        "--continue",
        "--no-mtime",
        "--retries", "10",
        "--fragment-retries", "10",
        "--file-access-retries", "10",
        "--user-agent", USER_AGENT,
        "-o", os.path.join(out_dir, "%(title)s.%(ext)s"),
        url
    ]

    if os.path.exists(COOKIE_FILE):
        cmd.insert(1, COOKIE_FILE)
        cmd.insert(1, "--cookies")
    else:
        print(f"[WARN] Cookie file not found at {COOKIE_FILE}. Some videos may require login.")

    print("[CMD] ", " ".join(cmd))

    res = subprocess.run(cmd)
    if res.returncode == 0:
        mark_downloaded(url)
        print("[OK] Downloaded:", url)
    else:
        print("[ERR] Failed to download:", url)

def main():
    if not os.path.exists(URL_FILE):
        print(f"URL list not found: {URL_FILE}")
        return

    with open(URL_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if not urls:
        print("No URLs to download")
        return

    for u in urls:
        if u in downloaded:
            print("[SKIP] Already downloaded:", u)
            continue

        print("[DOWNLOAD]", u)
        download_url(u)
        time.sleep(5)

    print("[DONE] All urls processed")

if __name__ == "__main__":
    main()
