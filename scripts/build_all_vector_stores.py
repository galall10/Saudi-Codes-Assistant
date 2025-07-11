# scripts/build_all_vector_stores.py
import os
from config import Config
from services.vector_store_builder import VectorStoreBuilder

def build_all_vector_stores():
    base_pdf_dir = Config.CODES_DIR
    persist_dir = Config.DB_DIR
    categories = Config.CATEGORIES

    print("🔍 Starting vector DB generation...\n")

    for category in categories:
        category_pdf_dir = os.path.join(base_pdf_dir, category)
        if not os.path.isdir(category_pdf_dir):
            print(f"⚠️  Skipping '{category}' (no folder found at {category_pdf_dir})")
            continue

        pdf_paths = [
            os.path.join(category_pdf_dir, f)
            for f in os.listdir(category_pdf_dir)
            if f.endswith(".pdf")
        ]

        if not pdf_paths:
            print(f"⚠️  No PDFs found for '{category}' in {category_pdf_dir}")
            continue

        print(f"📚 Processing '{category}' with {len(pdf_paths)} PDFs...")
        VectorStoreBuilder.build_vector_store(
            category_name=category,
            pdf_paths=pdf_paths,
            persist_dir=persist_dir
        )
        print(f"✅ Done: Vector store created for '{category}' in {os.path.join(persist_dir, category)}\n")

    print("🎉 All vector databases are ready!")
