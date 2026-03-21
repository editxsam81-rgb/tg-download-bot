import os
import asyncio
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from telegram import Bot
import yt_dlp

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
STORAGE_CHANNEL = int(os.getenv("STORAGE_CHANNEL"))
MONGO_URI = os.getenv("MONGO_URI")

CAPTION = "join telegram @link69_viral"
CHECK_INTERVAL = 600

# ================= DB =================
client = MongoClient(MONGO_URI)
db = client["scraperbot"]
links_db = db.links

bot = Bot(token=BOT_TOKEN)

# ================= GET POSTS =================
def get_post_links():
    url = "https://www.thekamababa.com/"
    print("🌐 Fetching:", url)

    res = requests.get(url, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if (
            "thekamababa.com/" in href
            and not any(x in href for x in [
                "category", "tag", "page", "filter",
                "contact", "complaint", "tags"
            ])
            and href.count("/") > 3
        ):
            links.append(href)

    links = list(set(links))
    print("🔗 POSTS:", links)
    return links


# ================= EXTRACT REAL VIDEO =================
def extract_video_url(page_url):
    print("🔍 Extracting video from:", page_url)

    try:
        res = requests.get(page_url, timeout=15)
        soup = BeautifulSoup(res.text, "html.parser")

        # 🔥 1. Check video tag
        video = soup.find("video")
        if video and video.get("src"):
            return video["src"]

        # 🔥 2. Check source tag
        source = soup.find("source")
        if source and source.get("src"):
            return source["src"]

        # 🔥 3. Check iframe
        iframe = soup.find("iframe")
        if iframe and iframe.get("src"):
            return iframe["src"]

    except Exception as e:
        print("❌ Extract error:", e)

    return None


# ================= DOWNLOAD =================
def download_video(url):
    print("⬇️ Downloading:", url)

    ydl_opts = {
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "format": "best",
        "noplaylist": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print("✅ Downloaded:", filename)
            return filename
    except Exception as e:
        print("❌ Download error:", e)
        return None


# ================= UPLOAD =================
async def upload(file_path):
    print("📤 Uploading:", file_path)

    try:
        with open(file_path, "rb") as f:
            await bot.send_document(
                chat_id=STORAGE_CHANNEL,
                document=f,
                caption=CAPTION
            )
        print("✅ Uploaded")
    except Exception as e:
        print("❌ Upload error:", e)

    try:
        os.remove(file_path)
    except:
        pass


# ================= LOOP =================
async def main_loop():
    while True:
        print("🔁 LOOP STARTED")

        try:
            posts = get_post_links()

            for post in posts:

                if links_db.find_one({"url": post}):
                    continue

                video_url = extract_video_url(post)

                if not video_url:
                    print("❌ No video found")
                    continue

                file = download_video(video_url)

                if not file:
                    continue

                await upload(file)

                links_db.insert_one({"url": post})

                print("✅ DONE:", post)

                await asyncio.sleep(10)

        except Exception as e:
            print("❌ LOOP ERROR:", e)

        print("⏱ Waiting 10 min...\n")
        await asyncio.sleep(CHECK_INTERVAL)


# ================= RUN =================
if __name__ == "__main__":
    print("🚀 Bot 1 Running...")
    asyncio.run(main_loop())
