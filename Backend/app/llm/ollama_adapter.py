from __future__ import annotations

import httpx
from typing import Any, Dict, List

from ..config import settings
from .provider import LLMProvider


class OllamaAdapter(LLMProvider):
    """Adapter that talks to a local Ollama runtime."""

    def __init__(self) -> None:
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_REQUEST_TIMEOUT

    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": float(max(0.0, min(temperature, 1.0))),
                "num_predict": max(1, max_tokens),
            },
        }
        payload["options"].update(kwargs.get("options", {}))
        response = await self._post("/api/generate", payload)
        return response.get("response", "")

    async def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": float(max(0.0, min(temperature, 1.0))),
                "num_predict": max(1, max_tokens),
            },
        }
        payload["options"].update(kwargs.get("options", {}))
        response = await self._post("/api/chat", payload)
        if "message" in response and isinstance(response["message"], dict):
            return response["message"].get("content", "")
        return response.get("response", "")

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            timeout = httpx.Timeout(
                connect=10.0,
                read=60.0,
                write=10.0,
                pool=10.0,
            )

            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)

            resp.raise_for_status()
            return resp.json()

        except httpx.ReadTimeout:
            raise RuntimeError("Ollama timed out while generating response.")
        except httpx.ConnectError:
            raise RuntimeError("Could not connect to Ollama. Is it running?")
        except Exception as exc:
            raise RuntimeError(f"Ollama request failed: {exc}") from exc


