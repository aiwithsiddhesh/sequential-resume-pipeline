from typing import Annotated

from pydantic import BaseModel, Field

Score = Annotated[int, Field(ge=0, le=100)]


class ParsedResume(BaseModel):
    skills: list[str]
    experience_bullets: list[str]


class ParsedJobDescription(BaseModel):
    required_skills: list[str]
    requirements: list[str]


class GapAnalysis(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]
    match_score: Score


class TailoredResume(BaseModel):
    tailored_bullets: list[str]


class CoverLetter(BaseModel):
    text: str


class ValidationResult(BaseModel):
    passed: bool
    covered_keywords: list[str]
    missing_keywords: list[str]
    validation_score: Score


class PipelineState(BaseModel):
    raw_resume: str
    raw_job_description: str

    parsed_resume: ParsedResume | None = None
    parsed_job_description: ParsedJobDescription | None = None
    gap_analysis: GapAnalysis | None = None
    tailored_resume: TailoredResume | None = None
    cover_letter: CoverLetter | None = None
    validation: ValidationResult | None = None
