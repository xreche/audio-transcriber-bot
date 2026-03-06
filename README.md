# Audio Transcriber Bot

Bot de Telegram que transcribe mensajes de voz y archivos de audio a texto en cualquier idioma, con opción de traducción.

## Cómo funciona

1. Envía un mensaje de voz o archivo de audio al bot
2. El bot te devuelve la transcripción en texto
3. Puedes pedirle que lo traduzca a cualquier idioma

## Stack

- **Transcripción:** [OpenAI Whisper](https://github.com/openai/whisper) (local, gratuito)
- **Traducción:** [Groq API](https://groq.com) con Llama 3 (gratuito)
- **Bot:** python-telegram-bot

## Requisitos previos

- Python 3.11+
- [ffmpeg](https://ffmpeg.org/download.html) instalado en el sistema (necesario para Whisper)
- Token de bot de Telegram (via [@BotFather](https://t.me/BotFather))
- API Key de Groq (gratuita en [console.groq.com](https://console.groq.com))

## Instalación

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

Edita `.env` y añade tus credenciales:

```
TELEGRAM_TOKEN=tu_token_aqui
GROQ_API_KEY=tu_api_key_aqui
```

## Ejecución

```bash
python main.py
```
