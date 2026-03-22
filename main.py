import asyncio
import os
from telethon import TelegramClient
import yt_dlp

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

channel = "me"  # change later if needed

client = TelegramClient("session", api_id, api_hash)

# ===== DOWNLOAD USING YT-DLP =====
def download_video(url):
    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'best',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "video.mp4"

    except Exception as e:
        print("❌ yt-dlp error:", e)
        return None


async def main():
    print("🔥 USERBOT RUNNING (yt-dlp mode)")

    # 👉 TEST WITH ONE LINK FIRST
    test_link = "https://www.desitales2.com/videos/latest-updates/"

    while True:
        try:
            print("🔍 Trying download...")

            file = download_video(test_link)

            if not file:
                continue

            print("📤 Uploading...")
            await client.send_file(channel, file)

            os.remove(file)
            print("✅ Done")

        except Exception as e:
            print("❌ Error:", e)

        await asyncio.sleep(600)


with client:
    client.loop.run_until_complete(main())
