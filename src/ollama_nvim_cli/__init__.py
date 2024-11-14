from .prompt.chat import ChatInterface
from .lib.history import HistoryManager
from .lib.config import Config
from .api.ollama import OllamaClient

__version__ = "0.1.0"

__all__ = ["ChatInterface", "HistoryManager", "Config", "OllamaClient"]
