
from pathlib import Path

# Create logs directory if it doesn't exist 
LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"
import logging

logging.basicConfig(
    level=logging.ERROR,  # Only log ERROR and CRITICAL
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()  #  Print to console
    ]
)

logger = logging.getLogger("ai-code-assessment")
