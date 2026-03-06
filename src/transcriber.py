import logging
import os
from groq import AsyncGroq

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


async def transcribe_audio(file_path: str) -> str:
    client = _get_client()
    with open(file_path, "rb") as f:
        transcription = await client.audio.transcriptions.create(
            file=(os.path.basename(file_path), f.read()),
            model="whisper-large-v3-turbo",
        )
    return transcription.text.strip()
