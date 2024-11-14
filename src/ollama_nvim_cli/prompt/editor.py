import tempfile
import subprocess
from pathlib import Path


class Editor:
    def __init__(self, editor_cmd: str = "lvim"):
        self.editor_cmd = editor_cmd

    def open_temp_file(self, initial_content: str = "") -> str:
        with tempfile.NamedTemporaryFile(suffix=".md", mode="w+", delete=False) as tf:
            tf.write(initial_content)
            temp_path = tf.name

        try:
            subprocess.run([self.editor_cmd, temp_path], check=True)
            with open(temp_path, "r") as f:
                content = f.read()
            return content
        finally:
            Path(temp_path).unlink()

    def open_file(self, file_path: str):
        subprocess.run([self.editor_cmd, file_path], check=True)
