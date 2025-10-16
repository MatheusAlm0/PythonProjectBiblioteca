from exceptions.custom_exceptions import BadRequestException

class ValidationService:
    @staticmethod
    def validate_search_query(query):
        if not query or not query.strip():
            raise BadRequestException("O parâmetro 'q' é obrigatório e não pode estar vazio.")

    @staticmethod
    def validate_chat_message(message):
        if not message or not str(message).strip():
            raise BadRequestException("O campo 'message' é obrigatório e não pode estar vazio.")