from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.theme import Theme
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich.spinner import Spinner
from rich.live import Live
from datetime import datetime
from pathlib import Path
import time
import sys
import asyncio

from .keyboard import KeyboardHandler
from .editor import Editor

class Prompt:
    def __init__(self, config: dict, history_manager, ollama_client):
        self.config = config
        self.history_manager = history_manager
        self.ollama_client = ollama_client
        self.theme = config.get("theme", {})
        self.config_dir = Path(config.config_path).parent
        self.start_time = time.time()
        self.last_response = None
        self.editor = Editor(config.get("editor", "nvim"))

        # Initialize console with theme
        self.console = Console(
            theme=Theme({
                "info": self.theme.get("info", "cyan"),
                "warning": self.theme.get("warning", "yellow"),
                "error": self.theme.get("error", "red"),
                "user": self.theme.get("user_prompt", "green"),
                "assistant": self.theme.get("assistant", "blue"),
            })
        )

        # Initialize keyboard handler
        self.keyboard = KeyboardHandler(self)

        # Setup prompt session
        self.style = Style.from_dict({
            "prompt": f'bg:{config["theme"]["user_prompt"]} #000000',
            "rprompt": "bg:#ff0066 #ffffff",
        })

        self.session = PromptSession(
            message=HTML(
                '<style fg="green">you</style>'
                '<style fg="white">>>  </style>'
            ),
            style=self.style,
            key_bindings=self.keyboard.kb,
        )

    def format_header(self) -> str:
        """Format the welcome header with keyboard shortcuts"""
        model_name = self.ollama_client.model.split(":")[0]
        model_tag = (
            self.ollama_client.model.split(":")[1]
            if ":" in self.ollama_client.model
            else "latest"
        )
        
        shortcuts = Table(show_header=False, box=None, expand=True)
        shortcuts.add_column("Shortcut", style="bold cyan", justify="right")
        shortcuts.add_column("Description", style="dim", justify="left")
        
        shortcuts.add_row("Ctrl+H or F1", "Show help")
        shortcuts.add_row("Ctrl+I", "Edit current prompt")
        shortcuts.add_row("Esc, E", "Edit last response")
        shortcuts.add_row("Esc, S", "Show sessions")
        shortcuts.add_row("Ctrl+D or Ctrl+C", "Exit")
        
        # Render the table to a string
        console = Console(width=80, record=True)  # Adjust width as needed
        console.print(shortcuts)
        table_str = console.export_text()
        
        return Panel(
            Align.center(
                f"\n[cyan bold]Welcome to Ollama Chat![/]\n"
                f"[yellow]Using model: {model_name} ({model_tag})[/]\n\n"
                "[bold]Keyboard Shortcuts:[/]\n"
                f"{table_str}\n"
            ),
            border_style="cyan",
            padding=(1, 2),
        )

    async def process_response(self, response_generator):
        accumulated_response = ""
        start_time = time.time()
        spinner = Spinner("dots")
        model_name = self.ollama_client.model.split(":")[0]

        async def update_spinner():
            while True:
                current_time = time.time()
                yield f"{spinner.render(current_time)} Generating response... {current_time - start_time:.1f}s"
                await asyncio.sleep(0.1)

        spinner_gen = update_spinner()
        
        with Live(
            await anext(spinner_gen),  # Get first spinner frame
            console=self.console,
            refresh_per_second=10
        ) as live:
            async for chunk in response_generator:
                accumulated_response += chunk
                try:
                    live.update(await anext(spinner_gen))
                except StopAsyncIteration:
                    break

        # Clear any remaining loading indicator
        self.console.print("\r" + " " * 80 + "\r", end="")

        # Print AI response with model prefix, new line, and left alignment
        self.console.print(f"\n[blue]{model_name}[/][white]>>>[/]")
        self.console.print(accumulated_response.strip(), soft_wrap=True)
        self.console.print()  # Add an extra newline

        return accumulated_response

    async def chat_loop(self) -> None:
        """Main chat loop"""
        self.console.print(Panel(self.format_header()))

        while True:
            try:
                user_input = await self.session.prompt_async()
                if user_input is None or user_input.strip().lower() in ['exit', 'quit']:
                    break

                user_input = user_input.strip()
                if not user_input:
                    continue

                self.history_manager.add_message("user", user_input)
                response_generator = self.ollama_client.generate(user_input)
                self.last_response = await self.process_response(response_generator)
                self.history_manager.add_message("assistant", self.last_response)

            except KeyboardInterrupt:
                self.console.print("\n[yellow]Goodbye![/]")
                sys.exit(0)
            except EOFError:
                self.console.print("\n[yellow]Goodbye![/]")
                sys.exit(0)
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/]")
                continue 