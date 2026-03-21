import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# download function
def download_video(url):
    ydl_opts = {
        'outtmpl': 'video.%(ext)s',
        'format': 'best',
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return "video.mp4"
    except Exception as e:
        print("Download error:", e)
        return None

# handler
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return  # ignore non-text safely

    url = update.message.text.strip()

    await update.message.reply_text("⬇️ Downloading...")

    file = download_video(url)

    if file and os.path.exists(file):
        await update.message.reply_text("📤 Sending file...")
        try:
            await update.message.reply_document(document=open(file, "rb"))
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
        os.remove(file)
    else:
        await update.message.reply_text("❌ Download failed")

# run
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("🚀 Bot Running...")
app.run_polling()
