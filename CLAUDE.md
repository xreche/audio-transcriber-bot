# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el bot
python main.py
```

## Arquitectura

Bot de Telegram para transcripción de audio a texto, con traducción opcional y flujo de registro/aprobación de usuarios.

```
main.py              # Entry point: carga .env, configura logging, arranca el bot
src/
  bot.py             # Handlers de Telegram, máquina de estados, flujo completo
  transcriber.py     # Transcripción con Groq Whisper large-v3-turbo (AsyncGroq)
  translator.py      # Traducción con Groq Llama 3.1 8B Instant (AsyncGroq)
docs/                # Documentación técnica completa (casos de uso, diagramas, disclaimer)
```

### Flujo principal

1. Nuevo usuario → `/start` → aviso de privacidad → solicita nombre y apellidos
2. Bot notifica al admin con botones Aceptar/Rechazar (inline keyboard)
3. Admin aprueba → usuario puede enviar audios
4. Usuario envía audio (voz o archivo) → `handle_audio` valida acceso y tamaño (<= 20MB)
5. Bot descarga el audio como archivo temporal `temp_{chat_id}_{msg_id}.oga`
6. `transcribe_audio` envía el archivo a Groq Whisper API
7. Se muestra la transcripción y se pregunta si quiere traducir (InlineKeyboard)
8. Si acepta → estado `WAITING_LANGUAGE` → siguiente texto se interpreta como idioma → `translate_text` via Groq

### Estado gestionado en memoria

- `user_status`: dict `{user_id: "approved"|"pending"|"rejected"}` — estado global
- `pending_users`: dict `{user_id: {"name": str}}` — solicitudes pendientes
- `context.user_data["state"]`: `WAITING_NAME | WAITING_APPROVAL | WAITING_LANGUAGE | None` — estado por conversación
- `context.user_data["last_transcription"]`: última transcripción, disponible para traducción

### Variables de entorno (.env)

- `TELEGRAM_TOKEN`: token del bot (BotFather)
- `GROQ_API_KEY`: API key de Groq (transcripción + traducción)
- `ADMIN_TELEGRAM_ID`: ID numérico de Telegram del administrador — **nunca en el repo**
