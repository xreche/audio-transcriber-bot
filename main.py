import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)
logger.info(f"TELEGRAM_TOKEN present: {bool(os.getenv('TELEGRAM_TOKEN'))}")
logger.info(f"GROQ_API_KEY present: {bool(os.getenv('GROQ_API_KEY'))}")

from src.bot import run_bot

if __name__ == "__main__":
    run_bot()
