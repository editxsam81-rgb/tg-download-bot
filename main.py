import os
from telethon import TelegramClient, events
import yt_dlp

# ===== CONFIG =====
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient("session", api_id, api_hash)

# ===== DOWNLOAD FUNCTION WITH COOKIES =====
def download_video(url):
    try:
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'best',
            'cookiefile': 'cookies.txt',  # 🔥 IMPORTANT
            'quiet': False,
            'nocheckcertificate': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return filename

    except Exception as e:
        print("❌ Download error:", e)
        return None


# ===== MESSAGE HANDLER =====
@client.on(events.NewMessage)
async def handler(event):
    text = event.raw_text

    # Check if message contains a link
    if "http" in text:
        await event.reply("⬇️ Downloading...")

        file = download_video(text)

        if not file:
            await event.reply("❌ Failed to download (maybe cookies expired)")
            return

        await event.reply("📤 Uploading...")
        await client.send_file(event.chat_id, file)

        os.remove(file)
        await event.reply("✅ Done")


# ===== START =====
print("🔥 BOT RUNNING (COOKIE MODE)")

client.start()
client.run_until_disconnected()
