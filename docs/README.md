# Documentación Técnica — Audio Transcriber Bot

Índice de la documentación técnica del proyecto.

## Contenido

| Documento | Descripción |
|---|---|
| [Casos de uso](use-cases.md) | Actores, casos de uso e interacciones del sistema |
| [Diagrama de clases](class-diagram.md) | Estructura de módulos, clases y dependencias |
| [Diagramas de secuencia](sequence-diagrams.md) | Flujo de mensajes entre componentes |
| [Diagrama de procesos](process-flow.md) | Flujo de ejecución y decisiones del bot |
| [Disclaimer](disclaimer.md) | Por qué Telegram, verificación de usuarios y marco legal |

## Visión general del sistema

Audio Transcriber Bot es un bot de Telegram que permite a usuarios registrados y aprobados transcribir mensajes de voz o archivos de audio a texto en cualquier idioma, con opción de traducción posterior. El acceso requiere registro y aprobación por parte del administrador.

### Componentes externos

```
┌─────────────────────────────────────────────────┐
│                   USUARIO                        │
│              (cliente Telegram)                  │
└──────────────────────┬──────────────────────────┘
                       │ mensajes de voz / audio
                       ▼
┌─────────────────────────────────────────────────┐
│              TELEGRAM API                        │
│         (entrega de mensajes, polling)           │
└──────────────────────┬──────────────────────────┘
                       │ updates
                       ▼
┌─────────────────────────────────────────────────┐
│            AUDIO TRANSCRIBER BOT                 │
│                 (este proyecto)                  │
└──────────┬──────────────────────────────────────┘
           │                      │
           ▼                      ▼
┌──────────────────┐   ┌──────────────────────────┐
│   GROQ WHISPER   │   │       GROQ LLM           │
│ (transcripción)  │   │  (traducción — Llama 3.1) │
└──────────────────┘   └──────────────────────────┘
```
