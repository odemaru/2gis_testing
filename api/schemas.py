"""JSON-схемы ответов сервиса и помощник для их проверки."""

from typing import Any

from jsonschema import FormatChecker, validate

from api.constants import (
    COLORS,
    LAT_MAX,
    LAT_MIN,
    LON_MAX,
    LON_MIN,
    TITLE_MAX_LENGTH,
    TITLE_MIN_LENGTH,
)

#: Успешный ответ метода создания избранного места.
#:
#: Схема намеренно строгая: она описывает не просто «объект с полями», а весь
#: контракт из документации: диапазоны координат, длину названия и допустимые
#: цвета. Поэтому расхождения с документацией ловит сама схема, а не только
#: явные ассерты в тестах.
FAVORITE_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "title": {
            "type": "string",
            "minLength": TITLE_MIN_LENGTH,
            "maxLength": TITLE_MAX_LENGTH,
        },
        "lat": {"type": "number", "minimum": LAT_MIN, "maximum": LAT_MAX},
        "lon": {"type": "number", "minimum": LON_MIN, "maximum": LON_MAX},
        "color": {"type": ["string", "null"], "enum": [*COLORS, None]},
        "created_at": {"type": "string", "format": "date-time"},
    },
    "required": ["id", "title", "lat", "lon", "color", "created_at"],
    # ловит появление незадокументированных полей в ответе
    "additionalProperties": False,
}

#: Ответ сервиса с ошибкой: {"error": {"id": ..., "message": ...}}
ERROR_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "error": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "message": {"type": "string"},
            },
            "required": ["id", "message"],
            "additionalProperties": False,
        }
    },
    "required": ["error"],
    "additionalProperties": False,
}


def validate_schema(instance: Any, schema: dict[str, Any]) -> None:
    """Проверить объект по схеме, включая проверку format.

    По умолчанию jsonschema считает format аннотацией и не проверяет его,
    поэтому "format": "date-time" без format_checker не даёт никаких гарантий.
    Здесь checker передаётся явно. За реальную проверку date-time отвечает
    пакет rfc3339-validator из requirements.txt.
    """
    validate(instance=instance, schema=schema, format_checker=FormatChecker())
