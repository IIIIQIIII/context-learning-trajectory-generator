from pydantic import BaseModel


class ToolCallRecord(BaseModel):
    id: str
    name: str
    arguments: dict
    result: str
    timestamp: str
    duration_ms: int


class Message(BaseModel):
    role: str
    content: str | None = None
    tool_calls: list[ToolCallRecord] | None = None
    tool_call_id: str | None = None
    timestamp: str
    model: str | None = None
    stage: str


class ConversationHistory(BaseModel):
    messages: list[Message]
    total_turns: int
    total_tool_calls: int
