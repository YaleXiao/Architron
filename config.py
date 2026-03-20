# -*- coding: utf-8 -*-
PROVIDER = "ollama"

SYSTEM_PROMPT = """You are a programming assistant subagent that can skillfully call tools to help users complete various programming tasks.

## Available Tools
1. read_file(path): Read file content
2. write_file(path, content): Write file content  
3. run_python(code): Execute Python code with 10 second timeout

## Tool Calling Rules (Must Strictly Follow)
- Only call the above 3 tools, do not call any unlisted tool names
- When calling tools, use exact names: read_file, write_file, run_python
- File system operations (create directory, delete, move, etc.) must use run_python + os module
- Do not fabricate or guess non-existent tools

## Call Examples
Correct: run_python("import os; os.makedirs('new_dir')")
Wrong: create_directory('new_dir')  # This tool does not exist

Reply in Chinese.
"""

CONFIG = {
    "anthropic": {
        "api_key": "your-key",
        "model": "claude-opus-4-5",
        "max_tokens": 4096,
    },
    "openai": {"api_key": "your-key", "model": "gpt-4o-mini", "max_tokens": 4096},
    "ollama": {
        "base_url": "http://localhost:11434",
        "model": "qwen2.5-coder:7b",
        "max_tokens": 4096,
    },
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file content",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "File path"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write file content",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "File content"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Execute Python code with 10 second timeout",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"],
            },
        },
    },
]

RAG_DIRECTORIES = [
    "src/",
    "docs/",
    "knowledge/",
]

RAG_EXTENSIONS = [".py", ".md", ".txt"]

RAG_EXCLUDE = [".venv", "chroma_db", "__pycache__", ".git"]

RAG_FORCE_REINDEX = False

MCP_SERVERS = [
    {
        "name": "file-tools",
        "command": "python",
        "args": ["-m", "tools.file_tools_server"],
    }
]
