# Diagrama de Procesos

Flujo de ejecución completo del bot, incluyendo registro de usuarios, validaciones, transcripción, traducción y manejo de errores.

---

## Proceso principal

```mermaid
flowchart TD
    A([Inicio]) --> B[Cargar .env\nConfigurar logging]
    B --> C[Verificar TELEGRAM_TOKEN\ny ADMIN_TELEGRAM_ID]
    C --> D[Registrar handlers\nde Telegram]
    D --> E[Iniciar polling\nTelegram API]
    E --> F{Nuevo mensaje}

    F -->|/start| G{Estado del usuario}
    G -->|approved| H[Informar que puede\nenviar audios]
    G -->|pending| I[Informar que está\nen revisión]
    G -->|nuevo| J[Mostrar aviso de privacidad\nPedir nombre y apellidos]
    J --> K[state = WAITING_NAME]
    H --> E
    I --> E
    K --> E

    F -->|Texto libre| L{state?}
    L -->|WAITING_NAME| M[Validar nombre\n3-100 caracteres]
    M -->|Inválido| N[Pedir corrección]
    N --> E
    M -->|Válido| O[Guardar en pending_users\nuser_status = pending]
    O --> P[Notificar al admin\nbotones Aceptar/Rechazar]
    O --> Q[Informar al usuario\nque espere]
    P --> E

    L -->|WAITING_APPROVAL| R[Decir que espere]
    R --> E

    L -->|WAITING_LANGUAGE| S[Validar idioma\nmáx 50 caracteres]
    S -->|Inválido| T[Mensaje de error]
    T --> E
    S -->|Válido| U[Enviar a Groq LLM]
    U --> V{Traducción OK?}
    V -->|No| W[Notificar error]
    W --> E
    V -->|Sí| X[Enviar traducción\nal usuario]
    X --> E

    F -->|Voz o audio| Y{Usuario aprobado?}
    Y -->|pending| Z[Informar que espere]
    Y -->|rejected| AA[Informar denegación]
    Y -->|no registrado| AB[Indicar que use /start]
    Z --> E
    AA --> E
    AB --> E

    Y -->|approved| AC{Tamaño\n<= 20MB?}
    AC -->|No| AD[Rechazar con\ntamaño del archivo]
    AD --> E
    AC -->|Sí| AE[Descargar audio\ntemp_.oga]
    AE --> AF[Enviar a\nGroq Whisper API]
    AF --> AG{Transcripción OK?}
    AG -->|No| AH[Notificar error]
    AH --> AI[Eliminar archivo temporal]
    AI --> E
    AG -->|Sí| AJ[Enviar transcripción\nal usuario]
    AJ --> AI
    AJ --> AK[Preguntar si desea\ntraducir]
    AK --> E

    F -->|Callback inline| AL{Tipo de callback}
    AL -->|approve_ o reject_| AM{Es el admin?}
    AM -->|No| AN[Rechazar acción]
    AN --> E
    AM -->|Sí| AO{Acción}
    AO -->|approve| AP[user_status = approved\nNotificar al usuario]
    AO -->|reject| AQ[user_status = rejected\nNotificar al usuario]
    AP --> E
    AQ --> E
    AL -->|ask_translate| AR[state = WAITING_LANGUAGE\nPedir idioma]
    AL -->|no_translate| AS[Confirmar cancelación\nstate = None]
    AR --> E
    AS --> E
```

---

## Gestión del estado de conversación

El bot gestiona dos tipos de estado:

1. **`user_status`** (global, en memoria): indica si el usuario está aprobado, pendiente o rechazado
2. **`context.user_data["state"]`** (por conversación): indica en qué paso del flujo está el usuario

```mermaid
stateDiagram-v2
    [*] --> Nuevo

    Nuevo --> EsperandoNombre : /start (usuario desconocido)
    EsperandoNombre --> EsperandoPendiente : Envía nombre válido
    EsperandoPendiente --> Aprobado : Admin pulsa Aceptar
    EsperandoPendiente --> Rechazado : Admin pulsa Rechazar

    Aprobado --> Transcribiendo : Envía audio
    Transcribiendo --> Aprobado : Error de transcripción
    Transcribiendo --> EsperandoDecision : Transcripción completada

    EsperandoDecision --> Aprobado : Pulsa "No, gracias"
    EsperandoDecision --> EsperandoIdioma : Pulsa "Sí, traducir"

    EsperandoIdioma --> Traduciendo : Escribe idioma válido
    Traduciendo --> Aprobado : Traducción completada o error

    Rechazado --> [*]
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
