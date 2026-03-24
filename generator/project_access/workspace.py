import shutil
from pathlib import Path

from generator.config import WORKSPACE_DIR


def get_project_dir(repo: str, workspace: Path = WORKSPACE_DIR) -> Path | None:
    project_dir = workspace / repo.replace("/", "__")
    if project_dir.exists():
        return project_dir
    return None


def cleanup_project(repo: str, workspace: Path = WORKSPACE_DIR):
    project_dir = workspace / repo.replace("/", "__")
    if project_dir.exists():
        shutil.rmtree(project_dir)


def cleanup_all(workspace: Path = WORKSPACE_DIR):
    if workspace.exists():
        shutil.rmtree(workspace)
        workspace.mkdir(parents=True, exist_ok=True)
