import asyncio
import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt
from ollama_nvim_cli.lib.config import Config
from ollama_nvim_cli.prompt.chat import ChatInterface
from ollama_nvim_cli.lib.history import HistoryManager
from ollama_nvim_cli.api.ollama import OllamaClient
import sys

app = typer.Typer(
    name="ollama-nvim-cli",
    help="A CLI tool for chatting with Ollama models using Neovim/LunarVim",
    add_completion=False,
)
console = Console()


@app.command()
def chat(
    model: str = typer.Option(
        None, "--model", "-m", help="Specify the Ollama model to use"
    ),
    session: Optional[Path] = typer.Option(
        None,
        "--session",
        "-s",
        help="Path to an existing session file to continue",
        exists=False,
        dir_okay=False,
        file_okay=True,
    ),
    list_sessions: bool = typer.Option(
        False, "--list", "-l", help="List recent chat sessions"
    ),
) -> None:
    """Start a chat session with an Ollama model"""
    try:
        # Set the event loop policy
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        else:
            asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

        config = Config()
        if model:
            config.config["model"] = model

        history_manager = HistoryManager(config.history_dir)

        if list_sessions:
            recent_sessions = history_manager.list_sessions()
            if not recent_sessions:
                console.print("[yellow]No previous sessions found[/yellow]")
                raise typer.Exit()

            console.print("\n[bold]Recent sessions:[/bold]")
            for s in recent_sessions:
                console.print(f"  • {s.name}")
            raise typer.Exit()

        ollama_client = OllamaClient(config.config["endpoint"], config.config["model"])

        if session:
            if not session.exists():
                console.print(f"[red]Session file {session} not found[/red]")
                raise typer.Exit(1)
            messages = history_manager.load_session(str(session))
            console.print(
                f"[green]Loaded session with {len(messages)} messages[/green]"
            )
        else:
            recent_sessions = history_manager.list_sessions()[:5]
            if recent_sessions:
                console.print("\n[bold]Recent sessions:[/bold]")
                for i, s in enumerate(recent_sessions, 1):
                    console.print(f"{i}. {s.name}")

                choice = Prompt.ask(
                    "\nSelect a session to continue (or press Enter for new session)",
                    default="",
                )

                if choice.isdigit() and 0 < int(choice) <= len(recent_sessions):
                    session = recent_sessions[int(choice) - 1]
                    messages = history_manager.load_session(str(session))
                    console.print(
                        f"[green]Loaded session with {len(messages)} messages[/green]"
                    )

        chat_interface = ChatInterface(config.config, history_manager, ollama_client)

        # Run the async chat loop
        asyncio.run(chat_interface.chat_loop())

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
