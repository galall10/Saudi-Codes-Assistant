# handlers/base_handler.py
from abc import ABC, abstractmethod
from typing import Dict, List

from llm.llm_text_model import LLMTextModel
from services.image_analyzer import ImageAnalyzer
from services.image_validator import validate_image

class BaseHandler(ABC):
    """Base class for all category handlers"""

    def __init__(self, category_name: str):
        self.category_name = category_name
        self.rag_engine = None
        self._initialize_rag()

    @abstractmethod
    def _initialize_rag(self):
        """Initialize RAG engine for this category"""
        pass

    @property
    @abstractmethod
    def validation_prompt(self) -> str:
        """Prompt for image validation"""
        pass

    @property
    @abstractmethod
    def vision_analysis_prompt(self) -> str:
        """Prompt for image analysis"""
        pass

    @property
    @abstractmethod
    def compliance_analysis_prompt(self) -> str:
        """Prompt for compliance analysis"""
        pass

    @property
    @abstractmethod
    def validation_keywords(self) -> List[str]:
        """Keywords for validation"""
        pass

    def validate_image(self, image_path: str) -> Dict:
        """Validate if image is appropriate for this category"""
        try:
            is_valid = validate_image(
                image_path,
                self.validation_prompt,
                self.validation_keywords
            )
            return {
                "is_valid": is_valid,
                "reason": "" if is_valid else f"الصورة غير مناسبة لفئة {self.category_name}"
            }
        except Exception as e:
            return {
                "is_valid": False,
                "reason": f"خطأ في التحقق من الصورة: {str(e)}"
            }

    def analyze_image(self, image_path: str) -> Dict:
        """Analyze image and provide description"""
        try:
            description = ImageAnalyzer.describe(image_path, self.vision_analysis_prompt)
            return {
                "description": description
            }
        except Exception as e:
            return {
                "description": "",
                "error": str(e)
            }

    def get_compliance_analysis(self, description: str) -> Dict:
        try:
            matches = self.rag_engine.query(description)
            return {
                "description": description,
                "code_matches": matches,
                "compliance_prompt_used": self.compliance_analysis_prompt,
                "compliance_analysis": LLMTextModel.analyze(description, self.compliance_analysis_prompt)
            }
        except Exception as e:
            return {
                "description": description,
                "code_matches": [],
                "compliance_prompt_used": self.compliance_analysis_prompt,
                "error": str(e)
            }
