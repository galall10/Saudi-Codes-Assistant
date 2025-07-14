from typing import Dict, List, Any
from langchain_core.runnables import RunnableParallel, RunnableSequence, RunnableLambda
from services.handler_factory import HandlerFactory
import logging

class ComplianceOrchestrator:
    def __init__(self, category_map: Dict[str, List[str]]):
        """
        category_map: { "electricity": ["image1.jpg", "image2.jpg"], ... }
        """
        self.category_map = category_map
        self.logger = logging.getLogger(__name__)

    def _safe_validate_image(self, handler, image_path: str) -> Dict[str, Any]:
        """Safely validate image with error handling"""
        try:
            return handler.validate_image(image_path)
        except Exception as e:
            self.logger.error(f"Error validating image {image_path}: {str(e)}")
            return {
                "is_valid": False,
                "reason": f"خطأ في التحقق من الصورة: {str(e)}"
            }

    def _safe_analyze_image(self, handler, image_path: str, validation_result: Dict) -> Dict[str, Any]:
        """Safely analyze image with error handling"""
        if not validation_result.get("is_valid", False):
            return {
                "skipped": True,
                "reason": validation_result.get("reason", "فشل التحقق من الصورة")
            }

        try:
            return handler.analyze_image(image_path)
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {str(e)}")
            return {
                "skipped": True,
                "reason": f"خطأ في تحليل الصورة: {str(e)}"
            }

    def _safe_get_compliance(self, handler, analysis_result: Dict) -> Dict[str, Any]:
        """Safely get compliance analysis with error handling"""
        if analysis_result.get("skipped", False):
            return analysis_result

        if "description" not in analysis_result:
            return {
                "skipped": True,
                "reason": "لم يتم العثور على وصف للصورة"
            }

        try:
            return handler.get_compliance_analysis(analysis_result["description"])
        except Exception as e:
            self.logger.error(f"Error getting compliance analysis: {str(e)}")
            return {
                "description": analysis_result.get("description", ""),
                "code_matches": [],
                "error": f"خطأ في تحليل المطابقة: {str(e)}"
            }

    def build_image_chain(self, handler, image_path: str) -> RunnableSequence:
        """Build processing chain for a single image"""
        return RunnableSequence([
            RunnableLambda(lambda _: self._safe_validate_image(handler, image_path)),
            RunnableLambda(lambda result: self._safe_analyze_image(handler, image_path, result)),
            RunnableLambda(lambda analysis: self._safe_get_compliance(handler, analysis))
        ])

    def build_category_chain(self, category: str, image_paths: List[str]) -> RunnableParallel:
        """Build processing chain for a category"""
        try:
            handler = HandlerFactory.get_handler(category)
            return RunnableParallel({
                image_path: self.build_image_chain(handler, image_path)
                for image_path in image_paths
            })
        except Exception as e:
            self.logger.error(f"Error creating handler for category {category}: {str(e)}")
            # Return a chain that produces error results for all images
            return RunnableParallel({
                image_path: RunnableLambda(lambda _: {
                    "skipped": True,
                    "reason": f"خطأ في إنشاء معالج الفئة {category}: {str(e)}"
                })
                for image_path in image_paths
            })

    def run(self) -> Dict[str, Any]:
        """Run the compliance orchestrator"""
        try:
            category_chains = {
                category: self.build_category_chain(category, paths)
                for category, paths in self.category_map.items()
            }

            orchestrator = RunnableParallel(category_chains)
            return orchestrator.invoke({})

        except Exception as e:
            self.logger.error(f"Error running orchestrator: {str(e)}")
            return {
                "error": f"خطأ في تشغيل النظام: {str(e)}",
                "categories": list(self.category_map.keys())
            }

    def get_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of the orchestrator results"""
        summary = {
            "total_categories": len(self.category_map),
            "total_images": sum(len(paths) for paths in self.category_map.values()),
            "processed_successfully": 0,
            "validation_failures": 0,
            "processing_errors": 0,
            "categories_summary": {}
        }

        for category, category_results in results.items():
            if category == "error":
                continue

            category_summary = {
                "total_images": len(category_results),
                "successful": 0,
                "failed_validation": 0,
                "processing_errors": 0
            }

            for image_path, image_result in category_results.items():
                if image_result.get("skipped", False):
                    if "تحقق" in image_result.get("reason", ""):
                        category_summary["failed_validation"] += 1
                        summary["validation_failures"] += 1
                    else:
                        category_summary["processing_errors"] += 1
                        summary["processing_errors"] += 1
                elif "code_matches" in image_result:
                    category_summary["successful"] += 1
                    summary["processed_successfully"] += 1
                else:
                    category_summary["processing_errors"] += 1
                    summary["processing_errors"] += 1

            summary["categories_summary"][category] = category_summary

        return summary