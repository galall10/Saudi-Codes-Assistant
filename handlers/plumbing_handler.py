# handlers/plumbing_handler.py
from services.rag_engine import RAGEngine
from typing import  List
from handlers.base_handler import BaseHandler


class PlumbingHandler(BaseHandler):
    def __init__(self):
        super().__init__("plumbing")

    def _initialize_rag(self):
        self.rag_engine = RAGEngine("plumbing")

    @property
    def validation_prompt(self) -> str:
        return """
        أنت خبير في أنظمة السباكة. قم بتحليل هذه الصورة للتأكد من أنها تحتوي على:
        - أنابيب المياه أو الصرف
        - تركيبات صحية (حنفيات، مراحيض، مغاسل)
        - صمامات أو وصلات
        - أنظمة ضخ أو تصريف 
        إذا كانت الصورة تحتوي على هذه العناصر بشكل أساسي، فهي مناسبة لفئة السباكة.
        """

    @property
    def vision_analysis_prompt(self) -> str:
        return """
        انت سباك خبير، اوصف كل ما له علاقه بالسباكه في هذه الصوره بشكل مفصل.
        """

    @property
    def compliance_analysis_prompt(self) -> str:
        return """
        أنت خبير في الكود السعودي للسباكة:
        1. نوع التركيبات الصحية الموجودة
        2. مدى مطابقتها للكود السعودي
        3. المخالفات المحتملة
        4. التوصيات للتحسين
        ركز على:
        - جودة التوصيلات
        - المواد المستخدمة
        - الميول والانحدارات
        - متطلبات السلامة الصحية
        """

    @property
    def validation_keywords(self) -> List[str]:
        return [
            "سباكة", "أنابيب", "مياه", "صرف", "حنفيات",
            "مراحيض", "صمامات", "مضخات", "صحي"
        ]