from abc import ABC, abstractmethod

class BaseHandler(ABC):
    @abstractmethod
    def validate_image(self, image_path: str) -> dict:
        pass

    @abstractmethod
    def analyze_image(self, image_path: str) -> dict:
        pass

    @abstractmethod
    def get_compliance_analysis(self, description: str) -> dict:
        pass
