import json

import pytest

from llm_overall.core.multi_step_pipeline import run_multi_step_pipeline


class FakeChainClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)
        self.calls: list[tuple[str, str]] = []

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        self.calls.append((system_prompt, user_prompt))
        return next(self.responses)


def make_responses() -> list[str]:
    return [
        json.dumps(
            {
                "summary": "Приложение не запускается после обновления.",
                "sentiment": "negative",
                "key_points": [
                    "Было обновление",
                    "Приложение перестало запускаться",
                    "Пользователь просит помощь",
                ],
                "important_details": [
                    "Ошибка появилась после обновления",
                ],
            }
        ),
        json.dumps(
            {
                "category": "support",
                "intent": "troubleshooting",
            }
        ),
        json.dumps(
            {"final_answer": "Перезапустите приложение и проверьте обновления."}
        ),
        json.dumps(
            {
                "is_valid": True,
                "contradictions": [],
                "missing_details": [],
            }
        ),
    ]


def test_multi_step_pipeline_success() -> None:
    client = FakeChainClient(make_responses())

    result = run_multi_step_pipeline(
        "После обновления приложение не запускается. Помогите.",
        client,
    )

    assert result["category"] == "support"
    assert result["intent"] == "troubleshooting"
    assert result["sentiment"] == "negative"
    assert len(result["key_points"]) == 3
    assert len(result["important_details"]) == 1
    assert "Перезапустите" in result["final_answer"]
    assert len(client.calls) == 4
    assert result["self_check"]["is_valid"] is True


def test_previous_results_used_in_next_steps() -> None:
    client = FakeChainClient(make_responses())

    run_multi_step_pipeline(
        "После обновления приложение не запускается.",
        client,
    )

    classification_prompt = client.calls[1][1]
    generation_prompt = client.calls[2][1]

    assert "Приложение не запускается после обновления" in (classification_prompt)
    assert "Ошибка появилась после обновления" in (classification_prompt)
    assert "troubleshooting" in generation_prompt
    assert "Было обновление" in generation_prompt
    assert "Ошибка появилась после обновления" in generation_prompt


def test_invalid_final_answer() -> None:
    responses = make_responses()
    responses[2] = '{"wrong_field": "Invalid"}'
    responses.insert(3, '{"wrong_field": "Still invalid"}')

    client = FakeChainClient(responses)

    with pytest.raises(ValueError, match="invalid final answer"):
        run_multi_step_pipeline("Приложение не работает", client)

    assert len(client.calls) == 4


def test_empty_input() -> None:
    client = FakeChainClient(make_responses())

    with pytest.raises(ValueError, match="must not be empty"):
        run_multi_step_pipeline("   ", client)

    assert client.calls == []


def test_pipeline_self_check_uses_final_answer() -> None:
    client = FakeChainClient(make_responses())

    run_multi_step_pipeline(
        "После обновления приложение не запускается.",
        client,
    )

    check_prompt = client.calls[3][1]

    assert "Перезапустите приложение" in check_prompt
    assert "Ошибка появилась после обновления" in check_prompt


def test_pipeline_reports_self_check_failure() -> None:
    responses = make_responses()
    responses[3] = json.dumps(
        {
            "is_valid": False,
            "contradictions": ["Ответ противоречит тексту"],
            "missing_details": [],
        }
    )
    client = FakeChainClient(responses)

    result = run_multi_step_pipeline(
        "После обновления приложение не запускается.",
        client,
    )

    assert result["self_check"]["is_valid"] is False
    assert result["self_check"]["contradictions"]
    assert len(client.calls) == 4


def test_pipeline_accepts_markdown_wrapped_json() -> None:
    responses = make_responses()

    responses[0] = f"```json\n{responses[0]}\n```"
    responses[2] = f"```json\n{responses[2]}\n```"
    responses[3] = f"```json\n{responses[3]}\n```"

    client = FakeChainClient(responses)

    result = run_multi_step_pipeline(
        "После обновления приложение не запускается.",
        client,
    )

    assert result["category"] == "support"
    assert result["self_check"]["is_valid"] is True
    assert len(client.calls) == 4


def test_fallback_after_invalid_json() -> None:
    responses = make_responses()
    responses[2] = "This is not JSON"
    responses.insert(
        3,
        json.dumps({"final_answer": "Проверьте настройки приложения."}),
    )

    client = FakeChainClient(responses)
    result = run_multi_step_pipeline("Приложение не работает", client)

    assert result["final_answer"] == "Проверьте настройки приложения."
    assert result["self_check"]["is_valid"] is True
    assert len(client.calls) == 5
    assert "previous response failed validation" in client.calls[3][1].lower()


def test_fallback_after_too_long_answer() -> None:
    responses = make_responses()
    responses[2] = json.dumps({"final_answer": "слово " * 81})
    responses.insert(
        3,
        json.dumps({"final_answer": "Проверьте обновления."}),
    )

    client = FakeChainClient(responses)
    result = run_multi_step_pipeline("Приложение не работает", client)

    assert result["final_answer"] == "Проверьте обновления."
    assert len(client.calls) == 5


def test_fallback_after_empty_response() -> None:
    responses = make_responses()
    responses[2] = ""
    responses.insert(
        3,
        json.dumps({"final_answer": "Перезапустите приложение."}),
    )

    client = FakeChainClient(responses)
    result = run_multi_step_pipeline("Приложение не работает", client)

    assert result["final_answer"] == "Перезапустите приложение."
    assert len(client.calls) == 5


def test_fallback_fails_on_second_invalid_response() -> None:
    responses = make_responses()
    responses[2] = "Invalid JSON"
    responses.insert(3, '{"final_answer": ""}')

    client = FakeChainClient(responses)

    with pytest.raises(ValueError, match="after fallback"):
        run_multi_step_pipeline("Приложение не работает", client)

    assert len(client.calls) == 4


def test_invalid_self_check_is_reported() -> None:
    responses = make_responses()
    responses[3] = "Invalid self-check JSON"

    client = FakeChainClient(responses)
    result = run_multi_step_pipeline("Приложение не работает", client)

    assert result["self_check"]["is_valid"] is False
    assert result["self_check"]["error"] == ("Self-check unavailable or invalid")
    assert len(client.calls) == 4


def test_fallback_after_oversized_raw_response() -> None:
    responses = make_responses()
    responses[2] = "x" * 12001
    responses.insert(
        3,
        json.dumps({"final_answer": "Проверьте настройки."}),
    )

    client = FakeChainClient(responses)
    result = run_multi_step_pipeline("Приложение не работает", client)

    assert result["final_answer"] == "Проверьте настройки."
    assert len(client.calls) == 5


def test_api_error_does_not_trigger_fallback() -> None:
    class FailingClient(FakeChainClient):
        def complete(self, system_prompt: str, user_prompt: str) -> str:
            if len(self.calls) == 2:
                self.calls.append((system_prompt, user_prompt))
                raise RuntimeError("Simulated API failure")

            return super().complete(system_prompt, user_prompt)

    client = FailingClient(make_responses())

    with pytest.raises(RuntimeError, match="Simulated API failure"):
        run_multi_step_pipeline("Приложение не работает", client)

    assert len(client.calls) == 3


def test_self_check_api_error_is_not_hidden() -> None:
    class FailingClient(FakeChainClient):
        def complete(self, system_prompt: str, user_prompt: str) -> str:
            if len(self.calls) == 3:
                self.calls.append((system_prompt, user_prompt))
                raise RuntimeError("Self-check API unavailable")

            return super().complete(system_prompt, user_prompt)

    client = FailingClient(make_responses())

    with pytest.raises(RuntimeError, match="Self-check API unavailable"):
        run_multi_step_pipeline("Приложение не работает", client)

    assert len(client.calls) == 4
