import asyncio
import os
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient

# ================= CONFIG =================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # -100xxxx

SESSION = "session"  # session file name
WEBSITE = "https://www.thekamababa.com/"

# ==========================================

client = TelegramClient(SESSION, API_ID, API_HASH)


# ----------- FETCH POSTS -----------
def get_posts():
    try:
        res = requests.get(WEBSITE, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]

            if "/category/" in href:
                continue
            if "/tag/" in href:
                continue
            if "page" in href:
                continue

            if href.startswith(WEBSITE) and href not in links:
                links.append(href)

        print(f"🔗 Found {len(links)} posts")
        return links[:10]  # limit per loop

    except Exception as e:
        print("❌ Fetch error:", e)
        return []


# ----------- EXTRACT VIDEO -----------
def extract_video(post_url):
    try:
        res = requests.get(post_url, timeout=10)
        html = res.text

        # simple extract mp4
        import re
        match = re.search(r'(https?://[^\s"]+\.mp4)', html)

        if match:
            return match.group(1)

    except Exception as e:
        print("❌ Extract error:", e)

    return None


# ----------- DOWNLOAD -----------
def download_video(url):
    try:
        print("⬇️ Downloading...")
        file_name = "video.mp4"

        with requests.get(url, stream=True) as r:
            with open(file_name, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)

        return file_name

    except Exception as e:
        print("❌ Download error:", e)
        return None


# ----------- UPLOAD (NO LIMIT) -----------
async def upload_video(file_path):
    try:
        print("📤 Uploading...")

        await client.send_file(
            CHANNEL_ID,
            file_path,
            caption="🔥 Auto Uploaded",
            supports_streaming=True
        )

        os.remove(file_path)
        print("✅ Uploaded")

    except Exception as e:
        print("❌ Upload error:", e)


# ----------- MAIN LOOP -----------
async def main():
    await client.start()
    print("🔥 USERBOT STARTED")

    while True:
        print("🔁 LOOP STARTED")

        posts = get_posts()

        for post in posts:
            print(f"🔍 Processing: {post}")

            video_url = extract_video(post)

            if not video_url:
                continue

            file = download_video(video_url)

            if file:
                await upload_video(file)

        print("⏳ Sleeping 10 min...")
        await asyncio.sleep(600)


# ----------- RUN -----------
with client:
    client.loop.run_until_complete(main())
