import asyncio
from pathlib import Path

from generator.config import WORKSPACE_DIR


async def clone_project(repo: str, workspace: Path = WORKSPACE_DIR) -> Path:
    workspace.mkdir(parents=True, exist_ok=True)
    project_dir = workspace / repo.replace("/", "__")

    if project_dir.exists():
        return project_dir

    proc = await asyncio.create_subprocess_exec(
        "git", "clone", "--depth", "1",
        f"https://github.com/{repo}.git",
        str(project_dir),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

    if proc.returncode != 0:
        err = stderr.decode(errors="replace")
        raise RuntimeError(f"Failed to clone {repo}: {err}")

    return project_dir
