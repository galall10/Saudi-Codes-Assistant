# services/rag_engine.py
import os
from langchain_community.vectorstores import FAISS
from services.embedding_provider import EmbeddingProvider
from config import Config
import logging


class RAGEngine:
    def __init__(self, category_name: str, persist_dir: str = None):
        self.category_name = category_name
        self.logger = logging.getLogger(__name__)

        # Use Config.DB_DIR if persist_dir is not provided
        if persist_dir is None:
            persist_dir = Config.DB_DIR

        self.persist_dir = os.path.join(persist_dir, category_name)

        # Check if vector store exists
        if not os.path.exists(self.persist_dir):
            self.logger.error(f"Vector store directory not found: {self.persist_dir}")
            raise FileNotFoundError(
                f"Vector store for category '{category_name}' not found. Please build vector stores first.")

        # Check if vector store has data
        if not os.listdir(self.persist_dir):
            self.logger.error(f"Vector store directory is empty: {self.persist_dir}")
            raise ValueError(f"Vector store for category '{category_name}' is empty. Please rebuild vector stores.")

        try:
            embedder = EmbeddingProvider.get_embedder()
            self.vectorstore = FAISS.load_local(
                folder_path=self.persist_dir,
                embeddings=embedder,
                allow_dangerous_deserialization=True  # Fix: Add this parameter
            )

        except Exception as e:
            self.logger.error(f"Failed to initialize vector store for '{category_name}': {str(e)}")
            raise

    def query(self, text: str, k: int = 5):
        """Perform similarity search with error handling"""
        try:
            if not text or not text.strip():
                self.logger.warning("Empty query text provided")
                return []

            results = self.vectorstore.similarity_search(text, k=k)

            if not results:
                self.logger.info(f"No similarity search results found for: '{text[:50]}...'")
                return []

            formatted_results = []
            for r in results:
                formatted_results.append({
                    "source": r.metadata.get("source", "Unknown"),
                    "text": r.page_content,
                    "score": getattr(r, 'score', None)  # Some vector stores provide similarity scores
                })

            self.logger.info(f"Found {len(formatted_results)} similarity matches for category '{self.category_name}'")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Error during similarity search: {str(e)}")
            return []

    def mmr_query(self, text: str, k: int = 5, fetch_k: int = 20, lambda_mult: float = 0.5):
        """Perform MMR (Maximal Marginal Relevance) search with error handling"""
        try:
            if not text or not text.strip():
                self.logger.warning("Empty query text provided for MMR search")
                return []

            results = self.vectorstore.max_marginal_relevance_search(
                query=text,
                k=k,
                fetch_k=fetch_k,
                lambda_mult=lambda_mult
            )

            if not results:
                self.logger.info(f"No MMR search results found for: '{text[:50]}...'")
                return []

            formatted_results = []
            for r in results:
                formatted_results.append({
                    "source": r.metadata.get("source", "Unknown"),
                    "text": r.page_content,
                    "score": getattr(r, 'score', None)
                })

            self.logger.info(f"Found {len(formatted_results)} MMR matches for category '{self.category_name}'")
            return formatted_results

        except Exception as e:
            self.logger.error(f"Error during MMR search: {str(e)}")
            return []

    def get_collection_info(self):
        """Get information about the vector store collection"""
        try:
            # Fix: FAISS doesn't have _collection attribute, use index instead
            if hasattr(self.vectorstore, 'index'):
                ntotal = self.vectorstore.index.ntotal
                return {
                    "count": ntotal,
                    "name": self.category_name,
                    "metadata": None
                }
            else:
                return {
                    "count": 0,
                    "name": self.category_name,
                    "metadata": None
                }
        except Exception as e:
            self.logger.error(f"Error getting collection info: {str(e)}")
            return {"error": str(e)}

    def test_connection(self):
        """Test if the vector store is working properly"""
        try:
            # Test with a simple query
            test_results = self.vectorstore.similarity_search("test", k=1)
            return {
                "status": "success",
                "message": f"Vector store working properly. Found {len(test_results)} documents.",
                "collection_info": self.get_collection_info()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Vector store test failed: {str(e)}"
            }
