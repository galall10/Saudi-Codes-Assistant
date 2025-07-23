import os
from dotenv import load_dotenv
from typing import List

load_dotenv()


class Config:
    # API Keys
    OPENROUTER_API_KEYS: List[str] = os.getenv("OPENROUTER_API_KEYS", "").split(",")

    # Embedding Model
    EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "sentence-transformers/all-MiniLM-L6-v2")

    # Vision/Text Model Preferences
    VISION_MODELS: List[str] = os.getenv("VISION_MODELS", "").split(",")
    TEXT_MODELS: List[str] = os.getenv("TEXT_MODELS", "").split(",")
    THERMAL_VISION_MODELS: List[str] = os.getenv("THERMAL_VISION_MODELS", "").split(",")

    # Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CODES_DIR = os.path.join(BASE_DIR, "data", "saudi_codes")
    DB_DIR = os.path.join(BASE_DIR, "data", "db")
    UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")

    # Categories Supported
    CATEGORIES = ["electricity", "plumbing"]

    # Token limits
    MAX_TOKENS_VISION = 3000
    MAX_TOKENS_TEXT = 10000

    @classmethod
    def create_dirs(cls):
        """Ensure required directories exist."""
        for path in [cls.CODES_DIR, cls.DB_DIR, cls.UPLOADS_DIR]:
            os.makedirs(path, exist_ok=True)
