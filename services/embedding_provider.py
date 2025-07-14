from config import Config
from langchain_huggingface import HuggingFaceEmbeddings

# Then update the instance:
class EmbeddingProvider:
    _instance = None

    @classmethod
    def get_embedder(cls):
        if cls._instance is None:
            cls._instance = HuggingFaceEmbeddings(
                model_name=Config.EMBEDDING_MODEL_PATH
            )
        return cls._instance