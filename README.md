# Audio Transcriber Bot

Bot de Telegram que transcribe mensajes de voz y archivos de audio a texto en cualquier idioma, con opción de traducción.

## Demo

1. Envía un mensaje de voz o archivo de audio al bot
2. Recibes la transcripción en texto
3. El bot te pregunta si quieres traducirlo
4. Si dices que sí, escribe el idioma destino (ej: *inglés*, *japonés*, *alemán*...)

## Stack

| Componente | Tecnología |
|---|---|
| Bot | [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) |
| Transcripción | [Groq Whisper large-v3-turbo](https://console.groq.com/docs/speech-text) |
| Traducción | [Groq API](https://groq.com) — Llama 3.1 8B |

Todo gratuito dentro de los límites de la capa free de Groq.

## Requisitos previos

- Python 3.11+
- Token de bot de Telegram → [@BotFather](https://t.me/BotFather)
- API Key de Groq → [console.groq.com](https://console.groq.com) (gratuita)

## Instalación local

```bash
git clone https://github.com/xreche/audio-transcriber-bot.git
cd audio-transcriber-bot

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install -r requirements.txt
```

## Configuración

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```
TELEGRAM_TOKEN=tu_token_aqui
GROQ_API_KEY=tu_api_key_aqui
```

## Ejecución

```bash
python main.py
```

El bot estará activo mientras el proceso esté en ejecución.

## Despliegue en producción

Para que el bot funcione 24/7 sin depender de tu máquina, despliégalo en [Railway](https://railway.app):

1. Crea un nuevo proyecto en Railway → **Deploy from GitHub repo**
2. Selecciona este repositorio
3. En **Variables**, añade `TELEGRAM_TOKEN` y `GROQ_API_KEY`
4. En **Settings → Start command**, pon `python main.py`
