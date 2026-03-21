import os
import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import yt_dlp

# ================= CONFIG =================

print("🔥 BOT STARTED...")

BOT_TOKEN = os.getenv("BOT_TOKEN")  
# 👉 REPLACE in Railway ENV

CHANNEL_ID = os.getenv("CHANNEL_ID")  
# 👉 REPLACE with your STORAGE CHANNEL ID (-100xxxxxxxxxx)

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN missing")

if not CHANNEL_ID:
    raise ValueError("❌ CHANNEL_ID missing")

CHANNEL_ID = int(CHANNEL_ID)

bot = Bot(token=BOT_TOKEN)

CAPTION = "join telegram @link69_viral"  
# 👉 EDIT if needed

URL = "https://www.thekamababa.com/"  
# 👉 SOURCE WEBSITE

CHECK_INTERVAL = 600  # 10 min
MAX_SIZE_MB = 49

downloaded = set()

# ================= FETCH POSTS =================

def get_posts():
    print("🌐 Fetching website...")
    res = requests.get(URL, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        link = a["href"]

        if (
            "/category/" not in link and
            "/tag/" not in link and
            "page/" not in link and
            "?" not in link and
            link.endswith("/")
        ):
            if "thekamababa.com" in link:
                links.append(link)

    return list(set(links))

# ================= EXTRACT VIDEO =================

def get_video_url(post_url):
    try:
        print(f"🔍 Extracting: {post_url}")
        res = requests.get(post_url, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        video = soup.find("video")

        if video:
            source = video.find("source")
            if source and source.get("src"):
                return source["src"]

        return None

    except Exception as e:
        print("❌ Extract error:", e)
        return None

# ================= DOWNLOAD =================

def download_video(url):
    try:
        print(f"⬇️ Downloading: {url}")

        ydl_opts = {
            "outtmpl": "video.mp4",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        size = os.path.getsize("video.mp4") / (1024 * 1024)
        print(f"📦 Size: {size:.2f} MB")

        if size > MAX_SIZE_MB:
            print("⚠️ Skipped (too large)")
            os.remove("video.mp4")
            return None

        return "video.mp4"

    except Exception as e:
        print("❌ Download error:", e)
        return None

# ================= UPLOAD =================

async def upload_video(file):
    try:
        print("📤 Uploading...")

        with open(file, "rb") as f:
            await bot.send_document(
                chat_id=CHANNEL_ID,
                document=f,
                caption=CAPTION
            )

        os.remove(file)
        print("✅ Uploaded")

    except Exception as e:
        print("❌ Upload error:", e)

# ================= LOOP =================

async def main_loop():
    print("🔁 LOOP STARTED")

    while True:
        try:
            posts = get_posts()
            print(f"🔗 Found {len(posts)} posts")

            for post in posts:
                if post in downloaded:
                    continue

                video_url = get_video_url(post)

                if not video_url:
                    continue

                file = download_video(video_url)

                if file:
                    await upload_video(file)
                    downloaded.add(post)

                await asyncio.sleep(5)

        except Exception as e:
            print("❌ Loop error:", e)

        print("⏳ Sleeping 10 min...\n")
        await asyncio.sleep(CHECK_INTERVAL)

# ================= RUN =================

asyncio.run(main_loop())
