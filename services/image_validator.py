from vision.llm_vision_model import VisionModel

def validate_image(image_path: str, prompt: str, keywords: list) -> bool:
    description = VisionModel.describe(image_path, prompt)
    return any(keyword in description for keyword in keywords)

