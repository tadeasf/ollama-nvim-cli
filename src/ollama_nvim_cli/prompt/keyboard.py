from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from rich.table import Table
from rich.panel import Panel
import time
import sys
from datetime import datetime


class KeyboardHandler:
    def __init__(self, interface):
        self.interface = interface
        self.kb = KeyBindings()
        self.setup_bindings()

    def setup_bindings(self):
        @self.kb.add("c-h")  # Just Ctrl+H for help
        def show_help(event):
            """Show help"""
            help_file = self.interface.config_dir / "help.md"
            if help_file.exists():
                self.interface.editor.open_file(str(help_file))

        @self.kb.add("backspace")
        def handle_backspace(event):
            """Handle backspace normally"""
            event.current_buffer.delete_before_cursor(1)

        @self.kb.add("c-d", "c-c", "c-q")
        def handle_exit(event):
            """Exit with statistics"""
            self.display_stats()
            event.app.exit()
            sys.exit(0)

        @self.kb.add("c-i")
        def handle_edit(event):
            """Open current prompt in editor"""
            try:
                # Debug output
                self.interface.console.print("\nDebug: Ctrl+I pressed")
                
                # Create a temporary file with current buffer content
                current_text = event.current_buffer.text if event.current_buffer.text else ""
                self.interface.console.print(f"\nDebug: Opening editor with text: {current_text}")
                
                # Use the editor from config
                editor = self.interface.editor
                new_text = editor.open_temp_file(current_text)
                
                # Update buffer with edited text
                if new_text and new_text != current_text:
                    event.current_buffer.text = new_text
                    event.current_buffer.cursor_position = len(new_text)
                    
                self.interface.console.print(f"\nDebug: Editor returned text: {new_text}")
                
            except Exception as e:
                self.interface.console.print(f"\nDebug: Error in handle_edit: {str(e)}")
                import traceback
                self.interface.console.print(f"\nDebug: {traceback.format_exc()}")

        @self.kb.add("escape", "e")
        def handle_edit_last(event):
            """Open last AI response in editor"""
            if self.interface.last_response:
                self.interface.editor.open_temp_file(self.interface.last_response)

        @self.kb.add("escape", "s")
        def handle_sessions(event):
            """Show session picker"""
            recent_sessions = self.interface.history_manager.list_sessions()[:5]
            if recent_sessions:
                self.interface.console.print("\n[bold]Recent sessions:[/bold]")
                for i, session_path in enumerate(recent_sessions, 1):
                    try:
                        # Get character count
                        char_count = len(session_path.read_text())
                        
                        # Parse date from filename (format: chat_session_YYYYMMDD_HHMMSS.md)
                        date_str = session_path.stem.split("_")[2]  # Gets YYYYMMDD
                        date = datetime.strptime(date_str, "%Y%m%d").strftime("%d/%m/%Y")
                        
                        # Format and print session info
                        self.interface.console.print(
                            f"{i}. {date}: {char_count:,} characters"
                        )
                    except Exception as e:
                        self.interface.console.print(
                            f"{i}. Error reading session: {str(e)}"
                        )

        # Add F1 as a universal help key
        @self.kb.add("f1")
        def show_help_f1(event):
            """Show help (F1)"""
            help_file = self.interface.config_dir / "help.md"
            if help_file.exists():
                self.interface.editor.open_file(str(help_file))

    def display_stats(self):
        """Display session statistics"""
        elapsed_time = time.time() - self.interface.start_time

        # Calculate statistics
        ai_chars = sum(
            len(msg["content"])
            for msg in self.interface.history_manager.messages
            if msg["role"] == "assistant"
        )
        user_chars = sum(
            len(msg["content"])
            for msg in self.interface.history_manager.messages
            if msg["role"] == "user"
        )
        total_chars = ai_chars + user_chars

        # Create stats table
        table = Table(show_header=False, expand=True, border_style="bold cyan")
        table.add_column("Metric", style="bold #f5e0dc")
        table.add_column("Value", style="#cba6f7")

        table.add_row("Model", self.interface.ollama_client.model)
        table.add_row("Session Duration", f"{elapsed_time:.2f} seconds")
        table.add_row("AI Characters", str(ai_chars))
        table.add_row("User Characters", str(user_chars))
        table.add_row("Total Characters", str(total_chars))
        table.add_row(
            "AI/User Ratio", f"{(ai_chars/user_chars if user_chars else 0):.2f}"
        )

        self.interface.console.print(
            Panel(
                table,
                title="Session Statistics",
                border_style="bold #89dceb",
                padding=(1, 1),
            ),
            end=""
        )
