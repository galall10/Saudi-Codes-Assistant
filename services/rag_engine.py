# services/rag_engine.py
import os
from langchain_chroma import Chroma
from services.embedding_provider import EmbeddingProvider

class RAGEngine:
    def __init__(self, category_name: str, persist_dir: str = "vectorstores"):
        embedder = EmbeddingProvider.get_embedder()
        self.vectorstore = Chroma(
            persist_directory=os.path.join(persist_dir, category_name),
            embedding_function=embedder
        )

    def query(self, text: str, k: int = 5):
        results = self.vectorstore.similarity_search(text, k=k)
        return [
            {"source": r.metadata.get("source", ""), "text": r.page_content}
            for r in results
        ]

    def mmr_query(self, text: str, k: int = 5, fetch_k: int = 20, lambda_mult: float = 0.5):
        results = self.vectorstore.max_marginal_relevance_search(
            query=text,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult
        )
        return [
            {"source": r.metadata.get("source", ""), "text": r.page_content}
            for r in results
        ]
