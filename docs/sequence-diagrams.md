# Diagramas de Secuencia

---

## SD1 — Registro de usuario nuevo

Flujo completo desde que un nuevo usuario escribe `/start` hasta que recibe la aprobación o rechazo del administrador.

```mermaid
sequenceDiagram
    actor Usuario
    actor Administrador
    participant Telegram
    participant Bot

    Usuario->>Telegram: /start
    Telegram->>Bot: CommandUpdate("start")

    Bot->>Telegram: sendMessage(aviso de privacidad + petición de nombre)
    Telegram-->>Usuario: Muestra aviso y pide nombre

    Note over Bot: state = WAITING_NAME

    Usuario->>Telegram: Escribe "Nombre Apellidos"
    Telegram->>Bot: Message(text="Nombre Apellidos")

    Bot->>Telegram: sendMessage("Solicitud enviada, espera revisión")
    Telegram-->>Usuario: Confirmación de envío

    Note over Bot: user_status = "pending", state = WAITING_APPROVAL

    Bot->>Telegram: sendMessage(admin_id, solicitud + botones Aceptar/Rechazar)
    Telegram-->>Administrador: Notificación con botones

    Administrador->>Telegram: Pulsa "✅ Aceptar"
    Telegram->>Bot: CallbackQuery("approve_{user_id}")

    Bot->>Telegram: sendMessage(usuario, "✅ Acceso aprobado")
    Telegram-->>Usuario: Notificación de aprobación

    Bot->>Telegram: editMessageText(admin, "✅ Acceso aprobado para Nombre Apellidos")
    Telegram-->>Administrador: Confirmación

    Note over Bot: user_status = "approved"
```

---

## SD2 — Transcripción de audio

Flujo completo desde que un usuario aprobado envía un audio hasta que recibe la transcripción.

```mermaid
sequenceDiagram
    actor Usuario
    participant Telegram
    participant Bot
    participant Groq Whisper

    Usuario->>Telegram: Envía mensaje de voz / archivo de audio
    Telegram->>Bot: Update (VOICE | AUDIO)

    Note over Bot: Verifica user_status == "approved"
    Note over Bot: Verifica file_size <= 20MB

    Bot->>Telegram: sendMessage("🎙️ Transcribiendo audio (~{duración}s)...")

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

## SD3 — Traducción de transcripción

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

    Note over Bot: Valida len("inglés") <= 50 caracteres

    Bot->>Telegram: sendMessage("🌍 Traduciendo al inglés...")

    Bot->>Groq LLM: chat.completions.create(model="llama-3.1-8b-instant", prompt)
    Groq LLM-->>Bot: { text: "traducción..." }

    Bot->>Telegram: editMessageText("🌍 Traducción al inglés:\n\n{texto}")
    Telegram-->>Usuario: Muestra traducción

    Note over Bot: state = None
```

---

## SD4 — Cancelación de traducción

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

## SD5 — Rechazo por archivo demasiado grande

```mermaid
sequenceDiagram
    actor Usuario
    participant Telegram
    participant Bot

    Usuario->>Telegram: Envía archivo de audio > 20MB
    Telegram->>Bot: Update (AUDIO)

    Note over Bot: file_size > 20 * 1024 * 1024

    Bot->>Telegram: sendMessage("❌ El archivo es demasiado grande (X.XMB). Límite: 20MB.")
    Telegram-->>Usuario: Mensaje de error
```

---

## SD6 — Error en transcripción

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
