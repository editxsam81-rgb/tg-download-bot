import os
import asyncio
import requests
from bs4 import BeautifulSoup
import yt_dlp
from telegram import Bot

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # MUST be -100xxxxxxxxxx

CHECK_INTERVAL = 600  # 10 min
MAX_SIZE = 50 * 1024 * 1024  # 50MB

bot = Bot(token=BOT_TOKEN)

# ================= MEMORY =================
downloaded_links = set()

# ================= SCRAPER =================
def get_post_links():
    url = "https://www.thekamababa.com/"
    print(f"🌐 Fetching: {url}")

    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]

            # ✅ Only valid post links
            if "thekamababa.com" in href and href.count("/") > 3:
                if "/category/" not in href and "/tag/" not in href:
                    links.append(href)

        links = list(set(links))  # remove duplicates
        print(f"🔗 POSTS: {links[:20]}")

        return links

    except Exception as e:
        print(f"❌ Fetch error: {e}")
        return []

# ================= EXTRACT VIDEO =================
def extract_video_url(post_url):
    try:
        print(f"🔍 Extracting video from: {post_url}")

        res = requests.get(post_url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        video = soup.find("video")
        if video:
            source = video.find("source")
            if source and source.get("src"):
                return source["src"]

        return None

    except Exception as e:
        print(f"❌ Extract error: {e}")
        return None

# ================= DOWNLOAD =================
def download_video(url):
    ydl_opts = {
        "outtmpl": "video.%(ext)s",
        "quiet": True,
        "format": "mp4/best",
        "noplaylist": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

            if not os.path.exists(file):
                return None

            size = os.path.getsize(file)

            # ❌ Skip large files
            if size > MAX_SIZE:
                print("❌ Skipped (too large)")
                os.remove(file)
                return None

            return file

    except Exception as e:
        print(f"❌ Download error: {e}")
        return None

# ================= UPLOAD =================
async def upload_video(file_path):
    try:
        print(f"📤 Uploading: {file_path}")

        with open(file_path, "rb") as video:
            await bot.send_video(
                chat_id=CHANNEL_ID,
                video=video,
                caption="join telegram @link69_viral"
            )

        print("✅ Uploaded")

    except Exception as e:
        print(f"❌ Upload error: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# ================= LOOP =================
async def loop():
    print("🔁 LOOP STARTED")

    while True:
        print("🔍 Checking website...")

        posts = get_post_links()

        for post_url in posts:

            # ✅ Skip already done
            if post_url in downloaded_links:
                continue

            video_url = extract_video_url(post_url)

            if not video_url:
                continue

            print(f"⬇️ Downloading: {video_url}")

            file = download_video(video_url)

            if file:
                await upload_video(file)
                downloaded_links.add(post_url)

                await asyncio.sleep(5)  # safe delay

        print("⏱ Waiting 10 minutes...\n")
        await asyncio.sleep(CHECK_INTERVAL)

# ================= MAIN =================
async def main():
    print("🚀 Bot 1 Running...")
    await loop()

# ================= START =================
if __name__ == "__main__":
    asyncio.run(main())
