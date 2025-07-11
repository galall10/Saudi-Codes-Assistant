from typing import Dict, List
from langchain_core.runnables import RunnableParallel, RunnableSequence, RunnableLambda
from services.handler_factory import HandlerFactory

class ComplianceOrchestrator:
    def __init__(self, category_map: Dict[str, List[str]]):
        """
        category_map: { "electricity": ["image1.jpg", "image2.jpg"], ... }
        """
        self.category_map = category_map

    def build_image_chain(self, handler, image_path: str) -> RunnableSequence:
        return RunnableSequence([
            RunnableLambda(lambda _: handler.validate_image(image_path)),
            RunnableLambda(lambda result: (
                handler.analyze_image(image_path)
                if result.get("is_valid", False)
                else {"skipped": True, "reason": result.get("reason", "لم يتم التحقق")}
            )),
            RunnableLambda(lambda analysis: (
                handler.get_compliance_analysis(analysis["description"])
                if "description" in analysis and not analysis.get("skipped", False)
                else analysis
            ))
        ])

    def build_category_chain(self, category: str, image_paths: List[str]) -> RunnableParallel:
        handler = HandlerFactory.get_handler(category)
        return RunnableParallel({
            image_path: self.build_image_chain(handler, image_path)
            for image_path in image_paths
        })

    def run(self) -> dict:
        category_chains = {
            category: self.build_category_chain(category, paths)
            for category, paths in self.category_map.items()
        }
        orchestrator = RunnableParallel(category_chains)
        return orchestrator.invoke({})
