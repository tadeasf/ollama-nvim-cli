# Ollama NeoVim CLI

A CLI tool for chatting with Ollama models using Neovim/LunarVim as the editor.

## Features

- Chat with Ollama models using your favorite editor
- Save and resume chat sessions
- Progress bar with token counting
- Markdown formatting for responses
- Catppuccin-themed interface

## Installation

### Using pip

```bash
pip install ollama-nvim-cli
```

### From source

```bash
git clone https://github.com/tadeasf/ollama-nvim-cli
cd ollama-nvim-cli
rye sync
rye run build-binary
```

## Usage

Basic usage:

```bash
ollama-nvim-cli

# Or with options
ollama-nvim-cli --model mistral
ollama-nvim-cli --session previous_chat.md
ollama-nvim-cli --list
```

Available options:
- `--model, -m`: Specify the Ollama model to use
- `--session, -s`: Continue a previous chat session
- `--list, -l`: List recent chat sessions
- `--help`: Show help message

## Development

### Setup Development Environment

1. Install Rye (if not already installed):
```bash
curl -sSf https://rye-up.com/get | bash
```

2. Clone and setup project:
```bash
git clone https://github.com/yourusername/ollama-nvim-cli
cd ollama-nvim-cli
rye sync
```

### Development Commands

```bash
# Run the CLI in development
rye run onc

# Build binary
rye run build-binary

# Prepare for PyPI release
rye run build-pypi
```

### Project Structure

```
src/ollama_nvim_cli/
├── api/          # API clients
├── lib/          # Core functionality
├── prompt/       # UI and prompt handling
└── cli.py        # CLI entry point
```

## Configuration

Configuration file is automatically created at `~/.config/ollama-nvim-cli/config.yaml`:

```yaml
# API endpoint for Ollama
endpoint: "http://localhost:11434"

# Default model to use
model: "mistral"

# Editor command
editor: "lvim"

# Theme configuration (Catppuccin colors)
theme:
  user_prompt: "#a6e3a1"
  assistant: "#89b4fa"
  error: "#f38ba8"
  info: "#89dceb"
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

GPL-3.0