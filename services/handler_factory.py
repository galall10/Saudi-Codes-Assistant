from handlers.electricity_handler import ElectricityHandler
from handlers.plumbing_handler import PlumbingHandler
class HandlerFactory:
    @staticmethod
    def get_handler(category: str):
        if category == "electricity":
            return ElectricityHandler()
        if category == "plumbing":
            return PlumbingHandler()
        raise ValueError(f"Unsupported category: {category}")
