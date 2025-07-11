# services/vector_store_builder.py
import os
from langchain.vectorstores.chroma import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.embedding_provider import EmbeddingProvider

class VectorStoreBuilder:
    @staticmethod
    def build_vector_store(category_name: str, pdf_paths: list[str], persist_dir: str = "vectorstores"):
        all_docs = []
        for pdf in pdf_paths:
            loader = PyPDFLoader(pdf)
            docs = loader.load()
            all_docs.extend(docs)

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
        chunks = splitter.split_documents(all_docs)

        embedder = EmbeddingProvider.get_embedder()

        category_dir = os.path.join(persist_dir, category_name)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embedder,
            persist_directory=category_dir
        )
        vectorstore.persist()
        return vectorstore
