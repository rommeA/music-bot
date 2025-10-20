import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === НАСТРОЙКИ ===
TOKEN = "8198145454:AAHv0ovmpBWvt3XYAPw1I43s4DKp9r_14zo"  # вставь токен от BotFather
ALLOWED_USERS = [293253701]  # сюда вставь Telegram user ID разрешённых пользователей

# Папка для музыки
DOWNLOAD_DIR = "music"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# === ФУНКЦИИ ===
def download_audio(query):
    """Скачивает первый трек с YouTube по запросу"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)
        entry = info['entries'][0]
        filename = ydl.prepare_filename(entry).rsplit('.', 1)[0] + '.mp3'
        return filename, entry['title']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return
    await update.message.reply_text("🎧 Привет! Отправь мне название песни или исполнителя.")

async def search_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("⛔ У тебя нет доступа к этому боту.")
        return

    query = update.message.text
    await update.message.reply_text(f"🔎 Ищу: {query}")

    try:
        filename, title = download_audio(query)
        await context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(filename, 'rb'), title=title)
        os.remove(filename)  # удалить файл после отправки, чтобы не засорять диск
    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Ошибка при поиске или скачивании. Попробуй другой запрос.")

# === ЗАПУСК ===
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_music))
    print("🚀 Бот запущен")
    app.run_polling()
