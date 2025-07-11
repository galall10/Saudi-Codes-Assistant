import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Config:
    # API Settings
    OPENROUTER_API_KEYS: List[str] = os.getenv("OPENROUTER_API_KEYS", "").split(",")
    EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "models/all-MiniLM-L6-v2")

    # Directory settings
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CODES_DIR = os.path.join(BASE_DIR, "data", "saudi_codes")
    DB_DIR = os.path.join(BASE_DIR, "data", "db")
    UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")

    # Model preferences (loaded from .env and split by comma)
    VISION_MODELS: List[str] = os.getenv("VISION_MODELS", "").split(",")
    TEXT_MODELS: List[str] = os.getenv("TEXT_MODELS", "").split(",")
    THERMAL_VISION_MODELS: List[str] = os.getenv("THERMAL_VISION_MODELS", "").split(",")

    # Processing settings
    #MAX_IMAGES_PER_REQUEST = 10
    #EMBEDDING_BATCH_SIZE = 32
    MAX_TOKENS_VISION = 3000
    MAX_TOKENS_TEXT = 4000

    # Supported image formats
    #SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']

    # Supported categories
    CATEGORIES = ["electricity", "plumbing"]

    @classmethod
    def create_dirs(cls):
        """Create necessary directories"""
        for path in [cls.CODES_DIR, cls.DB_DIR, cls.UPLOADS_DIR]:
            os.makedirs(path, exist_ok=True)
