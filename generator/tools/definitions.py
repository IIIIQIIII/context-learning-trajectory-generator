TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "file_tree",
            "description": "Show project directory tree structure. Use to get an overview of the project layout.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Root path for tree (relative to project root)",
                        "default": ".",
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth to display",
                        "default": 3,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_list",
            "description": "List files and directories at a path. Returns names with type indicators (dir/, file).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path within the project directory",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If true, list recursively (max depth 3)",
                        "default": False,
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "file_read",
            "description": "Read a file's contents. Returns line-numbered text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Start line (1-based)",
                        "default": 1,
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max lines to read",
                        "default": 200,
                    },
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search for a regex pattern in project files. Returns matching lines with file paths and line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search in (relative to project root)",
                        "default": ".",
                    },
                    "file_glob": {
                        "type": "string",
                        "description": "Glob pattern to filter files (e.g., '*.py')",
                        "default": "*",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a shell command in the project directory. Use for running scripts, installing deps, checking versions, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default 30)",
                        "default": 30,
                    },
                },
                "required": ["command"],
            },
        },
    },
]
