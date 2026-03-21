import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# download function
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best[filesize<50M]/best',
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "video.mp4"
    except Exception as e:
        print("Download error:", e)
        return None

# handle message
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⬇️ Downloading...")

    file = download_video(url)

    if file and os.path.exists(file):
        await update.message.reply_text("📤 Uploading...")
        try:
            await update.message.reply_video(video=open(file, "rb"))
        except Exception as e:
            await update.message.reply_text(f"❌ Upload error: {e}")
        os.remove(file)
    else:
        await update.message.reply_text("❌ Failed to download")

# run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 Bot Running...")
app.run_polling()
