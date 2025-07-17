from services.rag_engine import RAGEngine
from typing import List
from handlers.base_handler import BaseHandler

class PlumbingHandler(BaseHandler):
    def __init__(self):
        super().__init__("plumbing")

    def _initialize_rag(self):
        self.rag_engine = RAGEngine("plumbing")

    @property
    def validation_prompt(self) -> str:
        return """
        You are an expert in plumbing systems. Analyze this image to verify it contains:
        - Water or drainage pipes
        - Plumbing fixtures (faucets, toilets, sinks)
        - Valves or connectors
        - Pumping or drainage systems
        If the image primarily contains these elements, it is suitable for the plumbing category.
        """

    @property
    def vision_analysis_prompt(self) -> str:
        return """
        You are a professional plumber. Describe in detail everything related to plumbing that appears in this image.
        """

    @property
    def compliance_analysis_prompt(self) -> str:
        return """
        You are an expert in the Saudi Plumbing Code:
        1. Identify the types of plumbing fixtures present.
        2. Assess their compliance with the Saudi code.
        3. Highlight any potential violations.
        4. Provide recommendations for improvement.
        Focus on:
        - Connection quality
        - Materials used
        - Slopes and gradients
        - Sanitary safety requirements
        """

    @property
    def validation_keywords(self) -> List[str]:
        return [
            "plumbing", "pipes", "water", "drainage", "faucets",
            "toilets", "valves", "pumps", "sanitary"
        ]
