from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Кастомный обработчик исключений для унификации формата ошибок.
    Оборачивает стандартные ошибки DRF в единый формат.
    """
    # стандартный обработчик DRF
    response = exception_handler(exc, context)

    # Если стандартный обработчик вернул ответ — оборачиваем его
    if response is not None:
        return Response(
            {
                "error": {
                    "code": response.status_code,
                    "message": format_error_message(response.data)
                }
            },
            status=response.status_code
        )

    # Для необработанных исключений возвращаем стандартный ответ
    return response


def format_error_message(data):
    """
    Извлекает читаемое сообщение из ошибки DRF
    """
    if isinstance(data, dict):
        # если есть детали
        if 'detail' in data:
            return data['detail']
        # если ошибки по полям
        for field, errors in data.items():
            if isinstance(errors, list) and errors:
                return f"{field}: {errors[0]}"
        return str(data)
    elif isinstance(data, list) and data:
        return str(data[0])
    return str(data)