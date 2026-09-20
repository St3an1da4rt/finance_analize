import os
from pathlib import Path

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance.db")
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))

MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", 10 * 1024 * 1024))
MAX_AUDIO_SIZE = int(os.getenv("MAX_AUDIO_SIZE", 25 * 1024 * 1024))

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}
ALLOWED_AUDIO_TYPES = {
    "audio/ogg": ".ogg",
    "audio/mpeg": ".mp3",
    "audio/mp4": ".m4a",
    "audio/wav": ".wav",
}
