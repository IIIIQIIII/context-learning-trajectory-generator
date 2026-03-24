import json
from datetime import datetime, timezone
from pathlib import Path

from generator.llm.client import AsyncOpenRouterClient
from generator.llm.prompts import ANALYZER_SYSTEM, ANALYZER_USER
from generator.models.project import AnchorProject, ProjectAnalysis
from generator.models.requirement import Requirement, RequirementSet
from generator.tools.executor import ToolExecutor


class ProjectAnalyzer:
    def __init__(self, client: AsyncOpenRouterClient, model: str):
        self.client = client
        self.model = model

    async def analyze(self, project: AnchorProject, project_root: Path) -> RequirementSet:
        executor = ToolExecutor(project_root)

        # Read README
        readme_content = "(no README found)"
        for name in ["README.md", "README.rst", "README.txt", "README"]:
            readme_path = project_root / name
            if readme_path.exists():
                readme_content = executor._file_read(name, limit=500)
                break

        # Get file structure
        file_structure = executor._file_tree(max_depth=2)

        # Build analysis
        analysis = ProjectAnalysis(
            project=project,
            readme_content=readme_content[:5000],
            file_structure=file_structure.splitlines()[:100],
            key_files_read=[name for name in ["README.md", "README.rst"] if (project_root / name).exists()],
            analysis_timestamp=datetime.now(timezone.utc).isoformat(),
        )

        # Generate requirements
        user_prompt = ANALYZER_USER.format(
            project_name=project.name,
            repo=project.repo,
            category=project.category,
            project_type=project.project_type.value,
            readme_content=readme_content[:5000],
            file_structure=file_structure[:3000],
        )

        if self.client.recorder:
            self.client.recorder.record_message("system", ANALYZER_SYSTEM, stage="analyzer")
            self.client.recorder.record_message("user", user_prompt, stage="analyzer")

        data = await self.client.chat_completion(
            messages=[
                {"role": "system", "content": ANALYZER_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            model=self.model,
            stage="analyzer",
        )

        response_text = data["choices"][0]["message"]["content"]

        if self.client.recorder:
            self.client.recorder.record_message("assistant", response_text, stage="analyzer", model=self.model)

        # Parse requirements from JSON response
        requirements = self._parse_requirements(response_text)

        return RequirementSet(
            project=project,
            requirements=requirements,
            analysis=analysis,
            generated_at=datetime.now(timezone.utc).isoformat(),
            model_used=self.model,
        )

    def _parse_requirements(self, text: str) -> list[Requirement]:
        # Try to extract JSON from markdown code blocks or raw text
        json_str = text
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0]

        try:
            data = json.loads(json_str.strip())
        except json.JSONDecodeError:
            # Fallback: try to find JSON array
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                return [Requirement(
                    id="req_001",
                    description="Write a basic usage example script for this project",
                    difficulty="easy",
                    script_language="python",
                    expected_output_type="stdout",
                )]

        requirements = []
        for item in data:
            requirements.append(Requirement(
                id=item.get("id", f"req_{len(requirements)+1:03d}"),
                description=item["description"],
                difficulty=item.get("difficulty", "medium"),
                script_language=item.get("script_language", "python"),
                expected_output_type=item.get("expected_output_type", "stdout"),
            ))
        return requirements
