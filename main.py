import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL = os.getenv("CHANNEL")  # username OR -100id

CAPTION = "join telegram @link69_viral"
WEBSITE = "https://www.thekamababa.com/"

# =========================================

if not API_ID or not API_HASH or not CHANNEL:
    raise ValueError("❌ Missing API_ID / API_HASH / CHANNEL")

client = TelegramClient("bot_session", API_ID, API_HASH)

downloaded = set()

# -------- GET POSTS --------
def get_posts():
    try:
        r = requests.get(WEBSITE, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]

            if WEBSITE in href and "/category/" not in href and "/tag/" not in href:
                if href.endswith("/"):
                    links.append(href)

        return list(set(links))
    except:
        return []

# -------- EXTRACT VIDEO --------
def extract_video(post_url):
    try:
        r = requests.get(post_url, timeout=10)
        html = r.text

        # find mp4 directly
        if ".mp4" in html:
            start = html.find("https://")
            end = html.find(".mp4") + 4
            return html[start:end]

    except:
        return None

# -------- DOWNLOAD --------
def download_video(url):
    try:
        filename = "video.mp4"

        with requests.get(url, stream=True) as r:
            with open(filename, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)

        return filename
    except:
        return None

# -------- UPLOAD --------
async def upload_video(file):
    try:
        size = os.path.getsize(file) / (1024 * 1024)

        if size > 300:
            print(f"⚠️ Skipped (too big {size:.1f}MB)")
            return

        await client.send_file(
            CHANNEL,
            file,
            caption=CAPTION,
            supports_streaming=True
        )

        print("✅ Uploaded")

    except Exception as e:
        print("❌ Upload error:", e)

# -------- MAIN LOOP --------
async def main():
    await client.start()

    print("🔥 BOT STARTED...")

    while True:
        print("🌐 Fetching website...")
        posts = get_posts()
        print(f"🔗 Found {len(posts)} posts")

        for post in posts:
            if post in downloaded:
                continue

            print("🔍 Extracting:", post)

            video_url = extract_video(post)
            if not video_url:
                continue

            file = download_video(video_url)

            if file:
                await upload_video(file)
                downloaded.add(post)

                try:
                    os.remove(file)
                except:
                    pass

                await asyncio.sleep(10)  # safe delay

        print("⏳ Sleeping 10 min...")
        await asyncio.sleep(600)

# -------- RUN --------
asyncio.run(main())
