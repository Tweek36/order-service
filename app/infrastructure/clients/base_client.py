"""Базовый HTTP клиент."""

import httpx
import structlog

from app.settings import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class BaseHTTPClient:
    """Базовый класс для HTTP клиентов."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = httpx.Timeout(30.0)

    def _get_headers(self) -> dict[str, str]:
        """Получить заголовки для запроса."""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    async def _get(self, path: str) -> dict:
        """Выполнить GET запрос."""
        url = f"{self.base_url}{path}"

        await logger.ainfo("http_get_request", url=url)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._get_headers())
            response.raise_for_status()

            await logger.ainfo(
                "http_get_response",
                url=url,
                status_code=response.status_code,
            )

            return response.json()

    async def _post(self, path: str, json_data: dict) -> dict:
        """Выполнить POST запрос."""
        url = f"{self.base_url}{path}"

        await logger.ainfo("http_post_request", url=url)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                url, headers=self._get_headers(), json=json_data
            )
            response.raise_for_status()

            await logger.ainfo(
                "http_post_response",
                url=url,
                status_code=response.status_code,
            )

            return response.json()
