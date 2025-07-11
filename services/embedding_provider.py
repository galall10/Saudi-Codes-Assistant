# services/embedding_provider.py
from langchain.embeddings import SentenceTransformerEmbeddings
from config import Config

class EmbeddingProvider:
    _instance = None

    @classmethod
    def get_embedder(cls):
        if cls._instance is None:
            cls._instance = SentenceTransformerEmbeddings(
                model_name=Config.EMBEDDING_MODEL_PATH
            )
        return cls._instance
