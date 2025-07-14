# utils/llm_models_utils.py
import base64
import requests
from config import Config

def call_vision_model(image_path: str, prompt: str) -> str:
    key = Config.OPENROUTER_API_KEYS[0]
    model = Config.VISION_MODELS[0]

    # تحويل الصورة إلى base64
    with open(image_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")

    # إعداد الطلب
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_img}"
                        }
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    # إرسال الطلب إلى OpenRouter
    response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)

    if not response.ok:
        raise Exception(f"Failed to call vision model: {response.status_code} {response.text}")

    return response.json()["choices"][0]["message"]["content"]


def call_text_model(description: str, prompt: str) -> str:
    key = Config.OPENROUTER_API_KEYS[0]
    payload = {
        "model": Config.TEXT_MODELS[0],
        "messages": [
            {"role": "user", "content": f"{prompt}\n\nالوصف:\n{description}"}
        ],
        "max_tokens": Config.MAX_TOKENS_TEXT
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                             headers={"Authorization": f"Bearer {key}"},
                             json=payload)
    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
