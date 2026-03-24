import time
from datetime import datetime, timezone

from generator.models.conversation import Message, ToolCallRecord, ConversationHistory
from generator.models.trajectory import StageRecord


class TrajectoryRecorder:
    def __init__(self):
        self.stages: list[StageRecord] = []
        self.all_messages: list[Message] = []
        self.total_api_calls: int = 0
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self._current_stage: str | None = None
        self._stage_start: float | None = None
        self._stage_messages: list[Message] = []
        self._stage_tool_calls: int = 0
        self._stage_input_tokens: int = 0
        self._stage_output_tokens: int = 0
        self._stage_model: str = ""
        self._stage_number: int = 0

    def start_stage(self, stage_name: str, stage_number: int, model: str):
        if self._current_stage:
            self.end_stage()
        self._current_stage = stage_name
        self._stage_number = stage_number
        self._stage_model = model
        self._stage_start = time.time()
        self._stage_messages = []
        self._stage_tool_calls = 0
        self._stage_input_tokens = 0
        self._stage_output_tokens = 0

    def end_stage(self):
        if not self._current_stage:
            return
        now = datetime.now(timezone.utc).isoformat()
        start_ts = datetime.fromtimestamp(self._stage_start, tz=timezone.utc).isoformat() if self._stage_start else now
        self.stages.append(StageRecord(
            stage_name=self._current_stage,
            stage_number=self._stage_number,
            model_used=self._stage_model,
            messages=list(self._stage_messages),
            tool_calls_count=self._stage_tool_calls,
            input_tokens=self._stage_input_tokens,
            output_tokens=self._stage_output_tokens,
            duration_seconds=time.time() - (self._stage_start or time.time()),
            timestamp_start=start_ts,
            timestamp_end=now,
        ))
        self._current_stage = None

    def record_message(self, role: str, content: str | None, stage: str, model: str | None = None):
        msg = Message(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            model=model,
            stage=stage,
        )
        self._stage_messages.append(msg)
        self.all_messages.append(msg)

    def record_tool_call(self, stage: str, tool_call: ToolCallRecord):
        msg = Message(
            role="assistant_tool_call",
            content=f"[tool_call: {tool_call.name}({tool_call.arguments})]",
            tool_calls=[tool_call],
            timestamp=tool_call.timestamp,
            stage=stage,
        )
        self._stage_messages.append(msg)
        self.all_messages.append(msg)

        result_msg = Message(
            role="tool",
            content=tool_call.result,
            tool_call_id=tool_call.id,
            timestamp=tool_call.timestamp,
            stage=stage,
        )
        self._stage_messages.append(result_msg)
        self.all_messages.append(result_msg)
        self._stage_tool_calls += 1

    def record_api_call(self, stage: str, model: str, input_tokens: int, output_tokens: int):
        self.total_api_calls += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self._stage_input_tokens += input_tokens
        self._stage_output_tokens += output_tokens

    def get_conversation_history(self) -> ConversationHistory:
        total_tool_calls = sum(s.tool_calls_count for s in self.stages)
        total_turns = sum(
            1 for m in self.all_messages if m.role in ("user", "assistant")
        )
        return ConversationHistory(
            messages=self.all_messages,
            total_turns=total_turns,
            total_tool_calls=total_tool_calls,
        )
