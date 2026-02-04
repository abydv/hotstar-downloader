Below are **two ready-to-use files** for your project:

1. **`requirements.txt`** – minimal, correct dependencies
2. **`README.md`** – written for a **layman / non-technical user**, step-by-step, copy-paste friendly

You can copy these **as-is**.

---

# ✅ `requirements.txt`

```txt
yt-dlp>=2024.01.01
selenium>=4.15.0
webdriver-manager>=4.0.1
```

> **Notes**

* `yt-dlp` → downloads videos
* `selenium` → opens MX Player pages silently (no window)
* `webdriver-manager` → automatically manages ChromeDriver
* `ffmpeg` is required but installed **separately** (explained in README)

---

# ✅ `README.md` (Layman-Friendly)

```md
# MX Player Movie Downloader (Automatic)

This tool downloads **MX Player movies year-wise** in **highest quality**, completely **silently** (no browser window, no sound).

It works even if downloads stop midway — you can safely restart anytime.

---

## 🔹 What This Tool Does

- Downloads movies from MX Player
- Highest video + audio quality available
- Downloads subtitles (if available)
- Works year-wise (2026 → 2014)
- No duplicate downloads
- Resume supported (safe to stop/start)
- Chrome runs silently in background (no sound, no window)

---

## 📁 Folder Structure (Important)

Your folder should look like this:

```

movie-downloader/
├── mxplayer_yearwise_urls/
│   ├── mxplayer_movies_2014.txt
│   ├── mxplayer_movies_2015.txt
│   └── ...
├── downloads/
├── cookies/
│   └── mxplayer.txt   (optional but recommended)
├── mxplayer_downloader.py
├── requirements.txt
└── README.md

```

---

## 🧰 Step 1: Install Python (Once)

1. Download Python from:
   https://www.python.org/downloads/

2. **IMPORTANT:**  
   During installation, check:
```

☑ Add Python to PATH

````

3. After installation, open **Command Prompt / PowerShell** and run:
```powershell
python --version
````

---

## 🧰 Step 2: Install Required Tools

### Install Python libraries

Open PowerShell inside the project folder and run:

```powershell
pip install -r requirements.txt
```

---

### Install FFmpeg (REQUIRED)

1. Download FFmpeg:
   [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

2. Download **ffmpeg-release-essentials.zip**

3. Extract it

4. Copy `ffmpeg.exe` into:

   ```
   movie-downloader/ffmpeg/
   ```

(yt-dlp will automatically find it)

---

## 🍪 Step 3 (Recommended): Add Cookies (Avoid Errors)

Some movies require login/session cookies.

### How to do it

1. Install browser extension:
   **Get cookies.txt**

2. Open MX Player in Chrome

3. Login (if required)

4. Export cookies

5. Save as:

   ```
   cookies/mxplayer.txt
   ```

This greatly improves success rate.

---

## ▶ Step 4: Start Downloading

Open PowerShell in the project folder and run:

```powershell
python mxplayer_downloader.py
```

That’s it.

---

## 🔄 Can I Stop and Restart?

Yes. Absolutely safe.

* Already downloaded movies are skipped
* Failed movies retry automatically
* Progress is saved in:

  ```
  downloads/downloaded.log
  ```

---

## 🔇 Will I See or Hear Anything?

No.

* No Chrome window
* No sound
* Fully silent background operation

---

## 📂 Where Are Movies Saved?

Movies are saved year-wise:

```
downloads/
├── 2026/
├── 2025/
├── 2024/
└── ...
```

Subtitles (if available) are saved alongside the movie file.

---

## ⚠ Common Issues & Fixes

### ❌ Movie fails to download

* Movie may be removed from MX Player
* Try again later
* Cookies usually fix this

### ❌ No subtitles

* Some movies don’t have subtitles on MX Player

### ❌ Chrome error

* Update Google Chrome to latest version

---

## ❗ Important Rules (Please Read)

* ❌ Do NOT run multiple copies at once
* ❌ Do NOT remove sleep delays
* ✔ Let it run overnight
* ✔ Use cookies for best results

---

## ✅ Summary (Simple)

1. Install Python
2. Install requirements
3. Add FFmpeg
4. (Optional) Add cookies
5. Run the script

That’s all. Enjoy 😊

```

---
