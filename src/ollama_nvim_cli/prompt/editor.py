import tempfile
import os
from shutil import which
import subprocess


class Editor:
    def __init__(self, editor_cmd: str = "lvim"):
        """Initialize editor with command"""
        self.editor_cmd = editor_cmd
        self._validate_editor()

    def _validate_editor(self):
        """Validate that editor exists in PATH"""
        editor_path = which(self.editor_cmd)
        if not editor_path:
            raise FileNotFoundError(f"Editor '{self.editor_cmd}' not found in PATH")
        self.editor_path = editor_path

    def open_temp_file(self, initial_content: str = "") -> str:
        """Open a temporary file in the editor and return its contents"""
        temp_path = None
        try:
            # Create a temporary file with .md extension
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tf:
                tf.write(initial_content)
                temp_path = tf.name

            # Use os.system to run the editor
            exit_code = os.system(f"{self.editor_path} {temp_path}")
            
            if exit_code == 0 and os.path.exists(temp_path):
                with open(temp_path, 'r') as f:
                    return f.read().strip()
            return initial_content

        except Exception as e:
            print(f"Error in open_temp_file: {str(e)}")
            return initial_content
        finally:
            # Clean up the temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass

    def open_file(self, file_path: str):
        """Open a file in the editor"""
        try:
            editor_path = self.editor_cmd
            if not os.path.isfile(editor_path):
                from shutil import which
                editor_path = which(self.editor_cmd)
                if not editor_path:
                    raise FileNotFoundError(f"Editor '{self.editor_cmd}' not found")

            subprocess.run([editor_path, file_path], check=True)
        except Exception as e:
            print(f"Error opening file in editor: {str(e)}")
