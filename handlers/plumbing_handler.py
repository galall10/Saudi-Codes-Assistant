# handlers/electricity_handler.py
from services.rag_engine import RAGEngine
from services.image_analyzer import ImageAnalyzer
from langchain_core.runnables import RunnableLambda
from services.image_validator import validate_image


# Prompts specific to electricity category
validation_prompt = """
أنت خبير في أنظمة السباكة. قم بتحليل هذه الصورة للتأكد من أنها تحتوي على:
- أنابيب المياه أو الصرف
- تركيبات صحية (حنفيات، مراحيض، مغاسل)
- صمامات أو وصلات
- أنظمة ضخ أو تصريف 
إذا كانت الصورة تحتوي على هذه العناصر بشكل أساسي، فهي مناسبة لفئة السباكة.  """

vision_analysis_prompt = """ 
انت سباك خبير، اوصف كل ما له علاقه بالسباكه في هذه الصوره بشكل مفصل.
"""

compliance_analysis_prompt = """
أنت خبير في الكود السعودي للسباكة. :
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
validation_keywords = ["سباكة", "أنابيب", "مياه", "صرف", "حنفيات", "مراحيض", "صمامات", "مضخات", "صحي"]
plumbing_rag = RAGEngine("plumbing")

def plumbing_pipeline(image_path: str):
    if not validate_image(image_path, validation_prompt, validation_keywords):
        return {"category": "plumbing", "valid": False, "reason": "الصورة غير مناسبة لفئة السباكه"}

    description = ImageAnalyzer.describe(image_path, vision_analysis_prompt)
    matches = plumbing_rag.query(description)

    return {
        "category": "plumbing",
        "valid": True,
        "description": description,
        "code_matches": matches,
        "compliance_prompt_used": compliance_analysis_prompt
    }

plumbing_runnable = RunnableLambda(plumbing_pipeline)