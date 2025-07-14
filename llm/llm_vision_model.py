from utils.llm_models_utils import call_vision_model

class VisionModel:
    @staticmethod
    def describe(image_path: str, prompt: str) -> str:
        return call_vision_model(image_path, prompt)