import asyncio
import fnmatch
import os
import re
from pathlib import Path

from generator.config import TOOL_OUTPUT_MAX_CHARS


class ToolExecutor:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()

    def _resolve_safe_path(self, relative_path: str) -> Path:
        resolved = (self.project_root / relative_path).resolve()
        if not str(resolved).startswith(str(self.project_root)):
            raise ValueError(f"Path escape attempt: {relative_path}")
        return resolved

    def _truncate(self, text: str, max_chars: int = TOOL_OUTPUT_MAX_CHARS) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + f"\n\n[... truncated, {len(text) - max_chars} more chars ...]"

    async def execute(self, tool_name: str, arguments: dict) -> str:
        try:
            handlers = {
                "file_tree": self._file_tree,
                "file_list": self._file_list,
                "file_read": self._file_read,
                "grep": self._grep,
                "bash": self._bash,
            }
            handler = handlers.get(tool_name)
            if not handler:
                return f"Error: Unknown tool '{tool_name}'"

            if asyncio.iscoroutinefunction(handler):
                result = await handler(**arguments)
            else:
                result = handler(**arguments)
            return self._truncate(result)
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"

    def _file_tree(self, path: str = ".", max_depth: int = 3) -> str:
        root = self._resolve_safe_path(path)
        if not root.is_dir():
            return f"Error: '{path}' is not a directory"

        lines = []
        self._build_tree(root, "", max_depth, 0, lines)
        if not lines:
            return "(empty directory)"
        return "\n".join(lines[:300])

    def _build_tree(self, dir_path: Path, prefix: str, max_depth: int, depth: int, lines: list):
        if depth >= max_depth or len(lines) >= 300:
            return

        try:
            entries = sorted(dir_path.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return

        # Filter hidden and common noise
        entries = [e for e in entries if not e.name.startswith(".") and e.name not in {
            "node_modules", "__pycache__", ".git", "venv", ".venv", "dist", "build",
        }]

        for i, entry in enumerate(entries):
            if len(lines) >= 300:
                return
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"{prefix}{connector}{entry.name}{suffix}")
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                self._build_tree(entry, prefix + extension, max_depth, depth + 1, lines)

    def _file_list(self, path: str, recursive: bool = False) -> str:
        target = self._resolve_safe_path(path)
        if not target.is_dir():
            return f"Error: '{path}' is not a directory"

        entries = []
        if recursive:
            for root, dirs, files in os.walk(target):
                # Filter noise
                dirs[:] = [d for d in dirs if d not in {
                    "node_modules", "__pycache__", ".git", "venv", ".venv",
                }]
                depth = str(Path(root)).count(os.sep) - str(target).count(os.sep)
                if depth > 3:
                    continue
                for d in sorted(dirs):
                    rel = os.path.relpath(os.path.join(root, d), target)
                    entries.append(f"{rel}/")
                for f in sorted(files):
                    rel = os.path.relpath(os.path.join(root, f), target)
                    entries.append(rel)
                if len(entries) >= 500:
                    break
        else:
            for entry in sorted(target.iterdir(), key=lambda e: e.name.lower()):
                if entry.name.startswith("."):
                    continue
                suffix = "/" if entry.is_dir() else ""
                entries.append(f"{entry.name}{suffix}")

        if not entries:
            return "(empty directory)"
        result = "\n".join(entries[:500])
        if len(entries) > 500:
            result += f"\n\n[... {len(entries) - 500} more entries ...]"
        return result

    def _file_read(self, path: str, offset: int = 1, limit: int = 200) -> str:
        target = self._resolve_safe_path(path)
        if not target.is_file():
            return f"Error: '{path}' is not a file"

        try:
            content = target.read_text(errors="replace")
        except Exception as e:
            return f"Error reading file: {e}"

        lines = content.splitlines()
        total = len(lines)
        start = max(0, offset - 1)
        end = min(total, start + limit)
        selected = lines[start:end]

        numbered = [f"{i + start + 1:4d} | {line}" for i, line in enumerate(selected)]
        result = "\n".join(numbered)
        if end < total:
            result += f"\n\n[... {total - end} more lines, total {total} lines ...]"
        return result

    def _grep(self, pattern: str, path: str = ".", file_glob: str = "*") -> str:
        target = self._resolve_safe_path(path)
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            return f"Error: Invalid regex '{pattern}': {e}"

        matches = []
        if target.is_file():
            self._grep_file(target, regex, matches)
        elif target.is_dir():
            for root, dirs, files in os.walk(target):
                dirs[:] = [d for d in dirs if d not in {
                    "node_modules", "__pycache__", ".git", "venv", ".venv",
                }]
                for fname in files:
                    if file_glob != "*" and not fnmatch.fnmatch(fname, file_glob):
                        continue
                    fpath = Path(root) / fname
                    self._grep_file(fpath, regex, matches)
                    if len(matches) >= 50:
                        break
                if len(matches) >= 50:
                    break

        if not matches:
            return f"No matches found for pattern '{pattern}'"
        result = "\n".join(matches[:50])
        if len(matches) > 50:
            result += f"\n\n[... truncated, showing first 50 of {len(matches)} matches ...]"
        return result

    def _grep_file(self, fpath: Path, regex: re.Pattern, matches: list):
        try:
            text = fpath.read_text(errors="replace")
        except Exception:
            return
        rel = os.path.relpath(fpath, self.project_root)
        for i, line in enumerate(text.splitlines(), 1):
            if regex.search(line):
                matches.append(f"{rel}:{i}: {line.rstrip()}")
                if len(matches) >= 50:
                    return

    async def _bash(self, command: str, timeout: int = 30) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.project_root),
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )
            output = ""
            if stdout:
                output += stdout.decode(errors="replace")
            if stderr:
                output += "\n[stderr]\n" + stderr.decode(errors="replace")
            if proc.returncode != 0:
                output += f"\n[exit code: {proc.returncode}]"
            return output.strip() or "(no output)"
        except asyncio.TimeoutError:
            proc.kill()
            return f"Error: Command timed out after {timeout}s"
