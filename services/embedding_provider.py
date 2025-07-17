from config import Config
from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingProvider:
    _instance = None

    @classmethod
    def get_embedder(cls):
        if cls._instance is None:
            model_name = Config.EMBEDDING_MODEL_PATH

            # E5 models require a query instruction prompt
            if "e5" in model_name.lower() or "mlqa" in model_name.lower():
                cls._instance = HuggingFaceEmbeddings(
                    model_name=model_name,
                    encode_kwargs={"normalize_embeddings": True},
                    query_instruction="query: "
                )
            else:
                cls._instance = HuggingFaceEmbeddings(model_name=model_name)

        return cls._instance
