# Audio Transcriber Bot

Bot de Telegram que transcribe mensajes de voz y archivos de audio a texto en cualquier idioma, con opción de traducción. El acceso está restringido: cada nuevo usuario debe registrarse y ser aprobado por el administrador.

## Demo

1. Envía `/start` al bot y acepta el aviso de privacidad
2. Proporciona tu nombre y apellidos para solicitar acceso
3. El administrador aprueba o rechaza la solicitud
4. Una vez aprobado, envía mensajes de voz o archivos de audio
5. Recibes la transcripción en texto
6. El bot te pregunta si quieres traducirlo a otro idioma

## Stack

| Componente | Tecnología |
|---|---|
| Bot | [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v21 |
| Transcripción | [Groq Whisper large-v3-turbo](https://console.groq.com/docs/speech-text) |
| Traducción | [Groq API](https://groq.com) — Llama 3.1 8B Instant |

Todo gratuito dentro de los límites de la capa free de Groq.

## Requisitos previos

- Python 3.12
- Token de bot de Telegram → [@BotFather](https://t.me/BotFather)
- API Key de Groq → [console.groq.com](https://console.groq.com) (gratuita)
- Tu ID de usuario de Telegram (para actuar como administrador)

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
ADMIN_TELEGRAM_ID=tu_id_numerico_de_telegram
```

> Para obtener tu ID de Telegram, envía un mensaje a [@userinfobot](https://t.me/userinfobot).

## Ejecución

```bash
python main.py
```

El bot estará activo mientras el proceso esté en ejecución.

## Despliegue en producción

Para que el bot funcione 24/7 sin depender de tu máquina, despliégalo en [Railway](https://railway.app):

1. Crea un nuevo proyecto en Railway → **Deploy from GitHub repo**
2. Selecciona este repositorio
3. En **Variables**, añade `TELEGRAM_TOKEN`, `GROQ_API_KEY` y `ADMIN_TELEGRAM_ID`
4. Railway detecta el `Procfile` y ejecuta `python main.py` automáticamente

## Documentación

La documentación técnica completa está en la carpeta [`docs/`](docs/README.md):

- [Casos de uso](docs/use-cases.md)
- [Diagrama de clases](docs/class-diagram.md)
- [Diagramas de secuencia](docs/sequence-diagrams.md)
- [Diagrama de procesos](docs/process-flow.md)
- [Disclaimer y decisiones de diseño](docs/disclaimer.md)
