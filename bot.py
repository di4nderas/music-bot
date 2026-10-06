import os
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_USER = os.environ["GITHUB_USER"]
REPO = "spotify-downloader"

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    chat_id = update.message.chat_id

    await update.message.reply_text(f"⏳ Descargando: {query}")

    # Disparar workflow
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/actions/workflows/download.yml/dispatches"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"ref": "master", "inputs": {"query": query}}
    requests.post(url, json=data, headers=headers)

    # Esperar que termine
    await update.message.reply_text("⏳ Esperando que GitHub Actions termine (1-2 min)...")
    time.sleep(90)

    # Buscar el artifact
    runs_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/actions/runs"
    runs = requests.get(runs_url, headers=headers).json()
    run_id = runs["workflow_runs"][0]["id"]

    artifacts_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/actions/runs/{run_id}/artifacts"
    artifacts = requests.get(artifacts_url, headers=headers).json()

    if artifacts["total_count"] == 0:
        await update.message.reply_text("❌ No se encontró el archivo.")
        return

    download_url = artifacts["artifacts"][0]["archive_download_url"]
    mp3_data = requests.get(download_url, headers=headers)

    await context.bot.send_document(chat_id=chat_id, document=mp3_data.content, filename="musica.zip")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
app.run_polling()
