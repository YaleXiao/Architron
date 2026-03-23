# -*- coding: utf-8 -*-
PROVIDER = "ollama"

SYSTEM_PROMPT = """You are a programming assistant subagent that can skillfully call tools to help users complete various programming tasks.

## Available Tools (11 total)

### File Operations
1. read_file(path) - Read file content
2. write_file(path, content) - Write file content
3. edit_file_line(file_path, line_number, new_content) - Replace a specific line
4. insert_file_line(file_path, line_number, new_content) - Insert a new line
5. delete_file_lines(file_path, start_line, end_line) - Delete line range
6. get_file_info(file_path) - Get file metadata
7. list_directory(path='.', show_hidden=False) - List directory contents

### Code & Search
8. run_python(code) - Execute Python code (10s timeout)
9. grep_search(path, pattern, case_sensitive=True, file_pattern='*') - Search text in files
10. glob_files(pattern, path='.') - Find files by pattern

### System
11. run_bash(command, timeout=30) - Execute shell commands

## Tool Calling Rules (Must Strictly Follow)
- Only call the above 11 tools, do not call any unlisted tool names
- Do not fabricate or guess non-existent tools
- ALWAYS output tool calls in JSON format within a code block like this:
```json
{"name": "tool_name", "arguments": {"param1": "value1", "param2": "value2"}}
```

## Windows Path Handling (Critical!)
- When using absolute paths on Windows in run_python, ALWAYS use raw strings with 'r' prefix or forward slashes
- CORRECT: run_python(r"import os; os.makedirs(r'D:\\\\Program\\\\Architron\\\\docs')")
- CORRECT: run_python("import os; os.makedirs('D:/Program/Architron/docs')")  
- PREFERRED: Use relative paths when possible to avoid path escaping issues
- PREFERRED: run_python("import os; os.makedirs('./docs')")

## Call Examples
Correct: 
```json
{"name": "grep_search", "arguments": {"path": "./src", "pattern": "TODO", "file_pattern": "*.py"}}
```
Correct: 
```json
{"name": "glob_files", "arguments": {"pattern": "**/*.py", "path": "."}}
```
Correct: 
```json
{"name": "edit_file_line", "arguments": {"file_path": "config.py", "line_number": 10, "new_content": "NEW_CONTENT"}}
```
Wrong: create_directory('new_dir')  # This tool does not exist
"""

CONFIG = {
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
            "description": "Read file content. Args: path (str)",
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
            "description": "Write file content. Args: path (str), content (str)",
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
            "description": "Execute Python code with 10 second timeout. Args: code (str)",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Search for text pattern in files. Args: path (str), pattern (str), case_sensitive (bool, default=True), file_pattern (str, default='*')",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Directory path to search",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Text pattern to search for",
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Case sensitive search (default: true)",
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "File pattern to match (e.g., '*.py')",
                    },
                },
                "required": ["path", "pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "glob_files",
            "description": "Find files matching a glob pattern. Args: pattern (str), path (str, default='.')",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., '**/*.py')",
                    },
                    "path": {"type": "string", "description": "Base directory path"},
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash",
            "description": "Execute bash/shell commands. Args: command (str), timeout (int, default=30)",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 30)",
                    },
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file_line",
            "description": "Replace a specific line in a file. Args: file_path (str), line_number (int), new_content (str)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path"},
                    "line_number": {
                        "type": "integer",
                        "description": "Line number to replace (1-indexed)",
                    },
                    "new_content": {
                        "type": "string",
                        "description": "New content for the line",
                    },
                },
                "required": ["file_path", "line_number", "new_content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "insert_file_line",
            "description": "Insert a new line at a specific position. Args: file_path (str), line_number (int), new_content (str)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path"},
                    "line_number": {
                        "type": "integer",
                        "description": "Line number to insert at (1-indexed)",
                    },
                    "new_content": {
                        "type": "string",
                        "description": "Content for the new line",
                    },
                },
                "required": ["file_path", "line_number", "new_content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file_lines",
            "description": "Delete a range of lines from a file. Args: file_path (str), start_line (int), end_line (int)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path"},
                    "start_line": {
                        "type": "integer",
                        "description": "Start line number (1-indexed)",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "End line number (1-indexed)",
                    },
                },
                "required": ["file_path", "start_line", "end_line"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_info",
            "description": "Get detailed information about a file. Args: file_path (str)",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "File path"},
                },
                "required": ["file_path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List directory contents. Args: path (str, default='.'), show_hidden (bool, default=False)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path"},
                    "show_hidden": {
                        "type": "boolean",
                        "description": "Show hidden files",
                    },
                },
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
