import pytest

from llm_overall.core.pipeline import run_pipeline
from llm_overall.models.validation import StructuredOutputError


class FakeLLMClient:
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return """
        {
            "summary": "Test summary",
            "category": "question",
            "sentiment": "neutral",
            "key_points": [
                "Point 1",
                "Point 2",
                "Point 3"
            ],
            "final_answer": "Helpful response"
        }
        """


class InvalidJSONClient:
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return "This is not JSON"


def test_pipeline_success() -> None:
    result = run_pipeline(
        "Explain machine learning",
        FakeLLMClient(),
    )

    assert result["summary"] == "Test summary"
    assert result["category"] == "question"
    assert result["sentiment"] == "neutral"
    assert len(result["key_points"]) == 3
    assert result["final_answer"] == "Helpful response"
    assert len(result) == 5


def test_empty_input() -> None:
    with pytest.raises(ValueError):
        run_pipeline("", FakeLLMClient())


def test_invalid_json() -> None:
    with pytest.raises(
        StructuredOutputError,
        match="invalid JSON",
    ) as error:
        run_pipeline(
            "Some text",
            InvalidJSONClient(),
        )

    assert error.value.code == "invalid_json"


def test_all_prompt_variants() -> None:
    for variant_id in ("A", "B", "C"):
        result = run_pipeline(
            "Explain attention",
            FakeLLMClient(),
            prompt_variant=variant_id,
        )

        assert len(result["key_points"]) == 3
        assert len(result) == 5


def test_unknown_prompt_variant() -> None:
    with pytest.raises(
        ValueError,
        match="Unknown prompt variant",
    ):
        run_pipeline(
            "Explain attention",
            FakeLLMClient(),
            prompt_variant="unknown",
        )
