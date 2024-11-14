from pathlib import Path
import yaml
import os
from rich.console import Console
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from ..api.ollama import OllamaClient


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

    CONFIG_TEMPLATE = """# Ollama NeoVim CLI Configuration

# API endpoint for Ollama
endpoint: "http://localhost:11434"

# Default model to use
model: "mistral"

# Path to store chat history
history_path: "~/.config/ollama-nvim-cli/history"

# Editor command to use for prompts
editor: "lvim"

# Theme configuration using Catppuccin colors
theme:
  user_prompt: "#a6e3a1"    # Color for user messages
  assistant: "#89b4fa"      # Color for assistant responses
  error: "#f38ba8"         # Color for error messages
  info: "#89dceb"          # Color for info messages
"""

    HELP_TEMPLATE = """# Ollama NeoVim CLI Keyboard Shortcuts

## Navigation
- `Ctrl+D`: Exit the CLI with session statistics
- `Ctrl+H`: Show this help file
- `Ctrl+E`: Open current prompt in editor
- `Alt+E`: Open last AI response in editor (or Esc, E)
- `Alt+W`: Show session picker (or Esc, S)
- `Alt+X`: Rename current session (or Esc, R)

## Tips
- Use arrow keys to navigate command history
- Empty prompt will be ignored
- Session statistics are shown on exit
"""

    def __init__(self):
        self.console = Console()
        self.config_dir = Path(os.path.expanduser("~/.config/ollama-nvim-cli"))
        self.config_file = self.config_dir / "config.yaml"
        self.history_dir = self.config_dir / "history"
        self.ensure_directories()
        self.config = self.load_config()

    def ensure_directories(self):
        # Create config directory if it doesn't exist
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
            self.console.print("[green]Created config directory[/green]")

        # Create history directory if it doesn't exist
        if not self.history_dir.exists():
            self.history_dir.mkdir(parents=True)
            self.console.print("[green]Created history directory[/green]")

        # Create config file with template if it doesn't exist
        if not self.config_file.exists():
            with open(self.config_file, "w") as f:
                f.write(self.CONFIG_TEMPLATE)
            self.console.print(
                "[green]Created config file with default settings[/green]"
            )

        # Create help file with template if it doesn't exist
        help_file = self.config_dir / "help.md"
        if not help_file.exists():
            help_file.parent.mkdir(parents=True, exist_ok=True)
            with open(help_file, "w") as f:
                f.write(self.HELP_TEMPLATE)
            self.console.print("[green]Created help file[/green]")

    def interactive_config(self) -> dict:
        """Create config interactively using prompt_toolkit"""
        self.console.print("[cyan]Welcome to Ollama NeoVim CLI setup![/]")

        # Get endpoint first
        endpoint = prompt(
            "Enter Ollama API endpoint: ", default="http://localhost:11434"
        )

        # Get available models from Ollama
        temp_client = OllamaClient(endpoint, "mistral")
        available_models = temp_client.get_model_names()

        if not available_models:
            self.console.print(
                "[yellow]Warning: No models found. Is Ollama running?[/]"
            )
            available_models = ["mistral:latest", "llama2:latest"]

        model_completer = WordCompleter(available_models)
        model = prompt(
            "Enter default model name: ",
            default="mistral:latest",
            completer=model_completer,
        )

        # Editor selection
        editor_completer = WordCompleter(["nvim", "lvim", "vim"])
        editor = prompt(
            "Enter editor command: ", default="lvim", completer=editor_completer
        )

        return {
            "endpoint": endpoint,
            "model": model,
            "editor": editor,
            "history_path": str(self.history_dir),
            "theme": self.DEFAULT_CONFIG["theme"],
        }

    def load_config(self) -> dict:
        if not self.config_file.exists():
            self.console.print("[yellow]No config file found.[/]")
            config = self.interactive_config()

            with open(self.config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False)

            self.console.print("[green]Config file created successfully![/]")
            return config

        with open(self.config_file) as f:
            return yaml.safe_load(f)
