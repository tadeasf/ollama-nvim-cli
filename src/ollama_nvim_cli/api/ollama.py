import httpx
import asyncio
from typing import List, Dict, AsyncGenerator
import json
from ..lib.config import Config


class OllamaClient:
    def __init__(self, config: Config):
        """Initialize Ollama client with config"""
        self.config = config
        self.model = config.get("model")
        
        if not self.model:
            # Prompt user for model if not set
            from rich.prompt import Prompt
            available_models = ["qwen2.5-coder:latest", "mistral:latest", "llama2:latest"]
            self.model = Prompt.ask(
                "Choose a model",
                choices=available_models,
                default="qwen2.5-coder:latest"
            )
            # Save to config
            self.config.set("model", self.model)
        
        ollama_config = config.get("ollama", {})
        self.host = ollama_config.get("host", "http://localhost:11434")
        self.timeout = ollama_config.get("timeout", 30)
        self.client = httpx.AsyncClient(base_url=self.host)
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
        return f"{self.host}/api/generate"

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
                    "POST", self.generate_url, json=data, timeout=self.timeout
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
