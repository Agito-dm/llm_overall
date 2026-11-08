import json

import pytest

from llm_overall.core.self_check import check_answer


class FakeCheckClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = 0
        self.last_prompt = ""

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        self.calls += 1
        self.last_prompt = user_prompt
        return self.response


def test_self_check_valid_answer() -> None:
    client = FakeCheckClient(
        json.dumps(
            {
                "is_valid": True,
                "contradictions": [],
                "missing_details": [],
            }
        )
    )

    result = check_answer(
        text="Приложение не запускается после обновления.",
        important_details=["Ошибка после обновления"],
        final_answer="Проверьте настройки и перезапустите приложение.",
        client=client,
    )

    assert result.is_valid is True
    assert result.contradictions == []
    assert result.missing_details == []
    assert client.calls == 1
    assert "Ошибка после обновления" in client.last_prompt


def test_self_check_detected_issues() -> None:
    client = FakeCheckClient(
        json.dumps(
            {
                "is_valid": False,
                "contradictions": ["Переустановка уже выполнялась"],
                "missing_details": ["Не учтена ошибка 503"],
            }
        )
    )

    result = check_answer(
        text="Переустановка не помогла. Ошибка 503.",
        important_details=["Ошибка 503", "Переустановка не помогла"],
        final_answer="Попробуйте переустановить приложение.",
        client=client,
    )

    assert result.is_valid is False
    assert len(result.contradictions) == 1
    assert len(result.missing_details) == 1


@pytest.mark.parametrize(
    "response",
    [
        "Not JSON",
        "{}",
        '{"is_valid": "yes", "contradictions": [], "missing_details": []}',
        '{"is_valid": true, "contradictions": [], "missing_details": ["X"]}',
    ],
)
def test_self_check_invalid_response(response: str) -> None:
    client = FakeCheckClient(response)

    with pytest.raises(ValueError, match="invalid self-check|inconsistent"):
        check_answer(
            text="Test",
            important_details=["Detail"],
            final_answer="Answer",
            client=client,
        )
