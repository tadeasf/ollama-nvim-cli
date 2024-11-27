from pathlib import Path
from datetime import datetime
from typing import List, Optional
import yaml
from prompt_toolkit.history import FileHistory
from rich.table import Table


class HistoryManager:
    def __init__(self, config):
        history_dir = Path(config.get("history", {}).get("save_dir", "~/.local/share/ollama-nvim-cli/history")).expanduser()
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.current_session: Optional[str] = None
        self.prompt_history = FileHistory(str(history_dir / ".prompt_history"))
        self.messages: List[dict] = []

    def create_session(self) -> str:
        """Create a new session file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_file = self.history_dir / f"chat_session_{timestamp}.md"
        self.current_session = str(session_file)

        # Initialize session file with metadata
        with open(session_file, "w", encoding="utf-8") as f:
            f.write("---\n")
            yaml.dump(
                {
                    "created_at": datetime.now().isoformat(),
                    "model": "mistral",  # This should come from config
                    "messages": [],
                },
                f,
            )
            f.write("---\n\n")

        return self.current_session

    def load_session(self, session_path: str) -> List[dict]:
        """Load an existing session"""
        self.current_session = session_path
        self.messages = []

        with open(session_path, "r", encoding="utf-8") as f:
            content = f.read()
            if content.startswith("---"):
                _, front_matter, *parts = content.split("---", 2)
                session_data = yaml.safe_load(front_matter)
                self.messages = session_data.get("messages", [])

        return self.messages

    def add_message(self, role: str, content: str):
        """Add a message to the current session"""
        if not self.current_session:
            self.create_session()

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        self.messages.append(message)

        # Update YAML front matter
        with open(self.current_session, "r+", encoding="utf-8") as f:
            content = f.read()
            _, front_matter, *parts = content.split("---", 2)
            session_data = yaml.safe_load(front_matter)
            session_data["messages"].append(message)

            # Rewrite the file
            f.seek(0)
            f.write("---\n")
            yaml.dump(session_data, f)
            f.write("---\n\n")

            # Append the message in markdown format
            f.write(f"\n### {role.title()}\n")
            f.write(f"{content}\n")
            f.write("\n---\n")

    def list_sessions(self) -> List[Path]:
        """List all available sessions"""
        sessions = sorted(
            self.history_dir.glob("chat_session_*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return sessions[:5]  # Return only the 5 most recent sessions

    def format_sessions(self) -> None:
        """Format and display recent sessions"""
        sessions = self.list_sessions()
        if not sessions:
            return

        table = Table(title="Recent Sessions", show_header=True, border_style="cyan")
        table.add_column("№", style="cyan", justify="right")
        table.add_column("Date", style="green")
        table.add_column("Size", style="yellow")

        for i, session_path in enumerate(sessions, 1):
            # Parse date from filename (format: chat_session_YYYYMMDD_HHMMSS.md)
            date_str = session_path.stem.split("_")[2]  # Gets YYYYMMDD
            date = datetime.strptime(date_str, "%Y%m%d").strftime("%d/%m/%Y")
            
            # Get character count
            try:
                char_count = len(session_path.read_text())
                size_str = f"{char_count:,} characters"
            except Exception:
                size_str = "N/A"

            table.add_row(str(i), date, size_str)

        return table
