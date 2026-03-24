import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from generator.config import OUTPUT_DIR


class ProjectResult(BaseModel):
    trajectories: int = 0
    passed: int = 0
    failed: int = 0
    tokens: int = 0


class BatchStats(BaseModel):
    total_trajectories: int = 0
    total_pass: int = 0
    total_fail: int = 0
    total_tokens: int = 0


class BatchState(BaseModel):
    batch_id: str
    total_projects: int
    reqs_per_project: int
    project_type: str
    completed: dict[str, ProjectResult] = Field(default_factory=dict)
    failed: dict[str, str] = Field(default_factory=dict)
    pending: list[str] = Field(default_factory=list)
    stats: BatchStats = Field(default_factory=BatchStats)
    created_at: str = ""
    updated_at: str = ""

    def mark_completed(self, project_name: str, result: ProjectResult):
        self.completed[project_name] = result
        if project_name in self.pending:
            self.pending.remove(project_name)
        self.stats.total_trajectories += result.trajectories
        self.stats.total_pass += result.passed
        self.stats.total_fail += result.failed
        self.stats.total_tokens += result.tokens
        self.updated_at = datetime.now().isoformat()

    def mark_failed(self, project_name: str, error: str):
        self.failed[project_name] = error
        if project_name in self.pending:
            self.pending.remove(project_name)
        self.updated_at = datetime.now().isoformat()

    def save(self, path: Path | None = None):
        path = path or (OUTPUT_DIR / "batch_state.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.model_dump(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> "BatchState":
        with open(path) as f:
            data = json.load(f)
        return cls.model_validate(data)

    @property
    def progress_str(self) -> str:
        done = len(self.completed)
        fail = len(self.failed)
        total = self.total_projects
        return f"{done} done, {fail} failed, {total - done - fail} pending / {total} total"
