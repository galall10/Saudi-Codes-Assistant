# test_RAG.py
import os
import sys
import logging
from services.rag_engine import RAGEngine
from services.vector_store_builder import VectorStoreBuilder
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_rag_comprehensive(category: str, query_text: str):
    """Comprehensive RAG testing with diagnostics"""

    print(f"🔍 Testing RAG for category '{category}'")
    print(f"📝 Query: {query_text}")
    print("=" * 60)

    try:
        # Initialize RAG engine
        rag = RAGEngine(category_name=category)

        # Test connection
        print("🧪 Testing vector store connection...")
        connection_test = rag.test_connection()
        print(f"Status: {connection_test['status']}")
        print(f"Message: {connection_test['message']}")

        if connection_test['status'] == 'error':
            print("❌ RAG connection failed!")
            return False

        # Get collection info
        collection_info = rag.get_collection_info()
        print(f"📊 Collection info: {collection_info}")

        # Perform similarity search
        print("\n🔍 Performing similarity search...")
        similarity_results = rag.query(query_text, k=5)

        if not similarity_results:
            print("❌ No similarity search results found.")
        else:
            print(f"✅ Found {len(similarity_results)} similarity matches:")
            for i, result in enumerate(similarity_results, 1):
                print(f"\n--- Match #{i} ---")
                print(f"Source: {result['source']}")
                print(f"Text: {result['text'][:200]}...")
                if result.get('score'):
                    print(f"Score: {result['score']}")

        # Perform MMR search
        print(f"\n🎯 Performing MMR search...")
        mmr_results = rag.mmr_query(query_text, k=5)

        if not mmr_results:
            print("❌ No MMR search results found.")
        else:
            print(f"✅ Found {len(mmr_results)} MMR matches:")
            for i, result in enumerate(mmr_results, 1):
                print(f"\n--- MMR Match #{i} ---")
                print(f"Source: {result['source']}")
                print(f"Text: {result['text'][:200]}...")
                if result.get('score'):
                    print(f"Score: {result['score']}")

        # Combine results
        all_results = similarity_results + mmr_results
        print(f"\n📈 Total combined results: {len(all_results)}")

        return True

    except FileNotFoundError as e:
        print(f"❌ Vector store not found: {str(e)}")
        print("💡 Try running build_all_vector_stores() first")
        return False

    except Exception as e:
        print(f"❌ Error during RAG testing: {str(e)}")
        logger.error(f"RAG test error: {str(e)}", exc_info=True)
        return False


def rebuild_and_test(category: str, query_text: str):
    """Rebuild vector store and test RAG"""

    print(f"🔄 Rebuilding vector store for category '{category}'...")

    try:
        # Get PDF paths
        category_pdf_dir = os.path.join(Config.CODES_DIR, category)

        if not os.path.exists(category_pdf_dir):
            print(f"❌ Category directory not found: {category_pdf_dir}")
            return False

        pdf_paths = [
            os.path.join(category_pdf_dir, f)
            for f in os.listdir(category_pdf_dir)
            if f.endswith(".pdf")
        ]

        if not pdf_paths:
            print(f"❌ No PDFs found in {category_pdf_dir}")
            return False

        print(f"📁 Found {len(pdf_paths)} PDFs:")
        for pdf in pdf_paths:
            print(f"  - {os.path.basename(pdf)}")

        # Build vector store
        VectorStoreBuilder.build_vector_store(
            category_name=category,
            pdf_paths=pdf_paths,
            persist_dir=Config.DB_DIR
        )

        print(f"✅ Vector store rebuilt successfully for '{category}'")

        # Test RAG
        print(f"\n🧪 Testing RAG after rebuild...")
        return test_rag_comprehensive(category, query_text)

    except Exception as e:
        print(f"❌ Error during rebuild: {str(e)}")
        logger.error(f"Rebuild error: {str(e)}", exc_info=True)
        return False


def diagnose_rag_issues():
    """Diagnose common RAG issues"""

    print("🔧 Diagnosing RAG setup...")
    print("=" * 50)

    # Check directories
    print("📁 Checking directories...")
    Config.create_dirs()

    dirs_to_check = [
        ("Codes Directory", Config.CODES_DIR),
        ("Database Directory", Config.DB_DIR),
        ("Uploads Directory", Config.UPLOADS_DIR)
    ]

    for name, path in dirs_to_check:
        exists = os.path.exists(path)
        print(f"  {name}: {'✅' if exists else '❌'} {path}")

        if exists and os.path.isdir(path):
            contents = os.listdir(path)
            print(f"    Contents: {contents}")

    # Check categories
    print(f"\n🏷️  Checking categories...")
    for category in Config.CATEGORIES:
        category_path = os.path.join(Config.CODES_DIR, category)
        category_db_path = os.path.join(Config.DB_DIR, category)

        print(f"  Category: {category}")
        print(f"    PDF Directory: {'✅' if os.path.exists(category_path) else '❌'} {category_path}")
        print(f"    Vector Store: {'✅' if os.path.exists(category_db_path) else '❌'} {category_db_path}")

        if os.path.exists(category_path):
            pdfs = [f for f in os.listdir(category_path) if f.endswith('.pdf')]
            print(f"    PDFs found: {len(pdfs)}")

        if os.path.exists(category_db_path):
            db_files = os.listdir(category_db_path)
            print(f"    DB files: {len(db_files)}")

    # Check embedding model
    print(f"\n🤖 Checking embedding model...")
    try:
        from services.embedding_provider import EmbeddingProvider
        embedder = EmbeddingProvider.get_embedder()
        print(f"  Embedding model: ✅ {Config.EMBEDDING_MODEL_PATH}")

        # Test embedding
        test_text = "This is a test sentence for embedding"
        embedding = embedder.embed_query(test_text)
        print(f"  Test embedding: ✅ Generated {len(embedding)} dimensions")

    except Exception as e:
        print(f"  Embedding model: ❌ {str(e)}")


if __name__ == "__main__":
    # Configuration
    test_category = "electricity"
    test_query = "electrical installation safety requirements"

    print("🚀 RAG System Diagnostic and Test")
    print("=" * 60)

    # Run diagnostics
    diagnose_rag_issues()

    print(f"\n{'=' * 60}")

    # Test RAG
    success = test_rag_comprehensive(test_category, test_query)

    if not success:
        print(f"\n🔄 RAG test failed. Attempting rebuild...")
        success = rebuild_and_test(test_category, test_query)

    if success:
        print(f"\n🎉 RAG system is working correctly!")
    else:
        print(f"\n❌ RAG system has issues that need to be resolved.")

        # Provide troubleshooting tips
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure PDF files are in the correct directory structure")
        print("2. Check that vector stores are built properly")
        print("3. Verify embedding model is accessible")
        print("4. Review logs for detailed error messages")
        print("5. Try running VectorStoreBuilder.rebuild_all_vector_stores()")