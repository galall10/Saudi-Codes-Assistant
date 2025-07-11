# utils/llm_utils.py
import base64
import requests
from config import Config

def call_vision_model(image_path: str, prompt: str) -> str:
    key = Config.OPENROUTER_API_KEYS[0]  # Just use the first key for now
    with open(image_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode()

    payload = {
        "model": Config.VISION_MODELS[0],
        "prompt": prompt,
        "image": b64_img,
        "max_tokens": Config.MAX_TOKENS_VISION
    }

    # Simulated endpoint for example purposes:
    response = requests.post("https://api.openrouter.ai/v1/vision", headers={"Authorization": f"Bearer {key}"}, json=payload)
    return response.json().get("result", "No response")
