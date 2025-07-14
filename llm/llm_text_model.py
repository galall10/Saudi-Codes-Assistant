from utils.llm_models_utils import call_text_model

class LLMTextModel:
    @staticmethod
    def analyze(description: str, compliance_prompt: str) -> str:
        return call_text_model(description, compliance_prompt)
