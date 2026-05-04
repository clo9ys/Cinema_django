from rest_framework.views import exception_handler
from rest_framework.response import Response

class ApplicationError(Exception):
    """Базовый класс для всех бизнес-ошибок"""
    def __init__(self, message):
        self.message = message

class AlreadySubscribedError(ApplicationError):
    pass

class AgeLimitError(ApplicationError):
    pass

ERROR_MAP = {
    "AlreadySubscribedError": (409, "ALREADY_HAS_SUBSCRIPTION"),
    "AgeLimitError": (403, "AGE_RESTRICTION"),
    "ObjectNotFoundError": (404, "NOT_FOUND"),
    "ValidationError": (400, "VALIDATION_ERROR"),
}

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ApplicationError):
        status_code, internal_code = ERROR_MAP.get(exc.__class__.__name__, (400, "APP_ERROR"))
        response = Response(
            data={"detail": exc.message},
            status=status_code
        )

    if response is not None:
        internal_code = ERROR_MAP.get(exc.__class__.__name__, (None, "ERROR"))[1]

        return Response(
            data={
                "error": {
                    "code": internal_code,
                    "status": response.status_code,
                    "message": format_error_message(response.data)
                }
            },
            status=response.status_code
        )
    return response

def format_error_message(data):
    """Извлекает читаемое сообщение"""
    if isinstance(data, dict):
        if 'detail' in data:
            return data['detail']
        for field, errors in data.items():
            if isinstance(errors, list) and errors:
                return f"{field}: {errors[0]}"
        return str(data)
    elif isinstance(data, list) and data:
        return str(data[0])
    return str(data)