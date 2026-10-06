import os
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_USER = os.environ["GITHUB_USER"]
RENDER_URL = os.environ["RENDER_EXTERNAL_URL"]
PORT = int(os.environ.get("PORT", 10000))
REPO = "spotify-downloader"


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/actions/workflows/download.yml/dispatches"
    r = requests.post(
        url,
        json={"ref": "master", "inputs": {"query": query}},
        headers=headers,
    )
    if r.status_code == 204:
        await update.message.reply_text(
            f"✅ Descarga iniciada: {query}\nRevisa GitHub > Actions > artifacts en 1-2 min."
        )
    else:
        await update.message.reply_text(f"❌ Error {r.status_code}: {r.text[:200]}")


if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"{RENDER_URL}/{TELEGRAM_TOKEN}",
    )
