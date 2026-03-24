import json

from generator.llm.client import AsyncOpenRouterClient
from generator.llm.prompts import (
    USER_INITIATE_SYSTEM,
    USER_INITIATE,
    USER_FOLLOWUP_SYSTEM,
    USER_FOLLOWUP,
    USER_VERIFY_SYSTEM,
    USER_VERIFY,
)
from generator.models.project import AnchorProject
from generator.models.requirement import Requirement
from generator.models.review import ReviewVerdict, UserVerification


class UserAgent:
    def __init__(self, client: AsyncOpenRouterClient, model: str):
        self.client = client
        self.model = model

    async def initiate_conversation(self, requirement: Requirement, project: AnchorProject) -> str:
        user_prompt = USER_INITIATE.format(
            project_name=project.name,
            repo=project.repo,
            requirement_description=requirement.description,
        )

        if self.client.recorder:
            self.client.recorder.record_message("system", USER_INITIATE_SYSTEM, stage="user_initiate")
            self.client.recorder.record_message("user", user_prompt, stage="user_initiate")

        data = await self.client.chat_completion(
            messages=[
                {"role": "system", "content": USER_INITIATE_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            model=self.model,
            stage="user_initiate",
        )

        response = data["choices"][0]["message"]["content"]

        if self.client.recorder:
            self.client.recorder.record_message("assistant", response, stage="user_initiate", model=self.model)

        return response

    async def generate_followup(self, requirement: Requirement, assistant_response: str) -> str | None:
        user_prompt = USER_FOLLOWUP.format(
            requirement_description=requirement.description,
            assistant_response=assistant_response[:3000],
        )

        data = await self.client.chat_completion(
            messages=[
                {"role": "system", "content": USER_FOLLOWUP_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            model=self.model,
            stage="user_followup",
        )

        response = data["choices"][0]["message"]["content"]

        if "[SATISFIED]" in response:
            return None

        if self.client.recorder:
            self.client.recorder.record_message("assistant", response, stage="user_followup", model=self.model)

        return response

    async def verify_script(
        self,
        requirement: Requirement,
        script: str,
        review: ReviewVerdict,
    ) -> UserVerification:
        user_prompt = USER_VERIFY.format(
            requirement_description=requirement.description,
            script_language=requirement.script_language,
            script_content=script,
            review_verdict=review.verdict,
            review_reasoning=review.reasoning,
            review_issues=json.dumps(review.issues_found, ensure_ascii=False),
        )

        if self.client.recorder:
            self.client.recorder.record_message("system", USER_VERIFY_SYSTEM, stage="user_verify")
            self.client.recorder.record_message("user", user_prompt, stage="user_verify")

        data = await self.client.chat_completion(
            messages=[
                {"role": "system", "content": USER_VERIFY_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            model=self.model,
            stage="user_verify",
        )

        response = data["choices"][0]["message"]["content"]

        if self.client.recorder:
            self.client.recorder.record_message("assistant", response, stage="user_verify", model=self.model)

        return self._parse_verification(response)

    def _parse_verification(self, text: str) -> UserVerification:
        json_str = text
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0]

        try:
            data = json.loads(json_str.strip())
            return UserVerification(
                verdict=data.get("verdict", "FAIL"),
                reasoning=data.get("reasoning", ""),
                requirement_coverage=data.get("requirement_coverage", "none"),
            )
        except (json.JSONDecodeError, KeyError):
            return UserVerification(
                verdict="FAIL",
                reasoning=f"Failed to parse verification response: {text[:500]}",
                requirement_coverage="none",
            )
