import os
import subprocess
import time
from urllib.parse import urlparse

BASE_DIR = os.getcwd()

URL_FILE = os.path.join(BASE_DIR, "hotstar_urls.tt")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
LOG_FILE = os.path.join(DOWNLOAD_DIR, "downloaded.log")

COOKIE_FILE = os.environ.get("HOTSTAR_COOKIES") or os.path.join(
    BASE_DIR, "cookies", "hotstar.txt"
)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
)

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ---------------- LOAD DOWNLOADED LOG ----------------

downloaded = set()

if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        downloaded = {line.strip() for line in f if line.strip()}


def mark_downloaded(url):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")
    downloaded.add(url)


# ---------------- DOWNLOAD FUNCTION ----------------

def download_url(url):
    parsed = urlparse(url)
    domain_dir = parsed.netloc.replace(".", "_")

    out_dir = os.path.join(DOWNLOAD_DIR, domain_dir)
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "yt-dlp",
        "-f", "bestvideo*+bestaudio/best",
        "--merge-output-format", "mp4",
        "--continue",
        "--no-mtime",
        "--retries", "10",
        "--fragment-retries", "10",
        "--file-access-retries", "10",
        "--user-agent", USER_AGENT,
        "-o", os.path.join(out_dir, "%(title)s.%(ext)s"),
    ]

    if os.path.exists(COOKIE_FILE):
        cmd += ["--cookies", COOKIE_FILE]
    else:
        print(f"[WARN] Cookie not found: {COOKIE_FILE}")

    cmd.append(url)

    print("\n[RUN]", " ".join(cmd))

    try:
        result = subprocess.run(cmd, check=False)

        if result.returncode == 0:
            mark_downloaded(url)
            print("[DONE]", url)
        else:
            print("[FAILED]", url)

    except Exception as e:
        print("[ERROR]", e)


# ---------------- MAIN LOOP ----------------

def main():
    if not os.path.exists(URL_FILE):
        print("URL file not found:", URL_FILE)
        return

    with open(URL_FILE, "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]

    if not urls:
        print("No links in file")
        return

    print(f"Total links: {len(urls)}")
    print(f"Already downloaded: {len(downloaded)}")

    for index, url in enumerate(urls, start=1):

        if url in downloaded:
            print(f"[SKIP {index}] Already done")
            continue

        print(f"\n[DOWNLOAD {index}/{len(urls)}]")
        print(url)

        download_url(url)

        time.sleep(5)   # avoid rate limit

    print("\nAll links processed!")


if __name__ == "__main__":
    main()
