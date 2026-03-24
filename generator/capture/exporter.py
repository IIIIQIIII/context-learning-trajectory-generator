import json
from pathlib import Path

from generator.models.trajectory import TrajectoryRecord


def export_jsonl(records: list[TrajectoryRecord], output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        for record in records:
            f.write(record.model_dump_json() + "\n")


def export_sharegpt(records: list[TrajectoryRecord], output_path: Path, quality_filter: bool = True):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    conversations = []

    for record in records:
        if quality_filter and record.final_quality != "PASS":
            continue

        conv = {"conversations": [], "metadata": {
            "project": record.project.name,
            "repo": record.project.repo,
            "requirement_id": record.requirement.id,
            "difficulty": record.requirement.difficulty,
            "final_quality": record.final_quality,
            "trajectory_id": record.trajectory_id,
        }}

        for msg in record.full_conversation.messages:
            if msg.role == "system":
                conv["conversations"].append({"from": "system", "value": msg.content or ""})
            elif msg.role == "user":
                conv["conversations"].append({"from": "human", "value": msg.content or ""})
            elif msg.role == "assistant":
                conv["conversations"].append({"from": "gpt", "value": msg.content or ""})
            elif msg.role == "assistant_tool_call" and msg.tool_calls:
                tc = msg.tool_calls[0]
                tool_repr = json.dumps({"name": tc.name, "arguments": tc.arguments}, ensure_ascii=False)
                conv["conversations"].append({"from": "gpt", "value": f"<tool_call>{tool_repr}</tool_call>"})
            elif msg.role == "tool":
                conv["conversations"].append({"from": "tool", "value": msg.content or ""})

        if conv["conversations"]:
            conversations.append(conv)

    with open(output_path, "w") as f:
        json.dump(conversations, f, ensure_ascii=False, indent=2)


def load_trajectories(input_path: Path) -> list[TrajectoryRecord]:
    records = []
    if input_path.is_file():
        with open(input_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(TrajectoryRecord.model_validate_json(line))
    elif input_path.is_dir():
        for fp in sorted(input_path.glob("*.jsonl")):
            with open(fp) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        records.append(TrajectoryRecord.model_validate_json(line))
    return records
