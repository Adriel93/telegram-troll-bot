import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder
from bot.bot_logic import register_handlers

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
register_handlers(app)

async def handler(request):
    body = await request.json()

    update = Update.de_json(body, app.bot)
    await app.initialize()
    await app.process_update(update)

    return {
        "statusCode": 200,
        "body": json.dumps({"ok": True})
    }
