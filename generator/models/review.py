from pydantic import BaseModel


class ReviewVerdict(BaseModel):
    verdict: str
    reasoning: str
    issues_found: list[str]
    corrections: list[str]
    api_checks: list[dict]


class UserVerification(BaseModel):
    verdict: str
    reasoning: str
    requirement_coverage: str
