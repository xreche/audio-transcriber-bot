import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from src.transcriber import transcribe_audio
from src.translator import translate_text

logger = logging.getLogger(__name__)

WAITING_LANGUAGE = "waiting_language"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola! Soy tu asistente de transcripción de audio.\n\n"
        "Envíame cualquier mensaje de voz o archivo de audio y te lo convierto a texto, "
        "en cualquier idioma."
    )


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    status_msg = await message.reply_text("🎙️ Transcribiendo audio, un momento...")

    audio = message.voice or message.audio
    file = await audio.get_file()
    file_path = f"temp_{message.chat_id}_{message.message_id}.ogg"
    await file.download_to_drive(file_path)

    try:
        text = await transcribe_audio(file_path)
        await status_msg.delete()
        await message.reply_text(f"📝 *Transcripción:*\n\n{text}", parse_mode="Markdown")

        context.user_data["last_transcription"] = text
        context.user_data["state"] = None

        keyboard = [[
            InlineKeyboardButton("✅ Sí, traducir", callback_data="ask_translate"),
            InlineKeyboardButton("❌ No, gracias", callback_data="no_translate"),
        ]]
        await message.reply_text(
            "¿Quieres traducirlo a otro idioma?",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    except Exception as e:
        logger.error(f"Error transcribiendo audio: {e}")
        await status_msg.edit_text("❌ Error al transcribir el audio. Inténtalo de nuevo.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "no_translate":
        await query.edit_message_text("De acuerdo 👍")
        context.user_data["state"] = None

    elif query.data == "ask_translate":
        await query.edit_message_text(
            "¿A qué idioma quieres traducirlo?\n"
            "_(Escribe el idioma, ej: inglés, francés, alemán, japonés...)_",
            parse_mode="Markdown",
        )
        context.user_data["state"] = WAITING_LANGUAGE


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != WAITING_LANGUAGE:
        return

    language = update.message.text
    text = context.user_data.get("last_transcription", "")

    if not text:
        await update.message.reply_text("No encontré ninguna transcripción reciente. Envía un audio primero.")
        return

    status_msg = await update.message.reply_text(f"🌍 Traduciendo al {language}...")

    try:
        translated = await translate_text(text, language)
        await status_msg.edit_text(
            f"🌍 *Traducción al {language}:*\n\n{translated}",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Error traduciendo: {e}")
        await status_msg.edit_text("❌ Error al traducir. Inténtalo de nuevo.")
    finally:
        context.user_data["state"] = None


def run_bot():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_TOKEN no encontrado en las variables de entorno.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot iniciado y escuchando...")
    app.run_polling()
