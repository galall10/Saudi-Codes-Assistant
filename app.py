# app.py
from flask import Flask, request, jsonify
import os

from orchestrator.ComplianceOrchestrator import ComplianceOrchestrator
from orchestrator.orchestrator import Orchestrator
from config import Config
from scripts.build_all_vector_stores import build_all_vector_stores

app = Flask(__name__)
Config.create_dirs()  # Create folders on boot

build_all_vector_stores()

@app.route("/analyze", methods=["POST"])
def analyze():
    image = request.files.get("image")
    category = request.form.get("category")

    if not image or not category:
        return jsonify({"error": "Image and category are required"}), 400

    # Save the uploaded image
    image_path = os.path.join(Config.UPLOADS_DIR, image.filename)
    image.save(image_path)

    # Run through orchestrator
    result = Orchestrator.analyze_image(image_path, category)
    return jsonify(result), 200 if result.get("valid", True) else 400

@app.route("/parallel_analyze", methods=["POST"])
def analyze_images():
    data = request.get_json()  # يجب أن يكون في هيئة {"electricity": ["path1.jpg", ...], ...}

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid input format"}), 400

    orchestrator = ComplianceOrchestrator(data)
    results = orchestrator.run()

    return jsonify(results), 200

if __name__ == "__main__":
    app.run(debug=True)
