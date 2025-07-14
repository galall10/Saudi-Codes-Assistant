# image_analyzer.py
from llm.llm_vision_model import VisionModel

class ImageAnalyzer:
    @staticmethod
    def describe(image_path: str, prompt: str) -> str:
        return VisionModel.describe(image_path, prompt)
