# app.py
from flask import Flask, request, jsonify

from orchestrator import ComplianceOrchestrator
from config import Config
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
    try:
        data = request.get_json()

        if not data or not isinstance(data, dict):
            return jsonify({"error": "البيانات غير صحيحة. يجب إرسال JSON يحتوي على الفئات والصور"}), 400

        orchestrator = SimpleComplianceOrchestrator(data)
        results = orchestrator.run()
        summary = orchestrator.get_summary(results)

        return jsonify({
            "results": results,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": f"حدث خطأ: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
