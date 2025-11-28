import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from upstash_redis.asyncio import Redis

# ==========================
# CONFIGURACIÓN DEL BOT
# ==========================

TELEGRAM_TOKEN = "TU_TOKEN_DE_TELEGRAM"
OPENAI_API_KEY = "TU_API_KEY_OPENAI"

# Upstash Redis (✔ correcto, sin AUTH duplicado)
redis = Redis(
    url="https://adequate-ape-22293.upstash.io",   # ← pon tu URL AQUÍ
    token="AVcVAAIncDI2NTQzMmUzYjAzZjA0YmViYjU2ZDBhNDQ4Zjg1MDMwMHAyMjIyOTM"        # ← pon tu TOKEN AQUÍ
)

# ==========================
# LOGGING
# ==========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ==========================
# GESTIÓN DE MEMORIA
# ==========================

async def save_memory(user_id, text):
    key = f"user:{user_id}:memory"
    await redis.lpush(key, text)
    await redis.ltrim(key, 0, 9)  # guarda solo 10 mensajes


async def load_memory(user_id):
    key = f"user:{user_id}:memory"
    mem = await redis.lrange(key, 0, 9)
    return mem or []


# ==========================
# OPENAI – RESPUESTA
# ==========================

import httpx

async def generate_response(user_id, text):
    memory = await load_memory(user_id)

    prompt = (
        "Eres un asistente conversacional. Aquí está la conversación reciente:\n\n"
        + "\n".join([f"- {m}" for m in memory])
        + f"\n\nUsuario: {text}\nAsistente:"
    )

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
            },
        )

    answer = r.json()["choices"][0]["message"]["content"]

    await save_memory(user_id, text)
    await save_memory(user_id, answer)

    return answer


# ==========================
# HANDLER DE MENSAJES
# ==========================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        reply = await generate_response(user_id, text)
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"ERROR en handler: {e}")
        await update.message.reply_text("Ocurrió un error, intenta nuevamente.")


# ==========================
# MAIN LOOP (getUpdates)
# ==========================

async def main():
    logger.info("Iniciando bot...")

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
