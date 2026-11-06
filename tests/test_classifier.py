import pytest

from llm_overall.classification.categories import Category
from llm_overall.classification.classifier import classify_text


class FakeClassificationClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0
        self.last_system_prompt = ""
        self.last_user_prompt = ""

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        self.calls += 1
        self.last_system_prompt = system_prompt
        self.last_user_prompt = user_prompt
        return self.response


@pytest.mark.parametrize(
    ("category", "intent"),
    [
        ("support", "troubleshooting"),
        ("support", "how_to"),
        ("feedback", "praise"),
        ("complaint", "refund_request"),
        ("sales", "pricing"),
        ("sales", "comparison"),
        ("general_question", "information"),
        ("general_question", "other"),
    ],
)
def test_valid_classification(
    category: str,
    intent: str,
) -> None:
    response = f'{{"category": "{category}", "intent": "{intent}"}}'
    client = FakeClassificationClient(response)

    result = classify_text("Test user message", client)

    assert result.category == Category(category)
    assert result.intent == intent
    assert client.calls == 1
    assert "Test user message" in client.last_user_prompt
    assert "Allowed categories" in client.last_system_prompt


@pytest.mark.parametrize(
    "response",
    [
        "Not JSON",
        '{"category": "unknown", "intent": "other"}',
        '{"category": "support"}',
        '{"category": 123, "intent": "how_to"}',
        '{"category": "support", "intent": "invalid"}',
        '{"category": "support", "intent": "how_to", "extra": 1}',
    ],
)
def test_invalid_classification(response: str) -> None:
    client = FakeClassificationClient(response)

    with pytest.raises(
        ValueError,
        match="invalid classification",
    ):
        classify_text("Test input", client)


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_input(text: str) -> None:
    client = FakeClassificationClient("{}")

    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        classify_text(text, client)

    assert client.calls == 0
