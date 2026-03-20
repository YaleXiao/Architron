import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from tools.file_tools import read_file as _read_file
from tools.file_tools import write_file as _write_file
from tools.code_tools import run_python as _run_python

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


if __name__ == "__main__":
    mcp.run()
