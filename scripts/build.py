import PyInstaller.__main__
from pathlib import Path


def build_binary():
    # Get the project root directory
    root_dir = Path(__file__).parent.parent
    entry_point = root_dir / "src" / "ollama_nvim_cli" / "cli.py"

    # Ensure the entry point exists
    if not entry_point.exists():
        raise FileNotFoundError(f"Entry point not found: {entry_point}")

    PyInstaller.__main__.run(
        [
            "--name=ollama-nvim-cli",
            "--onefile",
            "--add-data=src/ollama_nvim_cli:ollama_nvim_cli",
            "--hidden-import=typer",
            "--hidden-import=rich",
            "--hidden-import=prompt_toolkit",
            "--hidden-import=httpx",
            str(entry_point),
        ]
    )


if __name__ == "__main__":
    build_binary()
