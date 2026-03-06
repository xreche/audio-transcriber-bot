# Diagrama de Clases y Módulos

El proyecto está organizado en módulos Python. No utiliza clases orientadas a objetos de forma explícita, sino funciones y estado gestionado por `python-telegram-bot`. El diagrama refleja la estructura real de módulos, funciones y dependencias.

---

## Diagrama

```mermaid
classDiagram

    class main {
        +run_bot()
        load_dotenv()
        configure_logging()
    }

    class bot {
        -WAITING_NAME: str
        -WAITING_APPROVAL: str
        -WAITING_LANGUAGE: str
        -MAX_FILE_SIZE_MB: int
        -MAX_LANGUAGE_LENGTH: int
        -user_status: dict
        -pending_users: dict
        -PRIVACY_NOTICE: str
        +start(update, context)
        +handle_audio(update, context)
        +handle_callback(update, context)
        +handle_text(update, context)
        +run_bot()
    }

    class transcriber {
        -_client: AsyncGroq
        -_get_client() AsyncGroq
        +transcribe_audio(file_path: str) str
    }

    class translator {
        -_client: AsyncGroq
        -_get_client() AsyncGroq
        +translate_text(text: str, target_language: str) str
    }

    class GroqAPI {
        <<external>>
        +audio.transcriptions.create()
        +chat.completions.create()
    }

    class TelegramAPI {
        <<external>>
        +getUpdates()
        +sendMessage()
        +getFile()
        +editMessageText()
        +answerCallbackQuery()
        +deleteMessage()
    }

    main --> bot : llama run_bot()
    bot --> transcriber : llama transcribe_audio()
    bot --> translator : llama translate_text()
    transcriber --> GroqAPI : whisper-large-v3-turbo
    translator --> GroqAPI : llama-3.1-8b-instant
    bot --> TelegramAPI : python-telegram-bot
```

---

## Descripción de módulos

### `main.py`
Punto de entrada de la aplicación. Carga las variables de entorno desde `.env`, configura el sistema de logging y arranca el bot.

### `src/bot.py`
Núcleo del bot. Gestiona el flujo completo de conversación, incluyendo registro de usuarios, aprobación de acceso, transcripción y traducción.

**Estado global en memoria:**

| Variable | Tipo | Descripción |
|---|---|---|
| `user_status` | `dict` | `{user_id: "approved" \| "pending" \| "rejected"}` |
| `pending_users` | `dict` | `{user_id: {"name": str}}` — solicitudes en espera de revisión |

**Estado por conversación (`context.user_data`):**

| Variable | Tipo | Descripción |
|---|---|---|
| `state` | `str \| None` | Estado del usuario: `WAITING_NAME`, `WAITING_APPROVAL`, `WAITING_LANGUAGE` o `None` |
| `last_transcription` | `str` | Última transcripción generada, disponible para traducción |

**Handlers registrados:**

| Handler | Trigger | Función |
|---|---|---|
| `CommandHandler("start")` | `/start` | `start()` — aviso de privacidad y flujo de registro |
| `MessageHandler(VOICE \| AUDIO)` | Audio o voz | `handle_audio()` — valida acceso, tamaño y transcribe |
| `CallbackQueryHandler` | Botones inline | `handle_callback()` — traducción y aprobación de admin |
| `MessageHandler(TEXT)` | Texto libre | `handle_text()` — nombre, espera o idioma según estado |

**Variables de entorno requeridas:**

| Variable | Descripción |
|---|---|
| `TELEGRAM_TOKEN` | Token del bot (BotFather) |
| `GROQ_API_KEY` | API key de Groq |
| `ADMIN_TELEGRAM_ID` | User ID numérico del administrador en Telegram |

### `src/transcriber.py`
Gestiona la transcripción de audio. Envía el archivo a la API de Groq (modelo `whisper-large-v3-turbo`) y retorna el texto. El cliente `AsyncGroq` se instancia una sola vez (singleton).

### `src/translator.py`
Gestiona la traducción de texto. Envía el texto y el idioma destino a Groq Chat Completions (modelo `llama-3.1-8b-instant`) con un prompt de sistema que instruye al LLM a devolver únicamente la traducción. El cliente `AsyncGroq` se instancia una sola vez (singleton).
