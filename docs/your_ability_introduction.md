# Your Ability Introduction

## Overview
This document provides an overview of the capabilities and features offered by your base model。

## Key Features
- **Task Execution**: Utilize pre-programmed tools to execute specific tasks efficiently.
- **Code Operations**: Execute, search, and edit code with ease.
- **File Management**: Handle file operations such as reading, writing, editing, and deleting lines within files.
- **System Interaction**: Run system commands directly from the prompt.

## Base Model Abilities
### File Operations
- `read_file(path)`: Read content of a specified file.
- `write_file(path, content)`: Write text content to a specified file.
- `edit_file_line(file_path, line_number, new_content)`: Replace a specific line in a file.
- `insert_file_line(file_path, line_number, new_content)`: Insert a new line at a specific position in a file.
- `delete_file_lines(file_path, start_line, end_line)`: Delete lines within a specified range in a file.
- `get_file_info(file_path)`: Get information about the file attributes like size and modification time.

### Code & Search Operations
- `run_python(code)`: Execute Python code with a 10-second timeout.
- `grep_search(path, pattern, case_sensitive=True, file_pattern='*')`: Search text in files based on specific patterns.
- `glob_files(pattern, path='.')`: Find files matching a given glob pattern.

### System Operations
- `run_bash(command, timeout=30)`: Execute shell commands with a 30-second timeout.

## How to Use
1. Determine the task required from your data points or instructions.
2. Select and utilize relevant tools based on the requirements.
3. Handle each tool call using proper JSON format inputs as outlined in this document.