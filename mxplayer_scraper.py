import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

BASE_URL = "https://www.mxplayer.in"
START_YEAR = 2014
END_YEAR = 2026

SCROLL_PAUSE = 3
MAX_IDLE_SCROLLS = 4

OUTPUT_DIR = "mxplayer_yearwise_urls"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("[BOOT] Starting MX Player scraper...")

options = webdriver.ChromeOptions()

# IMPORTANT: DO NOT USE HEADLESS
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--lang=en-US")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

def scrape_year(year):
    url = f"{BASE_URL}/movie-videos/{year}-movies"
    output_file = os.path.join(OUTPUT_DIR, f"mxplayer_movies_{year}.txt")

    print(f"\n[OPEN] {url}")
    driver.get(url)
    time.sleep(6)

    last_height = driver.execute_script("return document.body.scrollHeight")
    idle = 0

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)

        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            idle += 1
            print(f"[SCROLL] No new content ({idle}/{MAX_IDLE_SCROLLS})")
            if idle >= MAX_IDLE_SCROLLS:
                break
        else:
            idle = 0
            last_height = new_height
            print("[SCROLL] Loaded more content")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    movie_urls = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/movie/" in href:
            if href.startswith("/"):
                href = BASE_URL + href
            movie_urls.add(href)

    with open(output_file, "w", encoding="utf-8") as f:
        for u in sorted(movie_urls):
            f.write(u + "\n")

    print(f"[DONE] {year} → {len(movie_urls)} URLs saved")

try:
    for year in range(START_YEAR, END_YEAR + 1):
        scrape_year(year)
finally:
    driver.quit()
    print("\n[EXIT] Browser closed. Scraping finished.")
