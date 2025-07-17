from typing import Dict, List, Any
from services.handler_factory import HandlerFactory
import logging

class SimpleComplianceOrchestrator:
    def __init__(self, category_map: Dict[str, List[str]]):
        self.category_map = category_map
        self.logger = logging.getLogger(__name__)

    def _safe_validate_image(self, handler, image_path: str) -> Dict[str, Any]:
        try:
            return handler.validate_image(image_path)
        except Exception as e:
            self.logger.error(f"Error validating image {image_path}: {str(e)}")
            return {
                "is_valid": False,
                "reason": f"Image validation error: {str(e)}"
            }

    def _safe_analyze_image(self, handler, image_path: str, validation_result: Dict) -> Dict[str, Any]:
        if not validation_result.get("is_valid", False):
            return {
                "skipped": True,
                "reason": validation_result.get("reason", "Image validation failed")
            }

        try:
            return handler.analyze_image(image_path)
        except Exception as e:
            self.logger.error(f"Error analyzing image {image_path}: {str(e)}")
            return {
                "skipped": True,
                "reason": f"Image analysis error: {str(e)}"
            }

    def _safe_get_compliance(self, handler, analysis_result: Dict) -> Dict[str, Any]:
        if analysis_result.get("skipped", False):
            return analysis_result

        if "description" not in analysis_result:
            return {
                "skipped": True,
                "reason": "No image description found"
            }

        try:
            return handler.get_compliance_analysis(analysis_result["description"])
        except Exception as e:
            self.logger.error(f"Error getting compliance analysis: {str(e)}")
            return {
                "description": analysis_result.get("description", ""),
                "code_matches": [],
                "error": f"Compliance analysis error: {str(e)}"
            }

    def run(self) -> Dict[str, Any]:
        """Runs compliance checks serially without parallel processing"""
        results = {}
        try:
            for category, image_paths in self.category_map.items():
                try:
                    handler = HandlerFactory.get_handler(category)
                except Exception as e:
                    results[category] = {
                        path: {
                            "skipped": True,
                            "reason": f"Failed to create handler: {str(e)}"
                        } for path in image_paths
                    }
                    continue

                results[category] = {}
                for image_path in image_paths:
                    validation = self._safe_validate_image(handler, image_path)
                    analysis = self._safe_analyze_image(handler, image_path, validation)
                    compliance = self._safe_get_compliance(handler, analysis)
                    results[category][image_path] = compliance

            return results

        except Exception as e:
            self.logger.error(f"Error running orchestrator: {str(e)}")
            return {
                "error": f"System execution error: {str(e)}",
                "categories": list(self.category_map.keys())
            }

    def get_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary from the compliance results"""
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
                    reason = image_result.get("reason", "")
                    if "validation" in reason or "suitable" in reason:
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
