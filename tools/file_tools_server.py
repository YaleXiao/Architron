import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from tools.file_tools import read_file as _read_file
from tools.file_tools import write_file as _write_file
from tools.code_tools import run_python as _run_python
from tools.dev_tools import (
    grep_search as _grep_search,
    glob_files as _glob_files,
    run_bash as _run_bash,
    edit_file_line as _edit_file_line,
    insert_file_line as _insert_file_line,
    delete_file_lines as _delete_file_lines,
    get_file_info as _get_file_info,
    list_directory as _list_directory,
)

mcp = FastMCP("file-tools")


@mcp.tool()
def read_file(path: str) -> str:
    return _read_file(path)


@mcp.tool()
def write_file(path: str, content: str) -> str:
    return _write_file(path, content)


@mcp.tool()
def run_python(code: str) -> str:
    return _run_python(code)


@mcp.tool()
def grep_search(
    path: str, pattern: str, case_sensitive: bool = True, file_pattern: str = "*"
) -> str:
    return _grep_search(path, pattern, case_sensitive, file_pattern)


@mcp.tool()
def glob_files(pattern: str, path: str = ".") -> str:
    return _glob_files(pattern, path)


@mcp.tool()
def run_bash(command: str, timeout: int = 30) -> str:
    return _run_bash(command, timeout)


@mcp.tool()
def edit_file_line(file_path: str, line_number: int, new_content: str) -> str:
    return _edit_file_line(file_path, line_number, new_content)


@mcp.tool()
def insert_file_line(file_path: str, line_number: int, new_content: str) -> str:
    return _insert_file_line(file_path, line_number, new_content)


@mcp.tool()
def delete_file_lines(file_path: str, start_line: int, end_line: int) -> str:
    return _delete_file_lines(file_path, start_line, end_line)


@mcp.tool()
def get_file_info(file_path: str) -> str:
    return _get_file_info(file_path)


@mcp.tool()
def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    return _list_directory(path, show_hidden)


if __name__ == "__main__":
    mcp.run()
