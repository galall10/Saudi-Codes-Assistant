# app.py
from flask import Flask, request, jsonify

from orchestrator import ComplianceOrchestrator
from config import Config
from scripts.build_all_vector_stores import build_all_vector_stores
from simple_orchestrator import SimpleComplianceOrchestrator

app = Flask(__name__)
Config.create_dirs()  # Create folders on boot

# build_all_vector_stores()

# @app.route("/analyze", methods=["POST"])
# def analyze():
#     image = request.files.get("image")
#     category = request.form.get("category")
#
#     if not image or not category:
#         return jsonify({"error": "Image and category are required"}), 400
#
#     # Save the uploaded image
#     image_path = os.path.join(Config.UPLOADS_DIR, image.filename)
#     image.save(image_path)
#
#     # Run through orchestrator
#     result = Orchestrator.analyze_image(image_path, category)
#     return jsonify(result), 200 if result.get("valid", True) else 400

@app.route("/api/parallel_analyze", methods=["POST"])
def analyze_images():
    data = request.get_json()  # يجب أن يكون في هيئة {"electricity": ["path1.jpg", ...], ...}

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input format"}), 400

    orchestrator = ComplianceOrchestrator(data)
    results = orchestrator.run()

    return jsonify(results), 200

# @app.route("/api/analyze_images", methods=["POST"])
# def analyze_images():
#
#     data = request.get_json()
#
#     if not isinstance(data, dict):
#         return jsonify({"error": "Invalid input format. Expected a dict of categories to image paths."}), 400
#
#     try:
#         orchestrator = ComplianceOrchestrator(category_map=data)
#         results = orchestrator.run()
#         summary = orchestrator.get_summary(results)
#
#         return jsonify({
#             "results": results,
#             "summary": summary
#         }), 200
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route("/api/simple_analyze", methods=["POST"])
def simple_analyze():
    """
    Analyze images and generate compliance tables

    Expected JSON format:
    {
        "category1": ["image1.jpg", "image2.jpg"],
        "category2": ["image3.jpg", "image4.jpg"],
        "generate_tables": true  // optional, defaults to true
    }
    """
    try:
        data = request.get_json()

        if not data or not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request format. Expected JSON with categories and photo paths.",
                "expected_format": {
                    "category_name": ["image1.jpg", "image2.jpg"],
                    "generate_tables": True
                }
            }), 400

        # Extract table generation preference
        generate_tables = data.pop("generate_tables", True)

        # Validate that we have category data
        if not data:
            return jsonify({
                "error": "No category data provided. Please include at least one category with image paths."
            }), 400

        # Validate category data structure
        for category, image_paths in data.items():
            if not isinstance(image_paths, list):
                return jsonify({
                    "error": f"Invalid format for category '{category}'. Expected list of image paths."
                }), 400

            if not image_paths:
                return jsonify({
                    "error": f"Category '{category}' has no image paths. Each category must have at least one image."
                }), 400

            # Validate that all paths are strings
            for path in image_paths:
                if not isinstance(path, str):
                    return jsonify({
                        "error": f"Invalid image path in category '{category}'. All paths must be strings."
                    }), 400

        # Initialize orchestrator
        orchestrator = SimpleComplianceOrchestrator(data)

        if generate_tables:
            # Generate compliance tables (new functionality)
            results = orchestrator.run_with_tables()

            return jsonify({
                "success": True,
                "compliance_tables": results["compliance_tables"],
                "processing_summary": results["processing_summary"],
                "errors": results["errors"],
                "total_categories": len(data),
                "total_images": sum(len(paths) for paths in data.values())
            })
        else:
            # Use original analysis method
            results = orchestrator.run()
            summary = orchestrator.get_summary(results)

            return jsonify({
                "success": True,
                "results": results,
                "summary": summary
            })

    except Exception as e:
        app.logger.error(f"Error in simple_analyze endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route("/api/analyze_with_tables", methods=["POST"])
def analyze_with_tables():
    """
    Dedicated endpoint for generating compliance tables

    Expected JSON format:
    {
        "category1": ["image1.jpg", "image2.jpg"],
        "category2": ["image3.jpg", "image4.jpg"]
    }
    """
    try:
        data = request.get_json()

        if not data or not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request format. Expected JSON with categories and photo paths.",
                "expected_format": {
                    "category_name": ["image1.jpg", "image2.jpg"]
                }
            }), 400

        # Validate category data structure
        for category, image_paths in data.items():
            if not isinstance(image_paths, list) or not image_paths:
                return jsonify({
                    "error": f"Invalid format for category '{category}'. Expected non-empty list of image paths."
                }), 400

        # Initialize orchestrator and generate tables
        orchestrator = SimpleComplianceOrchestrator(data)
        results = orchestrator.run_with_tables()

        return jsonify({
            "success": True,
            "compliance_tables": results["compliance_tables"],
            "processing_summary": results["processing_summary"],
            "errors": results["errors"],
            "metadata": {
                "total_categories": len(data),
                "total_images": sum(len(paths) for paths in data.values()),
                "categories_processed": list(results["compliance_tables"].keys())
            }
        })

    except Exception as e:
        app.logger.error(f"Error in analyze_with_tables endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route("/api/analyze_basic", methods=["POST"])
def analyze_basic():
    """
    Basic analysis endpoint (original functionality)

    Expected JSON format:
    {
        "category1": ["image1.jpg", "image2.jpg"],
        "category2": ["image3.jpg", "image4.jpg"]
    }
    """
    try:
        data = request.get_json()

        if not data or not isinstance(data, dict):
            return jsonify({
                "error": "Invalid request format. Expected JSON with categories and photo paths."
            }), 400

        # Validate category data structure
        for category, image_paths in data.items():
            if not isinstance(image_paths, list) or not image_paths:
                return jsonify({
                    "error": f"Invalid format for category '{category}'. Expected non-empty list of image paths."
                }), 400

        # Initialize orchestrator and run basic analysis
        orchestrator = SimpleComplianceOrchestrator(data)
        results = orchestrator.run()
        summary = orchestrator.get_summary(results)

        return jsonify({
            "success": True,
            "results": results,
            "summary": summary
        })

    except Exception as e:
        app.logger.error(f"Error in analyze_basic endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
