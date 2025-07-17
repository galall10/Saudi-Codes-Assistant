# services/vector_store_builder.py
import os
import shutil
import logging
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.embedding_provider import EmbeddingProvider


class VectorStoreBuilder:
    @staticmethod
    def build_vector_store(category_name: str, pdf_paths: list[str], persist_dir: str = "vectorstores"):
        logger = logging.getLogger(__name__)

        if not pdf_paths:
            logger.error(f"No PDF paths provided for category '{category_name}'")
            raise ValueError(f"No PDF paths provided for category '{category_name}'")

        all_docs = []
        failed_pdfs = []

        # Load all PDFs into documents
        for pdf in pdf_paths:
            if not os.path.exists(pdf):
                logger.warning(f"PDF file not found: {pdf}")
                failed_pdfs.append(pdf)
                continue

            try:
                logger.info(f"Loading PDF: {pdf}")
                loader = PyPDFLoader(pdf)
                docs = loader.load()

                if not docs:
                    logger.warning(f"No documents loaded from PDF: {pdf}")
                    failed_pdfs.append(pdf)
                    continue

                # Add source metadata
                for doc in docs:
                    doc.metadata["source"] = os.path.basename(pdf)
                    doc.metadata["category"] = category_name

                all_docs.extend(docs)
                logger.info(f"Successfully loaded {len(docs)} pages from {pdf}")

            except Exception as e:
                logger.error(f"Error loading PDF {pdf}: {str(e)}")
                failed_pdfs.append(pdf)
                continue

        if not all_docs:
            logger.error(f"No documents were successfully loaded for category '{category_name}'")
            raise ValueError(f"No documents were successfully loaded for category '{category_name}'")

        if failed_pdfs:
            logger.warning(f"Failed to load {len(failed_pdfs)} PDFs: {failed_pdfs}")

        logger.info(f"Total documents loaded: {len(all_docs)}")

        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

        try:
            chunks = splitter.split_documents(all_docs)
            logger.info(f"Created {len(chunks)} chunks from {len(all_docs)} documents")
        except Exception as e:
            logger.error(f"Error splitting documents: {str(e)}")
            raise

        if not chunks:
            logger.error("No chunks were created from the documents")
            raise ValueError("No chunks were created from the documents")

        # Print sample chunks for debugging
        logger.info(f"Sample chunks for '{category_name}':")
        for i, chunk in enumerate(chunks[:3]):
            logger.info(f"Chunk #{i + 1} (length: {len(chunk.page_content)}):")
            logger.info(f"Content: {chunk.page_content[:200]}...")
            logger.info(f"Metadata: {chunk.metadata}")
            logger.info("-" * 50)

        # Initialize embedding model
        try:
            embedder = EmbeddingProvider.get_embedder()
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {str(e)}")
            raise

        # Build and persist vector store
        category_dir = os.path.join(persist_dir, category_name)

        if os.path.exists(category_dir):
            logger.info(f"Removing existing vector store: {category_dir}")
            shutil.rmtree(category_dir)

        os.makedirs(category_dir, exist_ok=True)

        try:
            logger.info(f"Building vector store for '{category_name}' with {len(chunks)} chunks...")
            vectorstore = FAISS.from_documents(documents=chunks, embedding=embedder)

            # Save the vector store
            vectorstore.save_local(folder_path=category_dir)

            # Fix: Check document count properly for FAISS
            doc_count = vectorstore.index.ntotal if hasattr(vectorstore, 'index') else len(chunks)

            if doc_count == 0:
                logger.error("Vector store was created but contains no documents")
                raise ValueError("Vector store was created but contains no documents")

            logger.info(f"Vector store created successfully with {doc_count} documents")

            # Optional test query
            try:
                test_results = vectorstore.similarity_search("test", k=1)
                logger.info(f"Vector store test successful. Found {len(test_results)} test results")
            except Exception as e:
                logger.warning(f"Vector store test failed: {str(e)}")

            return vectorstore

        except Exception as e:
            logger.error(f"Error building vector store: {str(e)}")
            if os.path.exists(category_dir):
                shutil.rmtree(category_dir)
            raise

    @staticmethod
    def rebuild_all_vector_stores():
        """Rebuild all vector stores from scratch"""
        from config import Config

        logger = logging.getLogger(__name__)
        base_pdf_dir = Config.CODES_DIR
        persist_dir = Config.DB_DIR
        categories = Config.CATEGORIES

        logger.info("Starting complete vector store rebuild...")

        for category in categories:
            category_pdf_dir = os.path.join(base_pdf_dir, category)
            if not os.path.isdir(category_pdf_dir):
                logger.warning(f"Skipping '{category}' (no folder found at {category_pdf_dir})")
                continue

            pdf_paths = [
                os.path.join(category_pdf_dir, f)
                for f in os.listdir(category_pdf_dir)
                if f.endswith(".pdf")
            ]

            if not pdf_paths:
                logger.warning(f"No PDFs found for '{category}' in {category_pdf_dir}")
                continue

            try:
                logger.info(f"Rebuilding vector store for '{category}' with {len(pdf_paths)} PDFs...")
                VectorStoreBuilder.build_vector_store(
                    category_name=category,
                    pdf_paths=pdf_paths,
                    persist_dir=persist_dir
                )
                logger.info(f"Successfully rebuilt vector store for '{category}'")
            except Exception as e:
                logger.error(f"Failed to rebuild vector store for '{category}': {str(e)}")
                continue

        logger.info("Vector store rebuild complete!")