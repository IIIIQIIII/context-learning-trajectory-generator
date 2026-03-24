import re
from pathlib import Path

from generator.llm.client import AsyncOpenRouterClient
from generator.llm.prompts import CODER_SYSTEM, FIXER_SYSTEM, FIXER_USER
import json

from generator.models.project import AnchorProject
from generator.models.requirement import Requirement
from generator.models.review import ReviewVerdict
from generator.tools.executor import ToolExecutor
from generator.tools.registry import ToolRegistry


class CoderAgent:
    def __init__(self, client: AsyncOpenRouterClient, model: str):
        self.client = client
        self.model = model
        self.registry = ToolRegistry()

    async def respond(
        self,
        user_message: str,
        conversation_history: list[dict],
        project: AnchorProject,
        project_root: Path,
    ) -> tuple[str, str | None]:
        executor = ToolExecutor(project_root)

        system_prompt = CODER_SYSTEM.format(
            project_name=project.name,
            repo=project.repo,
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})

        if self.client.recorder:
            if not conversation_history:
                self.client.recorder.record_message("system", system_prompt, stage="coder")
            self.client.recorder.record_message("user", user_message, stage="coder")

        messages, final_text = await self.client.tool_calling_loop(
            messages=messages,
            model=self.model,
            tools=self.registry.get_openai_tools(),
            tool_executor=executor,
            stage="coder",
        )

        if self.client.recorder:
            self.client.recorder.record_message("assistant", final_text, stage="coder", model=self.model)

        script = self._extract_script(final_text)
        return final_text, script

    async def fix(
        self,
        script: str,
        requirement: Requirement,
        review: ReviewVerdict,
        project: AnchorProject,
        project_root: Path,
    ) -> tuple[str, str | None]:
        executor = ToolExecutor(project_root)

        system_prompt = FIXER_SYSTEM.format(
            project_name=project.name,
            repo=project.repo,
        )

        user_prompt = FIXER_USER.format(
            requirement_description=requirement.description,
            script_language=requirement.script_language,
            script_content=script,
            review_verdict=review.verdict,
            review_reasoning=review.reasoning,
            review_issues=json.dumps(review.issues_found, ensure_ascii=False),
            review_corrections=json.dumps(review.corrections, ensure_ascii=False),
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if self.client.recorder:
            self.client.recorder.record_message("system", system_prompt, stage="fixer")
            self.client.recorder.record_message("user", user_prompt, stage="fixer")

        messages, final_text = await self.client.tool_calling_loop(
            messages=messages,
            model=self.model,
            tools=self.registry.get_openai_tools(),
            tool_executor=executor,
            stage="fixer",
        )

        if self.client.recorder:
            self.client.recorder.record_message("assistant", final_text, stage="fixer", model=self.model)

        fixed_script = self._extract_script(final_text)
        return final_text, fixed_script

    def _extract_script(self, text: str) -> str | None:
        # Try to find fenced code blocks: ```python or ```bash
        patterns = [
            r'```python\n(.*?)```',
            r'```bash\n(.*?)```',
            r'```sh\n(.*?)```',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
        return None
