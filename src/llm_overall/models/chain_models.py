from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MeaningResult(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
        str_min_length=1,
    )

    summary: str
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    key_points: list[str] = Field(min_length=3, max_length=3)
    important_details: list[str] = Field(min_length=1)


class FinalAnswerResult(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
        str_min_length=1,
    )

    final_answer: str


class SelfCheckResult(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    is_valid: bool
    contradictions: list[str]
    missing_details: list[str]
