# image_analyzer.py
from vision.llm_vision import VisionModel

class ImageAnalyzer:
    @staticmethod
    def describe(image_path: str, prompt: str) -> str:
        return VisionModel.describe(image_path, prompt)
