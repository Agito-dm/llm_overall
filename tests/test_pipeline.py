import pytest

from llm_overall.pipeline import run_pipeline


class FakeLLMClient:
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        return """
        {
            "summary": "Test summary",
            "key_points": [
                "Point 1",
                "Point 2",
                "Point 3"
            ],
            "response": "Helpful response"
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
    assert len(result["key_points"]) == 3
    assert result["response"] == "Helpful response"


def test_empty_input() -> None:
    with pytest.raises(ValueError):
        run_pipeline("", FakeLLMClient())


def test_invalid_json() -> None:
    with pytest.raises(
        ValueError,
        match="invalid JSON",
    ):
        run_pipeline(
            "Some text",
            InvalidJSONClient(),
        )
