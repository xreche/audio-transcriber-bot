# Disclaimer y Decisiones de Diseño

Este documento explica las decisiones tomadas durante el desarrollo del bot: por qué se eligió Telegram, por qué se requiere verificación de usuario, y qué implica legalmente el uso del servicio.

---

## Por qué Telegram y no WhatsApp

La primera opción considerada fue WhatsApp, dado que es la plataforma de mensajería más extendida en España. Sin embargo, el desarrollo de bots en WhatsApp presenta barreras de entrada significativas:

| Aspecto | WhatsApp Business API | Telegram Bot API |
|---|---|---|
| Cuenta de desarrollador | Meta Developer Account obligatoria | No se requiere |
| Verificación del negocio | Proceso de revisión por parte de Meta | No aplica |
| Número de teléfono | Número dedicado verificado por Meta | No aplica |
| Servidor propio | Webhook con HTTPS público obligatorio | Polling disponible sin infraestructura propia |
| Coste | De pago por conversación en producción | Gratuita |
| Tiempo de configuración | Días/semanas | Minutos |

Para un proyecto de aprendizaje personal con despliegue inmediato y sin costes, Telegram ofrece una API completa, gratuita y sin requisitos de verificación empresarial. La librería `python-telegram-bot` simplifica además la gestión del estado de conversación y los handlers asíncronos.

**La limitación real:** los usuarios deben tener instalada la aplicación de Telegram. Para uso personal o en entornos donde Telegram está disponible, esto no supone un problema. Si en el futuro se necesitase llegar a usuarios de WhatsApp, habría que migrar a la API oficial de Meta o a proveedores intermediarios como Twilio.

---

## Por qué se requiere verificación de usuario

El bot está desplegado públicamente: cualquier persona con el enlace podría usarlo. Dado que el bot envía audios a servicios externos de IA (Groq, con servidores en EEUU), se aplica verificación de usuario por dos razones:

### 1. Control de acceso personal

Este es un proyecto personal. Sin verificación, el bot quedaría expuesto a uso no autorizado por parte de terceros, lo que podría agotar los límites gratuitos de la API de Groq o generar un uso que el propietario no conoce ni ha autorizado.

### 2. Cumplimiento del RGPD (Reglamento General de Protección de Datos)

Cuando un usuario envía un audio, ese audio puede contener datos personales (voz, contenido de conversaciones). Antes de procesarlo y enviarlo a un servicio externo, el bot debe:

- **Informar al usuario** de que sus datos serán procesados por un tercero (Groq, EEUU) — esto se hace mediante el aviso de privacidad mostrado en `/start`.
- **Obtener el consentimiento activo** del usuario — el usuario proporciona su nombre y apellidos como acto explícito de consentimiento informado.
- **Controlar quién usa el servicio** — el administrador puede rechazar solicitudes de acceso, limitando el tratamiento de datos a personas conocidas y autorizadas.

El flujo de registro no recoge más datos de los estrictamente necesarios (principio de minimización de datos del RGPD): únicamente nombre, apellidos e ID de Telegram, que son suficientes para identificar al usuario y gestionar su acceso.

---

## Marco legal y avisos

### Aviso de privacidad

El bot informa a cada nuevo usuario, antes de recoger ningún dato, de lo siguiente:

- Los audios son procesados por **Groq** (empresa estadounidense), fuera del territorio de la UE.
- Al proporcionar su nombre y continuar, el usuario **acepta explícitamente** este tratamiento.
- La transferencia internacional de datos a EEUU se realiza bajo las garantías del **Marco de Privacidad UE-EEUU (Data Privacy Framework)**, al que Groq se acoge.

### Datos almacenados

| Dato | Dónde | Duración |
|---|---|---|
| Nombre y apellidos | Memoria del proceso (RAM) | Solo mientras el bot está en ejecución |
| Estado del usuario (aprobado/pendiente/rechazado) | Memoria del proceso (RAM) | Solo mientras el bot está en ejecución |
| Audios | Archivo temporal en disco | Se eliminan inmediatamente tras la transcripción |

**No se utiliza ninguna base de datos persistente.** Al reiniciar el bot, todos los usuarios pierden su estado y deben volver a registrarse. Esto es una limitación del MVP actual y podría resolverse con una base de datos en una versión futura.

### Responsabilidad sobre el contenido

El propietario del bot no es responsable del contenido de los audios transcritos. El servicio se ofrece tal cual, sin garantías de disponibilidad ni de precisión de las transcripciones. La calidad de la transcripción depende del modelo de Groq Whisper.

### Datos de terceros

- **Groq**: procesa los audios y los textos para traducción. Consulta su política de privacidad en [groq.com](https://groq.com).
- **Telegram**: gestiona el envío y recepción de mensajes. Consulta su política de privacidad en [telegram.org/privacy](https://telegram.org/privacy).

---

## Limitaciones conocidas del MVP

- El estado de usuarios se almacena en memoria: si el bot se reinicia (por ejemplo, por un redespliegue en Railway), los usuarios aprobados deberán volver a registrarse.
- No hay sistema de logs de auditoría persistente.
- Un único administrador puede aprobar o rechazar solicitudes.
- El límite de 20MB para archivos de audio es una restricción de la API de Telegram (los archivos enviados vía bot no pueden superar ese tamaño).
