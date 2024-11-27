from ..lib.config import Config
from ..lib.history import HistoryManager
from ..api.ollama import OllamaClient
from .prompt import Prompt

async def start_chat(config: Config) -> None:
    """Initialize and start the chat session"""
    history_manager = HistoryManager(config)
    ollama_client = OllamaClient(config)
    
    prompt = Prompt(config, history_manager, ollama_client)
    await prompt.chat_loop()
