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

WAITING_NAME = "waiting_name"
WAITING_APPROVAL = "waiting_approval"
WAITING_LANGUAGE = "waiting_language"

MAX_FILE_SIZE_MB = 20
MAX_LANGUAGE_LENGTH = 50

# Almacenamiento en memoria
user_status = {}    # {user_id: "approved" | "pending" | "rejected"}
pending_users = {}  # {user_id: {"name": str}}

PRIVACY_NOTICE = (
    "🔒 *Aviso de privacidad*\n\n"
    "Los audios que envíes serán procesados por *Groq* (empresa con servidores en EEUU) "
    "para realizar la transcripción. El audio se elimina inmediatamente tras procesarse "
    "y no se almacena ningún dato de forma permanente.\n\n"
    "Al continuar aceptas este tratamiento de datos conforme al RGPD."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    status = user_status.get(user_id)

    if status == "approved":
        await update.message.reply_text("✅ Ya tienes acceso. ¡Envíame un audio!")
        return

    if status == "pending":
        await update.message.reply_text("⏳ Tu solicitud ya está pendiente de revisión. Te avisaré cuando sea aprobada.")
        return

    await update.message.reply_text(
        f"👋 Hola, soy un asistente de transcripción de audio.\n\n"
        f"{PRIVACY_NOTICE}\n\n"
        f"Para acceder necesito saber quién eres. ¿Cuál es tu *nombre y apellidos*?",
        parse_mode="Markdown",
    )
    context.user_data["state"] = WAITING_NAME


async def handle_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    status = user_status.get(user_id)

    if status == "pending":
        await update.message.reply_text("⏳ Tu solicitud está pendiente de aprobación. Te avisaré cuando sea revisada.")
        return
    elif status == "rejected":
        await update.message.reply_text("❌ Tu solicitud fue denegada. Contacta con el administrador.")
        return
    elif status != "approved":
        await update.message.reply_text("⚠️ Primero debes registrarte. Usa /start.")
        return

    message = update.message
    audio = message.voice or message.audio

    if audio.file_size and audio.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        size_mb = audio.file_size / (1024 * 1024)
        await message.reply_text(
            f"❌ El archivo es demasiado grande ({size_mb:.1f}MB). "
            f"El límite es {MAX_FILE_SIZE_MB}MB."
        )
        return

    duration = getattr(audio, "duration", None)
    duration_text = f" (~{duration}s)" if duration else ""
    status_msg = await message.reply_text(f"🎙️ Transcribiendo audio{duration_text}, un momento...")

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

    # Aprobación/rechazo de acceso (solo admin)
    if query.data.startswith("approve_") or query.data.startswith("reject_"):
        admin_id = os.getenv("ADMIN_TELEGRAM_ID")
        if str(query.from_user.id) != admin_id:
            await query.answer("No tienes permisos para esto.", show_alert=True)
            return

        action, target_id = query.data.split("_", 1)
        target_user_id = int(target_id)
        name = pending_users.get(target_user_id, {}).get("name", "Usuario desconocido")

        if action == "approve":
            user_status[target_user_id] = "approved"
            await context.bot.send_message(
                chat_id=target_user_id,
                text=(
                    "✅ *Tu acceso ha sido aprobado.* ¡Ya puedes enviarme audios!\n\n"
                    "Antes de empezar, ten en cuenta lo siguiente:\n\n"
                    "🔹 Tus audios se envían a *Groq* (servidores en EEUU) para la transcripción. "
                    "Se eliminan inmediatamente tras procesarse.\n"
                    "🔹 No se almacena ningún dato de forma permanente.\n"
                    "🔹 El servicio se ofrece sin garantías de disponibilidad ni de precisión.\n"
                    "🔹 El límite de archivo es de 20MB por audio.\n\n"
                    "📄 Puedes leer el disclaimer completo aquí:\n"
                    "https://github.com/xreche/audio-transcriber-bot/blob/master/docs/disclaimer.md"
                ),
                parse_mode="Markdown",
            )
            await query.edit_message_text(f"✅ Acceso aprobado para {name}.")
        else:
            user_status[target_user_id] = "rejected"
            await context.bot.send_message(
                chat_id=target_user_id,
                text="❌ Tu solicitud de acceso ha sido denegada.",
            )
            await query.edit_message_text(f"❌ Acceso denegado para {name}.")

        pending_users.pop(target_user_id, None)
        return

    # Traducción
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
    state = context.user_data.get("state")

    # Registro: esperando nombre
    if state == WAITING_NAME:
        name = update.message.text.strip()

        if len(name) < 3 or len(name) > 100:
            await update.message.reply_text("Por favor, introduce un nombre válido (entre 3 y 100 caracteres).")
            return

        user_id = update.effective_user.id
        pending_users[user_id] = {"name": name}
        user_status[user_id] = "pending"
        context.user_data["state"] = WAITING_APPROVAL

        await update.message.reply_text(
            f"✅ Gracias, {name}. Tu solicitud ha sido enviada. Te avisaré cuando sea revisada."
        )

        admin_id = os.getenv("ADMIN_TELEGRAM_ID")
        keyboard = [[
            InlineKeyboardButton("✅ Aceptar", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ Rechazar", callback_data=f"reject_{user_id}"),
        ]]
        await context.bot.send_message(
            chat_id=admin_id,
            text=f"🔔 *Nueva solicitud de acceso*\n\nNombre: *{name}*\nUser ID: `{user_id}`",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # Registro: esperando aprobación
    if state == WAITING_APPROVAL:
        await update.message.reply_text("⏳ Tu solicitud ya está en revisión. Te avisaremos pronto.")
        return

    # Traducción
    if state != WAITING_LANGUAGE:
        return

    language = update.message.text

    if len(language) > MAX_LANGUAGE_LENGTH:
        await update.message.reply_text(
            "❌ El idioma introducido es demasiado largo. Escribe simplemente el nombre (ej: inglés, francés)."
        )
        return

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
    admin_id = os.getenv("ADMIN_TELEGRAM_ID")

    if not token:
        raise ValueError("TELEGRAM_TOKEN no encontrado en las variables de entorno.")
    if not admin_id:
        raise ValueError("ADMIN_TELEGRAM_ID no encontrado en las variables de entorno.")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_audio))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("Bot iniciado y escuchando...")
    app.run_polling()
