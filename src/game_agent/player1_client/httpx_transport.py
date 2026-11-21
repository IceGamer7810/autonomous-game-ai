"""httpx transport implementation kept separate from the client contract."""

import httpx


class HttpxTransport:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient()

    async def post(self, url: str, *, headers, json, timeout: float):
        response = await self._client.post(url, headers=headers, json=json, timeout=timeout)
        response.raise_for_status()
        return response

    async def aclose(self) -> None:
        await self._client.aclose()
