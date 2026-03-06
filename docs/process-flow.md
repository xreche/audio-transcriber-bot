# Diagrama de Procesos

Flujo de ejecución completo del bot, incluyendo decisiones, estados y manejo de errores.

---

## Proceso principal

```mermaid
flowchart TD
    A([Inicio]) --> B[Cargar .env\nConfigurar logging]
    B --> C[Registrar handlers\nde Telegram]
    C --> D[Iniciar polling\nTelegram API]
    D --> E{Nuevo mensaje}

    E -->|/start| F[Enviar mensaje\nde bienvenida]
    F --> D

    E -->|Voz o audio| G[Descargar archivo\ntemp_.oga]
    G --> H{Descarga OK?}
    H -->|No| I[Notificar error\nal usuario]
    I --> D

    H -->|Sí| J[Enviar a\nGroq Whisper API]
    J --> K{Transcripción OK?}
    K -->|No| L[Notificar error\nal usuario]
    L --> M[Eliminar archivo\ntemporal]
    M --> D

    K -->|Sí| N[Enviar transcripción\nal usuario]
    N --> M
    N --> O[Preguntar si desea\ntraducir]
    O --> P{Respuesta}

    P -->|No, gracias| Q[Confirmar cancelación]
    Q --> D

    P -->|Sí, traducir| R[Solicitar idioma destino]
    R --> S[state = WAITING_LANGUAGE]
    S --> D

    E -->|Texto libre| T{state ==\nWAITING_LANGUAGE?}
    T -->|No| D
    T -->|Sí| U[Leer idioma destino]
    U --> V[Enviar a\nGroq LLM]
    V --> W{Traducción OK?}
    W -->|No| X[Notificar error\nal usuario]
    X --> Y[state = None]
    Y --> D
    W -->|Sí| Z[Enviar traducción\nal usuario]
    Z --> Y
```

---

## Gestión del estado de conversación

El bot mantiene el estado de cada conversación en `context.user_data`. El único estado activo es `WAITING_LANGUAGE`, que indica que el bot está esperando que el usuario escriba el idioma de destino.

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> Transcribiendo : Usuario envía audio
    Transcribiendo --> Idle : Error de transcripción
    Transcribiendo --> EsperandoDecision : Transcripción completada

    EsperandoDecision --> Idle : Usuario pulsa "No, gracias"
    EsperandoDecision --> EsperandoIdioma : Usuario pulsa "Sí, traducir"

    EsperandoIdioma --> Traduciendo : Usuario escribe idioma
    Traduciendo --> Idle : Traducción completada o error
```

---

## Ciclo de vida de un archivo de audio

```mermaid
flowchart LR
    A[Audio en\nTelegram] -->|getFile + download| B[temp_chatid_msgid.oga\nen disco local]
    B -->|open + read| C[Bytes enviados\na Groq Whisper]
    C -->|finally| D[os.remove\narchivo eliminado]
```

Los archivos temporales se eliminan siempre en el bloque `finally`, tanto si la transcripción tiene éxito como si falla, garantizando que no se acumulen en disco.
