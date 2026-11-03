from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StructuredOutput(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        str_strip_whitespace=True,
        str_min_length=1,
    )

    summary: str
    category: Literal["question", "problem", "feedback", "other"]
    sentiment: Literal["positive", "negative", "neutral", "mixed"]
    key_points: list[str] = Field(min_length=3, max_length=3)
    final_answer: str
