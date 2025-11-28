from telegram.ext import CommandHandler, MessageHandler, ContextTypes, filters
from bot.memory import save_context, get_context
from bot.gemini import ask_gemini

async def start(update, context):
    await update.message.reply_text("Shalom, hijo mío. No prometo sabiduría, pero sarcasmo sí.")

async def on_message(update, context):
    user = update.message.from_user.id
    text = update.message.text

    save_context(user, text)
    context_data = get_context(user)

    reply = await ask_gemini(text, context_data)
    await update.message.reply_text(reply)

def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
