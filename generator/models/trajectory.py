from pydantic import BaseModel

from .project import AnchorProject
from .requirement import Requirement
from .conversation import Message, ConversationHistory


class StageRecord(BaseModel):
    stage_name: str
    stage_number: int
    model_used: str
    messages: list[Message]
    tool_calls_count: int
    input_tokens: int
    output_tokens: int
    duration_seconds: float
    timestamp_start: str
    timestamp_end: str


class TrajectoryRecord(BaseModel):
    trajectory_id: str
    project: AnchorProject
    requirement: Requirement
    stages: list[StageRecord]
    full_conversation: ConversationHistory
    generated_script: str | None
    review_verdict: str
    review_reasoning: str
    user_verification: str
    user_verification_reasoning: str
    final_quality: str
    total_api_calls: int
    total_tokens: int
    total_duration_seconds: float
    generated_at: str
