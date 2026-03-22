import asyncio
import requests
import re
import os
from telethon import TelegramClient

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
channel = os.getenv("CHANNEL")

client = TelegramClient("session", api_id, api_hash)

def extract_video(url):
    try:
        r = requests.get(url)
        match = re.search(r'https?://[^"]+\.mp4', r.text)
        return match.group(0) if match else None
    except:
        return None

def download(url):
    filename = "video.mp4"
    with requests.get(url, stream=True) as r:
        with open(filename, "wb") as f:
            for chunk in r.iter_content(1024*1024):
                if chunk:
                    f.write(chunk)
    return filename

async def main():
    print("🔥 USERBOT RUNNING")

    while True:
        try:
            r = requests.get("https://www.desitales2.com/videos/latest-updates/")
            links = re.findall(r'href="(https://www.desitales2.com/[^"]+)"', r.text)

            for link in links[:5]:
                print("🔍", link)

                video = extract_video(link)
                if not video:
                    continue

                file = download(video)

                print("📤 Uploading...")
                await client.send_file(channel, file)

                os.remove(file)

        except Exception as e:
            print("❌ Error:", e)

        await asyncio.sleep(600)

with client:
    client.loop.run_until_complete(main())
