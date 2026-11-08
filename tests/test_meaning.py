import json

import pytest

from llm_overall.core.meaning import extract_meaning


class FakeMeaningClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0
        self.last_user_prompt = ""

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        self.calls += 1
        self.last_user_prompt = user_prompt
        return self.response


def test_extract_meaning_success() -> None:
    data = {
        "summary": "Программа перестала запускаться после обновления.",
        "sentiment": "negative",
        "key_points": [
            "Программа обновлена",
            "Приложение не запускается",
            "Пользователю нужна помощь",
        ],
        "important_details": [
            "Проблема возникла после обновления",
        ],
    }
    client = FakeMeaningClient(json.dumps(data))

    result = extract_meaning("После обновления программа не работает", client)

    assert result.sentiment == "negative"
    assert len(result.key_points) == 3
    assert len(result.important_details) == 1
    assert client.calls == 1
    assert "После обновления" in client.last_user_prompt


@pytest.mark.parametrize(
    "response",
    [
        "Not JSON",
        '{"summary": "Test"}',
        "[]",
        '{"summary": 123}',
    ],
)
def test_extract_meaning_invalid_response(response: str) -> None:
    client = FakeMeaningClient(response)

    with pytest.raises(ValueError, match="invalid meaning data"):
        extract_meaning("Test input", client)


@pytest.mark.parametrize("text", ["", "   "])
def test_extract_meaning_empty_input(text: str) -> None:
    client = FakeMeaningClient("{}")

    with pytest.raises(ValueError, match="must not be empty"):
        extract_meaning(text, client)

    assert client.calls == 0
