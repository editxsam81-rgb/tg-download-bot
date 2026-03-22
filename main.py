import asyncio
import requests
import re
import os
from telethon import TelegramClient

# ====== CONFIG ======
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# 👉 For testing (no channel needed)
channel = "me"

client = TelegramClient("session", api_id, api_hash)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ====== EXTRACT VIDEO ======
def extract_video(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)

        patterns = [
            r'https?://[^"]+\.mp4',
            r'https?://[^"]+\.m3u8'
        ]

        for pattern in patterns:
            match = re.search(pattern, r.text)
            if match:
                return match.group(0)

        return None

    except Exception as e:
        print("❌ Extract error:", e)
        return None


# ====== DOWNLOAD VIDEO ======
def download(url):
    try:
        filename = "video.mp4"

        with requests.get(url, headers=HEADERS, stream=True, timeout=30) as r:
            with open(filename, "wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)

        return filename

    except Exception as e:
        print("❌ Download error:", e)
        return None


# ====== MAIN LOOP ======
async def main():
    print("🔥 USERBOT RUNNING")

    while True:
        try:
            print("🌐 Fetching website...")

            r = requests.get(
                "https://www.desitales2.com/videos/latest-updates/",
                headers=HEADERS
            )

            print("🌐 Status:", r.status_code)

            links = re.findall(
                r'href="(https://www.desitales2.com/[^"]+)"',
                r.text
            )

            print("🔗 Links found:", len(links))

            for link in links[:3]:
                print("🔍 Checking:", link)

                video = extract_video(link)
                print("🎥 Found:", video)

                if not video:
                    continue

                file = download(video)

                if not file:
                    continue

                print("📤 Uploading to Telegram...")
                await client.send_file(channel, file)

                os.remove(file)
                print("✅ Done\n")

        except Exception as e:
            print("❌ Main error:", e)

        print("⏳ Waiting 10 minutes...\n")
        await asyncio.sleep(600)


# ====== START CLIENT ======
with client:
    client.loop.run_until_complete(main())
