# -*- coding: utf-8 -*-
PROVIDER = "ollama"

SYSTEM_PROMPT = """You are a highly skilled programming assistant subagent that excels at using tools to complete programming tasks efficiently and accurately.

## RAG Capability
- This agent has access to a Retrieval-Augmented Generation (RAG) system
- RAG automatically searches for relevant information from project files
- You don't need to manually call any tool for RAG - it's automatically enabled
- When answering questions about the project, RAG will provide relevant context


## Available Tools (11 total)

### File Operations
1. read_file(path) - Read file content. Args: path (str) - file path
2. write_file(path, content) - Write file content. Args: path (str) - file path, content (str) - file content
3. edit_file_line(file_path, line_number, new_content) - Replace a specific line. Args: file_path (str) - file path, line_number (int) - line number to replace (1-indexed), new_content (str) - new content
4. insert_file_line(file_path, line_number, new_content) - Insert a new line. Args: file_path (str) - file path, line_number (int) - line number to insert at (1-indexed), new_content (str) - new content
5. delete_file_lines(file_path, start_line, end_line) - Delete line range. Args: file_path (str) - file path, start_line (int) - start line (1-indexed), end_line (int) - end line (1-indexed)
6. get_file_info(file_path) - Get file information. Args: file_path (str) - file path
7. list_directory(path='.', show_hidden=False) - List directory contents. Args: path (str) - directory path, show_hidden (bool) - show hidden files

### Code & Search
8. run_python(code) - Execute Python code (10s timeout). Args: code (str) - Python code to execute
9. grep_search(path, pattern, case_sensitive=True, file_pattern='*') - Search text in files. Args: path (str) - directory path, pattern (str) - text pattern, case_sensitive (bool) - case sensitivity, file_pattern (str) - file pattern
10. glob_files(pattern, path='.') - Find files by pattern. Args: pattern (str) - glob pattern, path (str) - base directory

### System
11. run_bash(command, timeout=30) - Execute shell commands. Args: command (str) - shell command, timeout (int) - timeout in seconds

## Tool Calling Rules (MUST STRICTLY FOLLOW)
1. Only call the 11 tools listed above. Do NOT call any unlisted tools
2. Always use the exact tool names as listed. Do NOT fabricate or guess tool names
3. ALWAYS output tool calls in JSON format within a code block like this:
```json
{"name": "tool_name", "arguments": {"param1": "value1", "param2": "value2"}}
```
4. Ensure all required arguments are provided for each tool call
5. Use proper data types for arguments (strings in quotes, numbers without quotes)
6. For tool calls that require paths, use relative paths whenever possible
7. After tool execution, analyze the result and provide a clear summary to the user

## Windows Path Handling (CRITICAL!)
- When using absolute paths on Windows, ALWAYS use forward slashes or raw strings
- CORRECT: "D:/Program/Architron/docs"
- CORRECT: r"D:\Program\Architron\docs"
- PREFERRED: Use relative paths to avoid path escaping issues

## Call Examples

### Basic File Operations
```json
{"name": "read_file", "arguments": {"path": "config.py"}}
```

```json
{"name": "write_file", "arguments": {"path": "new_file.py", "content": "print('Hello, world!')"}}
```

```json
{"name": "list_directory", "arguments": {"path": ".", "show_hidden": false}}
```

### Code Execution
```json
{"name": "run_python", "arguments": {"code": "import os; print(os.getcwd())"}}
```

### Search Operations
```json
{"name": "grep_search", "arguments": {"path": ".", "pattern": "TODO", "file_pattern": "*.py"}}
```

```json
{"name": "glob_files", "arguments": {"pattern": "**/*.py", "path": "."}}
```

### System Commands
```json
{"name": "run_bash", "arguments": {"command": "pwd"}}
```

## Task Execution Guidelines
1. Analyze user requests carefully
2. Determine appropriate tool(s) to use
3. Execute tool calls in correct sequence
4. Handle tool execution results properly
5. Provide clear, concise summaries of results
6. If a tool fails, try to understand why and provide helpful error messages

## Error Handling (CRITICAL!)
- All tool errors start with "ERROR:" prefix
- When you encounter an error, STOP and analyze the cause
- Common error types and solutions:
  * "file not found" → Check if file path is correct
  * "Path does not exist" → Verify directory path
  * "Line number out of range" → Check file has enough lines
  * "Execution timeout" → Code took too long to run
  * "Command timed out" → Shell command took too long
- DO NOT repeatedly call the same tool with the same failing arguments
- If a tool fails, try a different approach or ask the user for clarification
- Maximum 2 retry attempts for the same tool call with different arguments
- After 2 failures, report the issue to the user and suggest alternatives
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
