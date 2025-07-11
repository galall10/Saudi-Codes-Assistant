# orchestrator.py
from services.handler_factory import HandlerFactory

class Orchestrator:
    @staticmethod
    def analyze_image(image_path: str, category: str) -> dict:
        try:
            handler = HandlerFactory.get_handler(category)
            result = handler.invoke(image_path)
            return result
        except Exception as e:
            return {"error": str(e), "category": category, "valid": False}
