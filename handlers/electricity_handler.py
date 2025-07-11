# handlers/electricity_handler.py
from services.rag_engine import RAGEngine
from services.image_analyzer import ImageAnalyzer
from services.image_validator import validate_image
from handlers.base_handler import BaseHandler


class ElectricityHandler(BaseHandler):
    validation_prompt = """
    أنت خبير في التركيبات الكهربائية. قم بتحليل هذه الصورة للتأكد من أنها تحتوي على:
    - تركيبات كهربائية (أسلاك، مفاتيح، مقابس)
    - لوحات كهربائية أو قواطع
    - كابلات أو أنابيب كهربائية
    - معدات كهربائية أخرى
    """

    vision_analysis_prompt = """ 
    انت كهربائي خبير، اوصف كل ما له علاقه بالكهرباء في هذه الصوره بشكل مفصل.
    """

    compliance_analysis_prompt = """
    أنت خبير في الكود السعودي للكهرباء:
    1. نوع التركيبات الكهربائية الموجودة
    2. مدى مطابقتها للكود السعودي
    3. المخالفات المحتملة
    4. التوصيات للتحسين

    ركز على:
    - سلامة التوصيلات
    - المسافات الآمنة
    - جودة التركيب
    - متطلبات السلامة
    """

    validation_keywords = ["أسلاك", "مفاتيح", "قواطع", "كابلات", "معدات"]

    def __init__(self):
        self.rag_engine = RAGEngine("electricity")

    def validate_image(self, image_path: str) -> dict:
        is_valid = validate_image(image_path, self.validation_prompt, self.validation_keywords)
        return {"is_valid": is_valid, "reason": "" if is_valid else "الصورة غير مناسبة لفئة الكهرباء"}

    def analyze_image(self, image_path: str) -> dict:
        description = ImageAnalyzer.describe(image_path, self.vision_analysis_prompt)
        return {"description": description}

    def get_compliance_analysis(self, description: str) -> dict:
        matches = self.rag_engine.query(description)
        return {
            "description": description,
            "code_matches": matches,
            "compliance_prompt_used": self.compliance_analysis_prompt
        }
