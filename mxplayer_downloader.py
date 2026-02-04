import os
import subprocess
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ================= CONFIG =================

BASE_DIR = os.getcwd()
URL_DIR = os.path.join(BASE_DIR, "mxplayer_yearwise_urls")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
LOG_FILE = os.path.join(DOWNLOAD_DIR, "downloaded.log")
COOKIE_FILE = os.path.join(BASE_DIR, "cookies", "mxplayer.txt")

START_YEAR = 2014
END_YEAR = 2026   # processed in descending order

MIN_SLEEP = 5
MAX_SLEEP = 10

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120 Safari/537.36"
)

# =========================================

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------- Resume tracking ----------
downloaded = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        downloaded = {line.strip() for line in f if line.strip()}

def mark_downloaded(url: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")
    downloaded.add(url)

# ---------- Headless Chrome (NO UI, NO AUDIO) ----------

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")

# 🔇 CRITICAL: disable audio completely
chrome_options.add_argument("--mute-audio")

chrome_options.add_argument(f"--user-agent={USER_AGENT}")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# ------------------------------------------------------

def is_watch_url(url: str) -> bool:
    return "/movie/watch-" in url

def is_detail_url(url: str) -> bool:
    return "/detail/movie/" in url

def resolve_to_watch_url(url: str) -> str | None:
    """
    Resolve /detail/movie/... → /movie/watch-* using headless Chrome
    """
    driver.get(url)
    time.sleep(7)  # allow JS routing

    final_url = driver.current_url
    if is_watch_url(final_url):
        return final_url

    return None

def download_movie(watch_url: str, year: int):
    year_dir = os.path.join(DOWNLOAD_DIR, str(year))
    os.makedirs(year_dir, exist_ok=True)

    cmd = [
        "yt-dlp",

        # ===== HIGHEST QUALITY =====
        "-f", "bestvideo*+bestaudio/best",
        "--merge-output-format", "mp4",

        # ===== RESUME & STABILITY =====
        "--continue",
        "--no-mtime",
        "--retries", "10",
        "--fragment-retries", "10",
        "--file-access-retries", "10",

        # ===== SUBTITLES =====
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs", "all",
        "--convert-subs", "srt",

        "--user-agent", USER_AGENT,
        "-o", os.path.join(year_dir, "%(title)s.%(ext)s"),
        watch_url
    ]

    if os.path.exists(COOKIE_FILE):
        cmd.insert(1, "--cookies")
        cmd.insert(2, COOKIE_FILE)

    result = subprocess.run(cmd)

    if result.returncode == 0:
        mark_downloaded(watch_url)
        print("[OK] Download completed")
    else:
        print("[WARN] Download failed (will retry later)")

def process_year(year: int):
    file_path = os.path.join(URL_DIR, f"mxplayer_movies_{year}.txt")

    if not os.path.exists(file_path):
        return

    with open(file_path, "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]

    if not urls:
        return

    print(f"\n[YEAR {year}] URLs: {len(urls)}")

    for idx, url in enumerate(urls, start=1):

        if url in downloaded:
            print(f"[SKIP] {idx}/{len(urls)} already downloaded")
            continue

        watch_url = None

        if is_watch_url(url):
            watch_url = url
        elif is_detail_url(url):
            watch_url = resolve_to_watch_url(url)

        if not watch_url:
            print("[SKIP] Unable to resolve watch URL")
            continue

        print(f"[{year}] {idx}/{len(urls)}")
        print(f"[DOWNLOAD] {watch_url}")

        download_movie(watch_url, year)

        sleep_time = random.randint(MIN_SLEEP, MAX_SLEEP)
        print(f"[SLEEP] {sleep_time}s")
        time.sleep(sleep_time)

def main():
    print("[START] MX Player downloader (HEADLESS, SILENT, HQ)")
    print("[INFO] Processing years from 2026 → 2014")

    for year in range(END_YEAR, START_YEAR - 1, -1):
        process_year(year)

    driver.quit()
    print("\n[DONE] All possible downloads completed")

if __name__ == "__main__":
    main()
