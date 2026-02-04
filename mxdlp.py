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
END_YEAR = 2026

MIN_SLEEP = 5
MAX_SLEEP = 10

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120 Safari/537.36"
)

# =========================================

if not os.path.exists(COOKIE_FILE):
    raise FileNotFoundError(
        f"Cookie file not found: {COOKIE_FILE}\n"
        "Place mxplayer.txt inside cookies/ folder"
    )

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------- Resume tracking ----------
downloaded = set()
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        downloaded = {line.strip() for line in f if line.strip()}
    print(f"[RESUME] Loaded {len(downloaded)} previously downloaded URLs")

def mark_downloaded(url: str):
    """Log downloaded URL to avoid re-downloading"""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")
    downloaded.add(url)
    print(f"[LOG] URL saved to {LOG_FILE}")

# ---------- Headless Chrome ----------

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--window-size=1920,1080")
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
    driver.get(url)
    time.sleep(7)
    final_url = driver.current_url
    if is_watch_url(final_url):
        return final_url
    return None

def download_movie(watch_url: str, year: int):
    year_dir = os.path.join(DOWNLOAD_DIR, str(year))
    os.makedirs(year_dir, exist_ok=True)

    cmd = [
        "yt-dlp",

        # ===== PARALLEL DOWNLOADS =====
        "-N", "4",

        # ===== ROBUST FORMAT SELECTION =====
        # 1. Best video + Hindi audio (if exists)
        # 2. Best MP4 progressive
        # 3. Best available (fallback)
        "-f", "(bv*+ba[language=hi]/b)[protocol!=m3u8]/best[ext=mp4]/best",

        "--merge-output-format", "mp4",
        "--remux-video", "mp4",
        "--no-keep-video",

        # ===== STABILITY =====
        "--continue",
        "--no-mtime",
        "--retries", "10",
        "--fragment-retries", "10",
        "--file-access-retries", "10",

        # ===== AUTH =====
        "--cookies", COOKIE_FILE,
        "--user-agent", USER_AGENT,

        # ===== OUTPUT =====
        "-o", os.path.join(year_dir, "%(title)s.%(ext)s"),

        watch_url
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        mark_downloaded(watch_url)
        print("[OK] Single MP4 downloaded (best available quality)")
    else:
        print("[WARN] Download failed (format unavailable / DRM)")

def get_year_input():
    print("\n[SELECT] Choose download option:")
    print(f"[1] All years ({START_YEAR}-{END_YEAR})")
    print(f"[2] Specific year")
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        return list(range(END_YEAR, START_YEAR - 1, -1))
    elif choice == "2":
        try:
            year = int(input(f"Enter year ({START_YEAR}-{END_YEAR}): ").strip())
            if START_YEAR <= year <= END_YEAR:
                return [year]
            else:
                print(f"[ERROR] Year must be between {START_YEAR} and {END_YEAR}")
                return get_year_input()
        except ValueError:
            print("[ERROR] Invalid input. Please enter a valid year")
            return get_year_input()
    else:
        print("[ERROR] Invalid choice. Please enter 1 or 2")
        return get_year_input()

def process_year(year: int):
    file_path = os.path.join(URL_DIR, f"mxplayer_movies_{year}.txt")
    if not os.path.exists(file_path):
        return 0

    with open(file_path, "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f if u.strip()]

    if not urls:
        return 0

    total = len(urls)
    skipped = 0
    print(f"\n[YEAR {year}] URLs: {total}")

    for idx, url in enumerate(urls, start=1):

        if url in downloaded:
            print(f"[SKIP] {idx}/{total} already downloaded")
            skipped += 1
            continue

        watch_url = url if is_watch_url(url) else resolve_to_watch_url(url)

        if not watch_url:
            print(f"[SKIP] {idx}/{total} unable to resolve watch URL")
            continue

        print(f"[DOWNLOAD] {idx}/{total} → {watch_url}")
        download_movie(watch_url, year)

        sleep_time = random.randint(MIN_SLEEP, MAX_SLEEP)
        print(f"[SLEEP] {sleep_time}s")
        time.sleep(sleep_time)
    
    return skipped

def main():
    print("[START] MX Player downloader")
    print("[INFO] Best quality | Hindi-first | Single MP4 | N=4")
    print(f"[LOG] Download progress saved to: {LOG_FILE}")

    years = get_year_input()
    
    total_skipped = 0
    for year in years:
        skipped = process_year(year)
        total_skipped += skipped

    driver.quit()
    print(f"\n[DONE] All possible downloads completed")
    print(f"[SUMMARY] Total downloaded: {len(downloaded)} | Skipped (already downloaded): {total_skipped}")

# ===== ENTRY POINT =====
if __name__ == "__main__":
    main()
