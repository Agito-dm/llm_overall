import json

import pytest

from llm_overall.core.routed_pipeline import run_routed_pipeline


class FakeRoutedClient:
    def __init__(self, category: str, intent: str) -> None:
        self.category = category
        self.intent = intent
        self.prompts: list[str] = []
        self.calls = 0

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        self.prompts.append(system_prompt)

        if self.calls == 1:
            return json.dumps({"category": self.category, "intent": self.intent})

        return json.dumps(
            {
                "summary": "Test summary",
                "category": self.category,
                "sentiment": "neutral",
                "key_points": ["First", "Second", "Third"],
                "final_answer": "Test response",
            }
        )


@pytest.mark.parametrize(
    ("category", "intent", "expected_instruction"),
    [
        ("support", "troubleshooting", "troubleshooting steps"),
        ("feedback", "praise", "Acknowledge"),
        ("complaint", "service_issue", "empathy"),
        ("sales", "pricing", "sales-oriented"),
        ("general_question", "information", "clearly"),
    ],
)
def test_routed_pipeline(
    category: str,
    intent: str,
    expected_instruction: str,
) -> None:
    client = FakeRoutedClient(category, intent)

    result = run_routed_pipeline("Test user message", client)

    assert result["category"] == category
    assert result["intent"] == intent
    assert len(result["key_points"]) == 3
    assert len(result) == 6
    assert client.calls == 2
    assert expected_instruction in client.prompts[1]


def test_empty_input() -> None:
    client = FakeRoutedClient("support", "how_to")

    with pytest.raises(ValueError, match="must not be empty"):
        run_routed_pipeline("", client)

    assert client.calls == 0


def test_mismatched_category() -> None:
    class MismatchedClient(FakeRoutedClient):
        def complete(
            self,
            system_prompt: str,
            user_prompt: str,
        ) -> str:
            response = super().complete(system_prompt, user_prompt)

            if self.calls == 2:
                data = json.loads(response)
                data["category"] = "sales"
                return json.dumps(data)

            return response

    client = MismatchedClient("support", "troubleshooting")

    with pytest.raises(ValueError, match="does not match"):
        run_routed_pipeline("Application does not start", client)

    assert client.calls == 2


@pytest.mark.parametrize(
    ("extra_field", "extra_value"),
    [
        ("intent", "information"),
        ("detected_intent", "information"),
        ("additional_data", None),
    ],
)
def test_redundant_generated_fields(
    extra_field: str,
    extra_value: str | None,
) -> None:
    class ExtraFieldClient(FakeRoutedClient):
        def complete(
            self,
            system_prompt: str,
            user_prompt: str,
        ) -> str:
            response = super().complete(system_prompt, user_prompt)

            if self.calls == 2:
                data = json.loads(response)
                data[extra_field] = extra_value
                return json.dumps(data)

            return response

    client = ExtraFieldClient("general_question", "information")

    result = run_routed_pipeline("Explain neural networks", client)

    assert result["category"] == "general_question"
    assert result["intent"] == "information"
    assert set(result) == {
        "summary",
        "category",
        "sentiment",
        "key_points",
        "final_answer",
        "intent",
    }
    assert client.calls == 2


def test_unknown_extra_field_is_rejected() -> None:
    class UnknownFieldClient(FakeRoutedClient):
        def complete(
            self,
            system_prompt: str,
            user_prompt: str,
        ) -> str:
            response = super().complete(system_prompt, user_prompt)

            if self.calls == 2:
                data = json.loads(response)
                data["unexpected_field"] = "invalid"
                return json.dumps(data)

            return response

    client = UnknownFieldClient("support", "troubleshooting")

    with pytest.raises(
        ValueError,
        match="invalid routed response",
    ):
        run_routed_pipeline("Application error", client)
