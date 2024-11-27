from pathlib import Path
import json
import os
from typing import Optional, Any
from rich.console import Console
from rich.prompt import Prompt as RichPrompt

console = Console()

class Config:
    def __init__(self, config_path: Path | str = "~/.config/ollama-nvim-cli/config.json"):
        """Initialize config with path"""
        if isinstance(config_path, str):
            config_path = Path(config_path).expanduser()
        
        self.config_path = config_path
        self.config_dir = self.config_path.parent
        self._ensure_config_dir()
        self._config = self._load_config()
        self._validate_and_fix_config()

    def __getitem__(self, key: str) -> Any:
        """Allow dictionary-style access to config"""
        return self._config[key]

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value with a default"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a config value"""
        self._config[key] = value
        self._save_config()

    def _save_config(self) -> None:
        """Save current config to file"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self._config, f, indent=4)
        except Exception as e:
            raise Exception(f"Failed to save config: {str(e)}")

    def _ensure_config_dir(self) -> None:
        """Ensure config directory exists with all necessary files"""
        try:
            # Create config directory if it doesn't exist
            self.config_dir.mkdir(parents=True, exist_ok=True)

            # Create help.md if it doesn't exist
            help_file = self.config_dir / "help.md"
            if not help_file.exists():
                self._create_help_file(help_file)

            # Create templates directory if it doesn't exist
            templates_dir = self.config_dir / "templates"
            templates_dir.mkdir(exist_ok=True)

            # Create default template if it doesn't exist
            default_template = templates_dir / "default.md"
            if not default_template.exists():
                self._create_default_template(default_template)

        except Exception as e:
            raise Exception(f"Failed to initialize config directory: {str(e)}")

    def _create_help_file(self, help_file: Path) -> None:
        """Create default help.md file"""
        help_content = """# Ollama Chat Help

## Keyboard Shortcuts
- `Ctrl+H` or `F1`: Show this help
- `Ctrl+I`: Edit current prompt in editor
- `Esc, E`: Edit last AI response in editor
- `Esc, S`: Show session picker
- `Ctrl+D` or `Ctrl+C`: Exit with statistics

## Commands
- `/template <name>`: Load template from templates directory
- `/clear`: Clear current session
- `/exit` or `/quit`: Exit chat
- `/help`: Show this help

## Configuration
Config file is located at: ~/.config/ollama-nvim-cli/config.json
"""
        help_file.write_text(help_content)

    def _create_default_template(self, template_file: Path) -> None:
        """Create default template file"""
        default_content = """You are an AI assistant. Please help me with my questions.

Context: {context}

Question: {question}"""
        template_file.write_text(default_content)

    def _load_config(self) -> dict:
        """Load config from file or create default"""
        if not self.config_path.exists():
            self._create_default_config()
        
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except Exception as e:
            raise Exception(f"Failed to load config: {str(e)}")

    def _create_default_config(self) -> None:
        """Create default config file"""
        default_config = {
            "model": None,  # Will be prompted
            "editor": None,  # Will be prompted
            "theme": {
                "user_prompt": "green",
                "assistant": "blue",
                "info": "cyan",
                "warning": "yellow",
                "error": "red"
            },
            "ollama": {
                "host": None,  # Will be prompted
                "timeout": 30
            },
            "history": {
                "save_dir": None,  # Will be prompted
                "max_sessions": 50
            }
        }

        try:
            with open(self.config_path, "w") as f:
                json.dump(default_config, f, indent=4)
        except Exception as e:
            raise Exception(f"Failed to create default config: {str(e)}")

    def _validate_and_fix_config(self) -> None:
        """Validate required settings and prompt user for missing ones"""
        required_settings = {
            "model": {
                "prompt": "Enter the model name (e.g., qwen2.5-coder:latest): ",
                "default": "qwen2.5-coder:latest"
            },
            "ollama.host": {
                "prompt": "Enter Ollama host URL: ",
                "default": "http://localhost:11434"
            },
            "editor": {
                "prompt": "Enter preferred editor (nvim, vim, etc.): ",
                "default": "nvim"
            },
            "history.save_dir": {
                "prompt": "Enter history save directory: ",
                "default": "~/.local/share/ollama-nvim-cli/history"
            }
        }

        changed = False
        for setting, options in required_settings.items():
            keys = setting.split('.')
            current = self._config
            
            # Check nested keys
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            
            last_key = keys[-1]
            if last_key not in current or not current[last_key]:
                console.print(f"[yellow]Missing or invalid setting: {setting}[/yellow]")
                value = RichPrompt.ask(
                    options["prompt"],
                    default=options["default"]
                )
                current[last_key] = value
                changed = True

        if changed:
            self._save_config()
            console.print("[green]Configuration updated successfully![/green]")
