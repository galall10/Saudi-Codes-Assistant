# services/rag_engine.py
import os
from langchain.vectorstores import Chroma
from services.embedding_provider import EmbeddingProvider

class RAGEngine:
    def __init__(self, category_name: str, persist_dir: str = "vectorstores"):
        embedder = EmbeddingProvider.get_embedder()
        self.vectorstore = Chroma(
            persist_directory=os.path.join(persist_dir, category_name),
            embedding_function=embedder
        )

    def query(self, text: str):
        results = self.vectorstore.similarity_search(text, k=5)
        return [
            {"source": r.metadata.get("source", ""), "text": r.page_content}
            for r in results
        ]
