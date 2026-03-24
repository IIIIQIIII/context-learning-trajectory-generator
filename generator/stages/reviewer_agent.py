import json
from pathlib import Path

from generator.llm.client import AsyncOpenRouterClient
from generator.llm.prompts import REVIEWER_SYSTEM, REVIEWER_USER
from generator.models.project import AnchorProject
from generator.models.requirement import Requirement
from generator.models.review import ReviewVerdict
from generator.tools.executor import ToolExecutor
from generator.tools.registry import ToolRegistry


class ReviewerAgent:
    def __init__(self, client: AsyncOpenRouterClient, model: str):
        self.client = client
        self.model = model
        self.registry = ToolRegistry()

    async def review(
        self,
        script: str,
        requirement: Requirement,
        project: AnchorProject,
        project_root: Path,
    ) -> ReviewVerdict:
        executor = ToolExecutor(project_root)

        system_prompt = REVIEWER_SYSTEM.format(
            project_name=project.name,
            repo=project.repo,
        )

        user_prompt = REVIEWER_USER.format(
            requirement_description=requirement.description,
            script_language=requirement.script_language,
            script_content=script,
        )

        if self.client.recorder:
            self.client.recorder.record_message("system", system_prompt, stage="reviewer")
            self.client.recorder.record_message("user", user_prompt, stage="reviewer")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        messages, final_text = await self.client.tool_calling_loop(
            messages=messages,
            model=self.model,
            tools=self.registry.get_openai_tools(),
            tool_executor=executor,
            stage="reviewer",
        )

        if self.client.recorder:
            self.client.recorder.record_message("assistant", final_text, stage="reviewer", model=self.model)

        return self._parse_review(final_text)

    def _parse_review(self, text: str) -> ReviewVerdict:
        json_str = text
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0]

        try:
            data = json.loads(json_str.strip())
            return ReviewVerdict(
                verdict=data.get("verdict", "FAIL"),
                reasoning=data.get("reasoning", ""),
                issues_found=data.get("issues_found", []),
                corrections=data.get("corrections", []),
                api_checks=data.get("api_checks", []),
            )
        except (json.JSONDecodeError, KeyError):
            return ReviewVerdict(
                verdict="FAIL",
                reasoning=f"Failed to parse review response: {text[:500]}",
                issues_found=["Could not parse reviewer output"],
                corrections=[],
                api_checks=[],
            )
