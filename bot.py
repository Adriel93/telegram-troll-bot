import os
import logging
import asyncio
import json
import random
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from upstash_redis.asyncio import Redis

# -------------------------------------------------------
# CONFIGURACIONES
# -------------------------------------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Upstash Redis (poner la URL y token de tu instancia)
REDIS_URL = os.getenv("UPSTASH_REDIS_URL")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_TOKEN")
redis = Redis(url=REDIS_URL, token=REDIS_TOKEN)

logging.basicConfig(level=logging.INFO)


# -------------------------------------------------------
# FUNCION PARA GENERAR RESPUESTA CON GEMINI
# -------------------------------------------------------
async def ask_gemini(prompt: str) -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{url}?key={GEMINI_API_KEY}", json=payload, headers=headers) as r:
            data = await r.json()
            try:
                return data["candidates"][0]["content"]["parts"][0]["text"]
            except:
                return "El Espíritu Santo me dijo que no entendí nada. Intenta otra vez 😅"


# -------------------------------------------------------
# GUARDAR MEMORIA POR USUARIO
# -------------------------------------------------------
async def save_memory(user_id: int, message: str):
    key = f"user:{user_id}:history"

    # guardamos 10 mensajes como máximo
    await redis.lpush(key, message)
    await redis.ltrim(key, 0, 9)


async def load_memory(user_id: int):
    key = f"user:{user_id}:history"
    mem = await redis.lrange(key, 0, 9)
    if not mem:
        return ""
    return "\n".join(mem)


# -------------------------------------------------------
# GENERAR RESPUESTA SARCASTICA–CRISTIANA
# -------------------------------------------------------
async def generate_response(user_id: int, user_message: str):
    memory = await load_memory(user_id)

    estilo = (
        "Responde como un bot cristiano sarcástico, troll light, irónico pero nunca grosero. "
        "De vez en cuando lanza una frase bíblica con tono sarcástico tipo: "
        "'Hermano, hasta Jonas entendió más rápido que tú'. "
        "Siempre mantiene humor sano, irónico, pero positivo."
    )

    prompt = f"""
Eres un bot cristiano irónico.
Historial del usuario:
{memory}

Mensaje del usuario:
{user_message}

Responde en español, con humor irónico, un toque troll suave,
pero con sabiduría cristiana ocasional.
"""

    reply = await ask_gemini(prompt)

    # guardar mensaje del usuario y del bot
    await save_memory(user_id, f"User: {user_message}")
    await save_memory(user_id, f"Bot: {reply}")

    return reply


# -------------------------------------------------------
# HANDLER PRINCIPAL
# -------------------------------------------------------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    response = await generate_response(user_id, user_text)
    await update.message.reply_text(response)


# -------------------------------------------------------
# MAIN
# -------------------------------------------------------
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    await app.run_polling()


if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))
    app.run_polling()

