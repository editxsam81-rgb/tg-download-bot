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
CHECK_INTERVAL = 600  # 10 min

# ================= DB =================
client = MongoClient(MONGO_URI)
db = client["scraperbot"]
links_db = db.links

bot = Bot(token=BOT_TOKEN)

# ================= SCRAPER =================
def get_video_links():
    url = "https://www.thekamababa.com/"
    print("🌐 Fetching:", url)

    res = requests.get(url, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # ✅ FILTER ONLY REAL POST LINKS
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
    print("🔗 FILTERED LINKS:", links)

    return links


# ================= DOWNLOADER =================
def download_video(url):
    print("⬇️ Downloading:", url)

    ydl_opts = {
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "noplaylist": True,
        "format": "best"
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


# ================= UPLOADER =================
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


# ================= MAIN LOOP =================
async def main_loop():
    while True:
        print("🔁 LOOP STARTED")
        print("🔍 Checking website...")

        try:
            links = get_video_links()

            for link in links:

                # SKIP DUPLICATE
                if links_db.find_one({"url": link}):
                    continue

                file = download_video(link)

                if not file:
                    continue

                await upload(file)

                links_db.insert_one({"url": link})

                print("✅ DONE:", link)

                await asyncio.sleep(10)  # SAFE DELAY

        except Exception as e:
            print("❌ LOOP ERROR:", e)

        print("⏱ Waiting 10 min...\n")
        await asyncio.sleep(CHECK_INTERVAL)


# ================= RUN =================
if __name__ == "__main__":
    print("🚀 Bot 1 Running...")

    try:
        asyncio.run(main_loop())
    except Exception as e:
        print("🔥 FATAL ERROR:", e)
