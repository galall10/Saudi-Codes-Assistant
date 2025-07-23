from typing import List
from services.rag_engine import RAGEngine
from handlers.base_handler import BaseHandler


class ElectricityHandler(BaseHandler):
    def __init__(self):
        super().__init__("electricity")

    def _initialize_rag(self):
        self.rag_engine = RAGEngine("electricity")

    @property
    def validation_prompt(self) -> str:
        return """
        You are an expert in electrical installations. Analyze this image to verify it contains:
        - Electrical components (wires, switches, sockets)
        - Electrical panels or circuit breakers
        - Cables or electrical conduits
        - Other electrical equipment
        """

    @property
    def vision_analysis_prompt(self) -> str:
        return """ 
        You are a professional electrician. Describe in detail everything related to electricity that appears in this image.
        """

    @property
    def compliance_analysis_prompt(self) -> str:
        return """
        You are an expert in the Saudi Electrical Code. Analyze this electrical installation:
        1. Identify the types of electrical installations present.
        2. Assess their compliance with the Saudi code.
        3. Highlight any potential violations.
        4. Provide recommendations for improvement.

        Focus on:
        - Connection safety
        - Safe distances
        - Installation quality
        - Safety requirements

        Provide detailed analysis including compliance percentage and specific issues found.
        """

    @property
    def table_generation_prompt(self) -> str:
        return """
        You are an expert in Saudi Electrical Code compliance. Based on the following compliance analyses from multiple images in the {category_name} category, generate a comprehensive compliance table.

        Category Items to Check: {category_items}

        Compliance Analyses:
        {analyses_text}

        Generate a JSON response with the following exact structure:
        {{
            "category": "{category_name}",
            "items": [
                {{
                    "item": "Item name (e.g., Electrical outlets)",
                    "aspect": "Specific aspect being checked (e.g., Type/Load capacity/Wiring installation)",
                    "condition": "Pass/Partially Pass/Fail",
                    "compliance_percentage": 85,
                    "remarks": "Detailed remarks about the condition",
                    "site_notes": "Specific site observations"
                }}
            ],
            "overall_compliance_percentage": 78,
            "category_advantages": [
                "List of positive aspects found in this category",
                "What is working well according to Saudi code"
            ],
            "category_summary": "Overall summary of the category compliance"
        }}

        Important:
        - Each item should represent a specific checkpoint from the Saudi Electrical Code
        - Compliance percentage should be realistic based on findings
        - Use "Pass", "Partially Pass", or "Fail" for condition
        - Provide specific, actionable remarks
        - Include advantages/positive findings where applicable
        - Ensure valid JSON format
        """

    @property
    def validation_keywords(self) -> List[str]:
        return ["wires", "switches", "breakers", "cables", "equipment", "electrical", "panel", "outlet"]

    @property
    def category_items(self) -> List[str]:
        return [
            "Electrical outlets - Type and Quality",
            "Electrical outlets - Load capacity",
            "Electrical outlets - Wiring installation",
            "External electrical outlets - Coverage",
            "Around electrical finishing - Quality",
            "Electrical outlets - Alignment",
            "Kitchen oven electrical cable - Extension",
            "Oven outlet - Extension",
            "General electrical wiring - Extension",
            "Lighting units - Type and quality",
            "Lighting distribution",
            "Suitability of electrical switches and connections",
            "Lighting units operation",
            "Electrical panel - Type and quality",
            "Panel board distribution labeling",
            "Panel installation",
            "Panel breakers load capacity",
            "Panel load distribution",
            "Additional breakers presence",
            "Panel earthing connections",
            "Panel neutral connections"
        ]
