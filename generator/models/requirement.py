from enum import Enum
from pydantic import BaseModel

from .project import AnchorProject, ProjectAnalysis


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ScriptLanguage(str, Enum):
    PYTHON = "python"
    BASH = "bash"


class Requirement(BaseModel):
    id: str
    description: str
    difficulty: Difficulty
    script_language: ScriptLanguage
    expected_output_type: str


class RequirementSet(BaseModel):
    project: AnchorProject
    requirements: list[Requirement]
    analysis: ProjectAnalysis
    generated_at: str
    model_used: str
