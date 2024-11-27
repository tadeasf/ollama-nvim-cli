import typer
from rich.console import Console
from pathlib import Path
import asyncio
from typing import Optional
from ollama_nvim_cli.lib.config import Config
from ollama_nvim_cli.lib.history import HistoryManager
from ollama_nvim_cli.prompt.prompt import Prompt
from ollama_nvim_cli.api.ollama import OllamaClient

app = typer.Typer(help="Ollama Chat CLI")
console = Console()

@app.command()
def main(
    model: Optional[str] = typer.Option(None, help="Model to use for chat"),
    config_file: str = typer.Option(
        "~/.config/ollama-nvim-cli/config.json",
        help="Path to config file"
    ),
    list_sessions: bool = typer.Option(
        False,
        "--list-sessions",
        "-l",
        help="List recent chat sessions"
    ),
) -> None:
    """Start a chat session with an Ollama model"""
    try:
        # Initialize config with expanded path
        config = Config(str(Path(config_file).expanduser()))
        
        if model:
            config.set("model", model)

        # Ensure history directory is created
        history_dir = Path(config.get("history", {}).get("save_dir", "~/.local/share/ollama-nvim-cli/history")).expanduser()
        history_dir.mkdir(parents=True, exist_ok=True)
        
        # Pass the config object, not the Path object
        history_manager = HistoryManager(config)
        
        if list_sessions:
            sessions_table = history_manager.format_sessions()
            if sessions_table:
                console.print(sessions_table)
            else:
                console.print("[yellow]No previous sessions found[/yellow]")
            return

        ollama_client = OllamaClient(config)
        prompt = Prompt(config, history_manager, ollama_client)
        
        asyncio.run(prompt.chat_loop())

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
