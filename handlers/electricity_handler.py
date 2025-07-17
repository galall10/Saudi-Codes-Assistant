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
        You are an expert in the Saudi Electrical Code:
        1. Identify the types of electrical installations present.
        2. Assess their compliance with the Saudi code.
        3. Highlight any potential violations.
        4. Provide recommendations for improvement.
        Focus on:
        - Connection safety
        - Safe distances
        - Installation quality
        - Safety requirements
        """

    @property
    def validation_keywords(self) -> List[str]:
        return ["wires", "switches", "breakers", "cables", "equipment"]
