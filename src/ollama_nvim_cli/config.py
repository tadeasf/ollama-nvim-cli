from pathlib import Path
import pyaml
from typing import Dict, Any
import os


class Config:
    DEFAULT_CONFIG = {
        "endpoint": "http://localhost:11434",
        "model": "mistral",
        "history_path": "~/.config/ollama-nvim-cli/history",
        "editor": "lvim",
        "theme": {
            "user_prompt": "#a6e3a1",  # Catppuccin Green
            "assistant": "#89b4fa",  # Catppuccin Blue
            "error": "#f38ba8",  # Catppuccin Red
            "info": "#89dceb",  # Catppuccin Sky
        },
    }

    def __init__(self):
        self.config_dir = Path(os.path.expanduser("~/.config/ollama-nvim-cli"))
        self.config_file = self.config_dir / "config.yaml"
        self.history_dir = self.config_dir / "history"
        self.ensure_directories()
        self.config = self.load_config()

    def ensure_directories(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return self.DEFAULT_CONFIG

        with open(self.config_file, "r") as f:
            return {**self.DEFAULT_CONFIG, **pyaml.load(f)}
