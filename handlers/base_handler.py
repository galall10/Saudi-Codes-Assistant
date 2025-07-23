from abc import ABC, abstractmethod
from typing import Dict, List, Any
import json
from llm.llm_text_model import LLMTextModel
from services.image_analyzer import ImageAnalyzer
from services.image_validator import validate_image


class BaseHandler(ABC):
    """Base class for all category handlers with table generation capability"""

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
    def table_generation_prompt(self) -> str:
        """Prompt for generating compliance table"""
        pass

    @property
    @abstractmethod
    def validation_keywords(self) -> List[str]:
        """Keywords for validation"""
        pass

    @property
    @abstractmethod
    def category_items(self) -> List[str]:
        """List of items/checkpoints for this category"""
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
                "reason": "" if is_valid else f"The image is not suitable for the '{self.category_name}' category."
            }
        except Exception as e:
            return {
                "is_valid": False,
                "reason": f"Image validation error: {str(e)}"
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
        """Get compliance analysis for a single image"""
        try:
            matches = self.rag_engine.query(description)
            compliance_analysis = LLMTextModel.analyze(description, self.compliance_analysis_prompt)

            return {
                "description": description,
                "code_matches": matches,
                "compliance_analysis": compliance_analysis
            }
        except Exception as e:
            return {
                "description": description,
                "code_matches": [],
                "error": str(e)
            }

    def generate_compliance_table(self, all_compliance_analyses: List[Dict]) -> Dict[str, Any]:
        """
        Generate a compliance table JSON for the entire category

        Args:
            all_compliance_analyses: List of compliance analysis results from all images in this category

        Returns:
            JSON structure that frontend can use to generate the table
        """
        try:
            # Combine all compliance analyses
            combined_analyses = []
            for analysis in all_compliance_analyses:
                if not analysis.get("skipped", False) and "compliance_analysis" in analysis:
                    combined_analyses.append({
                        "description": analysis["description"],
                        "compliance_analysis": analysis["compliance_analysis"],
                        "code_matches": analysis.get("code_matches", [])
                    })

            if not combined_analyses:
                return {
                    "error": "No valid compliance analyses available for table generation",
                    "category": self.category_name
                }

            # Create the prompt with all analyses
            analyses_text = "\n\n---\n\n".join([
                f"Image Analysis {i + 1}:\nDescription: {analysis['description']}\nCompliance Analysis: {analysis['compliance_analysis']}"
                for i, analysis in enumerate(combined_analyses)
            ])

            full_prompt = self.table_generation_prompt.format(
                category_name=self.category_name,
                category_items=", ".join(self.category_items),
                analyses_text=analyses_text
            )

            # Get JSON response from LLM
            json_response = LLMTextModel.analyze(analyses_text, full_prompt)

            # Try to parse as JSON, fallback if needed
            try:
                table_data = json.loads(json_response)
            except json.JSONDecodeError:
                # If LLM didn't return valid JSON, create a fallback structure
                table_data = {
                    "category": self.category_name,
                    "items": [],
                    "overall_compliance_percentage": 0,
                    "category_advantages": [],
                    "raw_response": json_response,
                    "error": "Failed to parse LLM response as JSON"
                }

            return table_data

        except Exception as e:
            return {
                "error": f"Table generation error: {str(e)}",
                "category": self.category_name
            }

