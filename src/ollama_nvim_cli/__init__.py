from .prompt.prompt import Prompt
from .lib.config import Config
from .lib.history import HistoryManager
from .api.ollama import OllamaClient

__version__ = "0.1.0"

__all__ = ["Prompt", "Config", "HistoryManager", "OllamaClient"]
