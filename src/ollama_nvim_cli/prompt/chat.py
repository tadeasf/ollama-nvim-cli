from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.theme import Theme
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from rich.syntax import Syntax
from catppuccin.extras.pygments import MochaStyle
from .editor import Editor
from ..lib.history import HistoryManager
from ..api.ollama import OllamaClient
from .keyboard import KeyboardHandler
import re


class ChatInterface:
    def __init__(
        self, config: dict, history_manager: HistoryManager, ollama_client: OllamaClient
    ):
        self.editor = Editor(config["editor"])
        self.history_manager = history_manager
        self.ollama_client = ollama_client
        self.theme = config.get("theme", {})
        self.console = Console(
            theme=Theme(
                {
                    "info": self.theme.get("info", "cyan"),
                    "warning": self.theme.get("warning", "yellow"),
                    "error": self.theme.get("error", "red"),
                    "user": self.theme.get("user_prompt", "green"),
                    "assistant": self.theme.get("assistant", "blue"),
                }
            )
        )
        self.last_response = None
        self.keyboard = KeyboardHandler(self)

        self.style = Style.from_dict(
            {
                "prompt": f'bg:{config["theme"]["user_prompt"]} #000000',
                "rprompt": "bg:#ff0066 #ffffff",
            }
        )

        self.session = PromptSession(
            message=HTML('<style fg="green">you</style> >>> '),
            style=self.style,
            key_bindings=self.keyboard.kb,
        )

    def format_header(self) -> str:
        model_name = self.ollama_client.model.split(":")[0]
        model_tag = (
            self.ollama_client.model.split(":")[1]
            if ":" in self.ollama_client.model
            else "latest"
        )
        return (
            "[cyan bold]Welcome to Ollama Chat![/]\n"
            f"[yellow]Using model: {model_name} ({model_tag})[/]"
        )

    async def process_response(self, response_generator) -> str:
        tokens = 0
        total_expected = 100
        accumulated_response = ""

        with Progress(
            SpinnerColumn(spinner_name="dots"),
            BarColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Generating response...", total=total_expected
            )

            async for chunk in response_generator:
                accumulated_response += chunk
                tokens += 1
                progress.update(task, completed=min(tokens, total_expected))

        return accumulated_response

    async def chat_loop(self) -> None:
        self.console.print(Panel(self.format_header()))

        while True:
            try:
                # Get user input with prompt_toolkit
                user_input = await self.session.prompt_async()

                if not user_input.strip():
                    continue

                self.history_manager.add_message("user", user_input)

                # Generate and display response
                response_generator = self.ollama_client.generate(user_input)
                self.last_response = await self.process_response(response_generator)

                # Format and display response with markdown
                self.format_markdown(self.last_response)

                self.history_manager.add_message("assistant", self.last_response)

            except KeyboardInterrupt:
                continue
            except EOFError:
                self.console.print("[yellow]Goodbye![/]")
                break

    def format_markdown(self, content: str) -> None:
        """Format and display markdown content with code blocks."""
        parts = re.split(r"(```[\s\S]*?```)", content)

        for part in parts:
            if part.startswith("```") and part.endswith("```"):
                # Handle code blocks
                lines = part.split("\n")
                language = lines[0].strip("`").strip() or "text"
                code = "\n".join(lines[1:-1])

                syntax = Syntax(
                    code,
                    language,
                    theme=MochaStyle,
                    line_numbers=True,
                    word_wrap=True,
                )
                self.console.print(
                    Panel(
                        syntax,
                        expand=False,
                        border_style=self.theme.get("assistant", "blue"),
                        title=f"Code Block - {language}",
                        title_align="left",
                    )
                )
            else:
                # Handle regular markdown
                if part.strip():
                    self.console.print(Markdown(part.strip()))
