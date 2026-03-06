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

Bot de Telegram para transcripción de audio a texto, con traducción opcional.

```
main.py              # Entry point: carga .env, configura logging, arranca el bot
src/
  bot.py             # Handlers de Telegram y flujo de conversación
  transcriber.py     # Transcripción con Whisper local (async via asyncio.to_thread)
  translator.py      # Traducción con Groq API (AsyncGroq)
```

### Flujo principal

1. Usuario envía audio (voz o archivo) → `handle_audio` en `bot.py`
2. Se descarga el audio como archivo temporal `temp_{chat_id}_{msg_id}.ogg`
3. `transcribe_audio` llama a Whisper en un thread separado para no bloquear el event loop
4. Se muestra la transcripción y se pregunta si quiere traducir (InlineKeyboard)
5. Si acepta, se guarda estado `WAITING_LANGUAGE` en `context.user_data`
6. El siguiente mensaje de texto se interpreta como idioma destino → `translate_text` via Groq

### Variables de entorno (.env)

- `TELEGRAM_TOKEN`: token del bot (BotFather)
- `GROQ_API_KEY`: API key de Groq para traducción

### Modelo Whisper

Se usa el modelo `base` (equilibrio velocidad/precisión). Se carga en memoria la primera vez y se reutiliza. Para cambiar el modelo: `transcriber.py` → `_get_model()`.
