import asyncio
import logging
import whisper

logger = logging.getLogger(__name__)

_model = None


def _get_model():
    global _model
    if _model is None:
        logger.info("Cargando modelo Whisper (primera vez, puede tardar unos segundos)...")
        _model = whisper.load_model("base")
    return _model


def _transcribe_sync(file_path: str) -> str:
    model = _get_model()
    result = model.transcribe(file_path)
    return result["text"].strip()


async def transcribe_audio(file_path: str) -> str:
    return await asyncio.to_thread(_transcribe_sync, file_path)
