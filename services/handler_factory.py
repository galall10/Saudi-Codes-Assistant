from handlers.electricity_handler import ElectricityHandler

class HandlerFactory:
    @staticmethod
    def get_handler(category: str):
        if category == "electricity":
            return ElectricityHandler()
        raise ValueError(f"Unsupported category: {category}")
