import httpx
import asyncio
from typing import List, Dict, AsyncGenerator
import json


class OllamaClient:
    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint
        if ":" not in model and "/" not in model:
            self.model = f"{model}:latest"
        else:
            self.model = model
        self.client = httpx.AsyncClient(base_url=endpoint)
        self._lock = asyncio.Lock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def list_models(self) -> List[Dict]:
        """Get list of available models from Ollama"""
        async with self._lock:
            async with self.client.get("/api/tags") as response:
                if response.status_code == 200:
                    return response.json().get("models", [])
                return []

    async def get_model_names(self) -> List[str]:
        """Get list of model names with their tags"""
        models = await self.list_models()
        return [model["name"] for model in models]

    @property
    def generate_url(self) -> str:
        return f"{self.endpoint}/api/generate"

    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
            },
        }

        try:
            async with self._lock:
                async with self.client.stream(
                    "POST", self.generate_url, json=data, timeout=30.0
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    yield chunk["response"]
                            except json.JSONDecodeError:
                                continue
        except httpx.HTTPError as e:
            print(f"Error communicating with Ollama: {str(e)}")
            yield "[Error communicating with Ollama]"
