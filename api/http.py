"""Транспортный слой.

Единственное место в проекте, которое знает про конкретную HTTP-библиотеку.
Замена requests на httpx или aiohttp затрагивает только этот файл. Клиент
и тесты работают через интерфейс Http.request().
"""

import logging

import requests
from requests import Response

logger = logging.getLogger("api")

#: до скольких символов обрезать тело в логах, чтобы title в 1000 знаков
#: не забивал вывод целиком
LOG_BODY_LIMIT = 300


def _shorten(value: object, limit: int = LOG_BODY_LIMIT) -> str:
    text = str(value)
    return text if len(text) <= limit else f"{text[:limit]}... [{len(text)} символов]"


class Http:
    """Обёртка над HTTP-библиотекой с логированием запросов и ответов."""

    def __init__(self, timeout: float = 15.0):
        self._timeout = timeout

    def request(self, method: str, url: str, **kwargs) -> Response:
        kwargs.setdefault("timeout", self._timeout)

        logger.info(
            "--> %s %s | data=%s | cookies=%s",
            method,
            url,
            _shorten(kwargs.get("data")),
            kwargs.get("cookies"),
        )
        response = requests.request(method, url, **kwargs)
        logger.info(
            "<-- %s %s | %s",
            response.status_code,
            response.reason,
            _shorten(response.text),
        )
        return response
