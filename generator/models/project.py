from enum import Enum
from pydantic import BaseModel


class ProjectType(str, Enum):
    CLI_TOOL = "cli_tool"
    PYTHON_PACKAGE = "python_package"
    JS_TS_PACKAGE = "js_ts_package"


class AnchorProject(BaseModel):
    name: str
    repo: str
    category: str
    language: str | None = None
    project_type: ProjectType


class ProjectAnalysis(BaseModel):
    project: AnchorProject
    readme_content: str
    file_structure: list[str]
    key_files_read: list[str]
    analysis_timestamp: str
