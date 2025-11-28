import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder
from bot.bot_logic import register_handlers

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

app = FastAPI()

tg_app = ApplicationBuilder().token(TOKEN).build()
register_handlers(tg_app)


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)
    return {"ok": True}


@app.get("/")
def home():
    return {"status": "running"}
