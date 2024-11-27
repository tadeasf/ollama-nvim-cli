from rich.console import Console
import typer
import os
from ...lib.config import Config
from ...prompt.editor import Editor

console = Console()


def config_command() -> None:
    """Open and edit configuration file"""
    try:
        config = Config()

        # Try to find available editor
        editors = ["lvim", "nvim", "vim", "vi"]
        selected_editor = None
        for editor in editors:
            if os.system(f"which {editor} > /dev/null 2>&1") == 0:
                selected_editor = editor
                break

        if not selected_editor:
            console.print(
                "[red]No suitable editor found. Please install nvim or vim.[/red]"
            )
            raise typer.Exit(1)

        # Open config in editor
        editor = Editor(selected_editor)
        editor.open_file(str(config.config_file))

        # Reload and display config
        config = Config()  # Reload config
        console.print("\n[bold green]Current Configuration:[/bold green]")
        console.print(f"[cyan]Model:[/cyan] {config.config['model']}")
        console.print(f"[cyan]Endpoint:[/cyan] {config.config['endpoint']}")
        console.print(f"[cyan]Editor:[/cyan] {config.config['editor']}")
        console.print(f"[cyan]History Path:[/cyan] {config.config['history_path']}")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)
