# Diagramas de Secuencia

---

## SD1 — Transcripción de audio

Flujo completo desde que el usuario envía un audio hasta que recibe la transcripción.

```mermaid
sequenceDiagram
    actor Usuario
    participant Telegram
    participant Bot
    participant Groq Whisper

    Usuario->>Telegram: Envía mensaje de voz / archivo de audio
    Telegram->>Bot: Update (VOICE | AUDIO)

    Bot->>Telegram: sendMessage("🎙️ Transcribiendo audio...")

    Bot->>Telegram: getFile(file_id)
    Telegram-->>Bot: file_path

    Bot->>Telegram: GET /file/{file_path}
    Telegram-->>Bot: Descarga archivo .oga

    Bot->>Groq Whisper: audio.transcriptions.create(archivo, model="whisper-large-v3-turbo")
    Groq Whisper-->>Bot: { text: "transcripción..." }

    Bot->>Telegram: deleteMessage (mensaje "Transcribiendo...")
    Bot->>Telegram: sendMessage("📝 Transcripción:\n\n{texto}")
    Bot->>Telegram: sendMessage("¿Quieres traducirlo?", inline_keyboard)

    Telegram-->>Usuario: Muestra transcripción + botones
```

---

## SD2 — Traducción de transcripción

Flujo desde que el usuario acepta traducir hasta recibir el resultado.

```mermaid
sequenceDiagram
    actor Usuario
    participant Telegram
    participant Bot
    participant Groq LLM

    Usuario->>Telegram: Pulsa botón "✅ Sí, traducir"
    Telegram->>Bot: CallbackQuery("ask_translate")

    Bot->>Telegram: editMessageText("¿A qué idioma?")
    Telegram-->>Usuario: Muestra pregunta de idioma

    Note over Bot: state = WAITING_LANGUAGE

    Usuario->>Telegram: Escribe "inglés"
    Telegram->>Bot: Message(text="inglés")

    Bot->>Telegram: sendMessage("🌍 Traduciendo al inglés...")

    Bot->>Groq LLM: chat.completions.create(model="llama-3.1-8b-instant", prompt)
    Groq LLM-->>Bot: { text: "traducción..." }

    Bot->>Telegram: editMessageText("🌍 Traducción al inglés:\n\n{texto}")
    Telegram-->>Usuario: Muestra traducción

    Note over Bot: state = None
```

---

## SD3 — Cancelación de traducción

```mermaid
sequenceDiagram
    actor Usuario
    participant Telegram
    participant Bot

    Usuario->>Telegram: Pulsa botón "❌ No, gracias"
    Telegram->>Bot: CallbackQuery("no_translate")

    Bot->>Telegram: editMessageText("De acuerdo 👍")
    Telegram-->>Usuario: Confirmación

    Note over Bot: state = None
```

---

## SD4 — Flujo de error en transcripción

```mermaid
sequenceDiagram
    actor Usuario
    participant Telegram
    participant Bot
    participant Groq Whisper

    Usuario->>Telegram: Envía mensaje de voz
    Telegram->>Bot: Update (VOICE)

    Bot->>Telegram: sendMessage("🎙️ Transcribiendo audio...")
    Bot->>Groq Whisper: audio.transcriptions.create(...)
    Groq Whisper-->>Bot: Error (timeout / credenciales inválidas / límite excedido)

    Bot->>Telegram: editMessageText("❌ Error al transcribir el audio. Inténtalo de nuevo.")
    Telegram-->>Usuario: Mensaje de error

    Note over Bot: Archivo temporal eliminado (finally)
```
