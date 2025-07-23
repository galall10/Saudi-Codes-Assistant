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

    def run_with_tables(self) -> Dict[str, Any]:
        """
        Runs compliance checks and generates table JSON for each category

        Returns:
            Dictionary with compliance tables for each category
        """
        results = {
            "compliance_tables": {},
            "processing_summary": {},
            "errors": []
        }

        try:
            for category, image_paths in self.category_map.items():
                self.logger.info(f"Processing category: {category}")

                try:
                    handler = HandlerFactory.get_handler(category)
                except Exception as e:
                    error_msg = f"Failed to create handler for {category}: {str(e)}"
                    self.logger.error(error_msg)
                    results["errors"].append(error_msg)
                    results["compliance_tables"][category] = {
                        "error": error_msg,
                        "category": category
                    }
                    continue

                # Process all images in the category
                category_compliance_analyses = []
                category_processing_summary = {
                    "total_images": len(image_paths),
                    "processed_successfully": 0,
                    "validation_failures": 0,
                    "processing_errors": 0,
                    "image_details": {}
                }

                for image_path in image_paths:
                    self.logger.info(f"Processing image: {image_path}")

                    # Process individual image
                    validation = self._safe_validate_image(handler, image_path)
                    analysis = self._safe_analyze_image(handler, image_path, validation)
                    compliance = self._safe_get_compliance(handler, analysis)

                    # Track processing results
                    category_processing_summary["image_details"][image_path] = {
                        "validation_passed": validation.get("is_valid", False),
                        "analysis_successful": not analysis.get("skipped", False),
                        "compliance_successful": not compliance.get("skipped", False) and "error" not in compliance
                    }

                    if compliance.get("skipped", False):
                        reason = compliance.get("reason", "")
                        if "validation" in reason:
                            category_processing_summary["validation_failures"] += 1
                        else:
                            category_processing_summary["processing_errors"] += 1
                    elif "error" in compliance:
                        category_processing_summary["processing_errors"] += 1
                    else:
                        category_processing_summary["processed_successfully"] += 1
                        category_compliance_analyses.append(compliance)

                # Generate compliance table for the category
                try:
                    compliance_table = handler.generate_compliance_table(category_compliance_analyses)
                    results["compliance_tables"][category] = compliance_table
                    self.logger.info(f"Successfully generated compliance table for {category}")
                except Exception as e:
                    error_msg = f"Error generating compliance table for {category}: {str(e)}"
                    self.logger.error(error_msg)
                    results["errors"].append(error_msg)
                    results["compliance_tables"][category] = {
                        "error": error_msg,
                        "category": category
                    }

                results["processing_summary"][category] = category_processing_summary

            return results

        except Exception as e:
            error_msg = f"Error running orchestrator: {str(e)}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)
            return results

    def run(self) -> Dict[str, Any]:
        """Original method - runs compliance checks without table generation"""
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