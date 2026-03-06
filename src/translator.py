import os
import logging
from groq import AsyncGroq

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    return _client


async def translate_text(text: str, target_language: str) -> str:
    client = _get_client()
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    f"Eres un traductor profesional. Traduce el siguiente texto al {target_language}. "
                    "Devuelve SOLO la traducción, sin explicaciones ni comentarios adicionales."
                ),
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content.strip()
