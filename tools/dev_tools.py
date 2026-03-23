import os
import re
from pathlib import Path


def grep_search(
    path: str, pattern: str, case_sensitive: bool = True, file_pattern: str = "*"
) -> str:
    """Search for text pattern in files within a directory."""
    try:
        results = []
        search_path = Path(path) if os.path.isabs(path) else Path(".") / path
        if not search_path.exists():
            return f"Error: Path '{path}' does not exist"

        if not case_sensitive:
            pattern = pattern.lower()

        for root, dirs, files in os.walk(search_path):
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["__pycache__", "node_modules", ".venv"]
            ]

            for file in files:
                if not re.match(file_pattern.replace("*", ".*"), file):
                    continue

                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            search_line = line if case_sensitive else line.lower()
                            if pattern in search_line:
                                preview = line.strip()[:100]
                                results.append(f"{file_path}:{line_num}: {preview}")
                except Exception:
                    pass

        if not results:
            return f"No matches found for '{pattern}' in {path}"

        return f"Found {len(results)} matches:\n\n" + "\n".join(results[:50])
    except Exception as e:
        return f"Error during search: {str(e)}"


def glob_files(pattern: str, path: str = ".") -> str:
    """Find files matching a glob pattern."""
    try:
        search_path = Path(path)
        if not search_path.exists():
            return f"Error: Path '{path}' does not exist"

        results = list(search_path.rglob(pattern))
        if not results:
            return f"No files found matching pattern '{pattern}'"

        return f"Found {len(results)} files:\n\n" + "\n".join(
            [str(p) for p in results[:100]]
        )
    except Exception as e:
        return f"Error during glob: {str(e)}"


def run_bash(command: str, timeout: int = 30) -> str:
    """Execute bash/shell commands."""
    import subprocess

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = []
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        if result.returncode != 0:
            output.append(f"Exit code: {result.returncode}")

        return (
            "\n\n".join(output)
            if output
            else "Command executed successfully (no output)"
        )
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {str(e)}"


def edit_file_line(file_path: str, line_number: int, new_content: str) -> str:
    """Replace a specific line in a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if line_number < 1 or line_number > len(lines):
            return f"Error: Line number {line_number} out of range (file has {len(lines)} lines)"

        lines[line_number - 1] = new_content + "\n"

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return f"Successfully replaced line {line_number}"
    except Exception as e:
        return f"Error editing file: {str(e)}"


def insert_file_line(file_path: str, line_number: int, new_content: str) -> str:
    """Insert a new line at a specific position in a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if line_number < 1 or line_number > len(lines) + 1:
            return f"Error: Line number {line_number} out of range (file has {len(lines)} lines)"

        lines.insert(line_number - 1, new_content + "\n")

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return f"Successfully inserted line at position {line_number}"
    except Exception as e:
        return f"Error inserting line: {str(e)}"


def delete_file_lines(file_path: str, start_line: int, end_line: int) -> str:
    """Delete a range of lines from a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if start_line < 1 or end_line > len(lines):
            return f"Error: Line range ({start_line}-{end_line}) out of range (file has {len(lines)} lines)"

        del lines[start_line - 1 : end_line]

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return f"Successfully deleted lines {start_line}-{end_line}"
    except Exception as e:
        return f"Error deleting lines: {str(e)}"


def get_file_info(file_path: str) -> str:
    """Get detailed information about a file."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' does not exist"

        stat = path.stat()
        info = [
            f"Path: {path.absolute()}",
            f"Size: {stat.st_size} bytes",
            f"Modified: {stat.st_mtime}",
            f"Lines: {len(open(path, 'r', encoding='utf-8', errors='ignore').readlines())}",
        ]

        return "\n".join(info)
    except Exception as e:
        return f"Error getting file info: {str(e)}"


def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    """List directory contents."""
    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return f"Error: Directory '{path}' does not exist"
        if not dir_path.is_dir():
            return f"Error: '{path}' is not a directory"

        items = []
        for item in sorted(dir_path.iterdir()):
            if not show_hidden and item.name.startswith("."):
                continue

            prefix = "d" if item.is_dir() else "f"
            size = item.stat().st_size if item.is_file() else "-"
            items.append(f"{prefix} {item.name} ({size} bytes)")

        return f"Contents of '{path}':\n\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing directory: {str(e)}"
