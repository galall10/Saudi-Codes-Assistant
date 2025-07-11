# scripts/download_model.py
from sentence_transformers import SentenceTransformer
import os

def ensure_model_downloaded():
    target_dir = os.path.join("models", "all-MiniLM-L6-v2")
    if not os.path.exists(target_dir):
        print("📦 Downloading and saving model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        model.save(target_dir)
        print(f"✅ Model saved to {target_dir}")
    else:
        print("✅ Model already exists.")
