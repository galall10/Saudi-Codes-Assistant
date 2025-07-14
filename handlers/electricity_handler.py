# handlers/electricity_handler.py
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
        أنت خبير في التركيبات الكهربائية. قم بتحليل هذه الصورة للتأكد من أنها تحتوي على:
        - تركيبات كهربائية (أسلاك، مفاتيح، مقابس)
        - لوحات كهربائية أو قواطع
        - كابلات أو أنابيب كهربائية
        - معدات كهربائية أخرى
        """

    @property
    def vision_analysis_prompt(self) -> str:
        return """ 
        انت كهربائي خبير، اوصف كل ما له علاقه بالكهرباء في هذه الصوره بشكل مفصل.
        """

    @property
    def compliance_analysis_prompt(self) -> str:
        return """
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

    @property
    def validation_keywords(self) -> List[str]:
        return ["أسلاك", "مفاتيح", "قواطع", "كابلات", "معدات"]

    # @property
    # def compliance_analysis_prompt(self) -> str:
    #     return (
    #         "من فضلك قم بتحليل الوصف التالي بناءً على الكود السعودي للأعمال الكهربائية SBC401، واستخرج جدولًا يحتوي على الأعمدة التالية:\n"
    #         "1- البند (مثلاً: الأفياش، التمديدات، الإنارة...)\n"
    #         "2- الحالة (مجتاز / غير مجتاز)\n"
    #         "3- الملاحظات باختصار (أخطاء أو تجاوزات)\n"
    #         "4- الموقع إن وُجد (مثلاً: غرفة النوم، المطبخ...)\n"
    #         "5- نسبة الالتزام التقريبية (%) لهذا البند\n\n"
    #         "بعد الجدول، أضف فقرة قصيرة توضح **مزايا العقار** (مثل جودة التركيب، توفر الحماية، التنظيم الجيد...) بصيغة هندسية رسمية.\n"
    #         "الإخراج يجب أن يكون نصًا منسقًا فقط بدون Markdown."
    #     )
