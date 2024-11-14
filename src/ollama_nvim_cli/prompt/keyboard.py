from prompt_toolkit.key_binding import KeyBindings
from rich.table import Table
from rich.panel import Panel
from pathlib import Path
import time


class KeyboardHandler:
    def __init__(self, chat_interface):
        self.chat = chat_interface
        self.kb = KeyBindings()
        self.start_time = time.time()
        self.setup_bindings()

    def display_stats(self):
        """Display session statistics"""
        elapsed_time = time.time() - self.start_time

        # Calculate statistics
        ai_chars = sum(
            len(msg["content"])
            for msg in self.chat.history_manager.messages
            if msg["role"] == "assistant"
        )
        user_chars = sum(
            len(msg["content"])
            for msg in self.chat.history_manager.messages
            if msg["role"] == "user"
        )
        total_chars = ai_chars + user_chars

        # Create stats table
        table = Table(show_header=False, expand=True, border_style="bold cyan")
        table.add_column("Metric", style="bold #f5e0dc")
        table.add_column("Value", style="#cba6f7")

        table.add_row("Model", self.chat.ollama_client.model)
        table.add_row("Session Duration", f"{elapsed_time:.2f} seconds")
        table.add_row("AI Characters", str(ai_chars))
        table.add_row("User Characters", str(user_chars))
        table.add_row("Total Characters", str(total_chars))
        table.add_row(
            "AI/User Ratio", f"{(ai_chars/user_chars if user_chars else 0):.2f}"
        )

        self.chat.console.print(
            Panel(
                table,
                title="Session Statistics",
                border_style="bold #89dceb",
                padding=(1, 1),
            )
        )

    def setup_bindings(self):
        @self.kb.add("c-d")
        def _(event):
            """Exit with statistics"""
            self.display_stats()
            event.app.exit()

        @self.kb.add("c-h")
        def _(event):
            """Show help"""
            help_file = Path("~/.config/ollama-nvim-cli/help.md").expanduser()
            if help_file.exists():
                self.chat.editor.open_file(str(help_file))

        @self.kb.add("c-e")
        def _(event):
            """Open current prompt in editor"""
            if event.current_buffer.text:
                new_text = self.chat.editor.open_temp_file(event.current_buffer.text)
                event.current_buffer.text = new_text

        @self.kb.add("escape", "e")
        def _(event):
            """Open last AI response in editor"""
            if self.chat.last_response:
                self.chat.editor.open_temp_file(self.chat.last_response)

        @self.kb.add("escape", "s")
        def _(event):
            """Show session picker"""
            recent_sessions = self.chat.history_manager.list_sessions()[:5]
            if recent_sessions:
                self.chat.console.print("\n[bold]Recent sessions:[/bold]")
                for i, s in enumerate(recent_sessions, 1):
                    self.chat.console.print(f"{i}. {s.name}")
