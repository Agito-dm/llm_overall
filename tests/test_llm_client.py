from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from openai import APIConnectionError, APIStatusError

from llm_overall.clients import llm_client
from llm_overall.clients.llm_client import LLMClient
from llm_overall.config import Settings


def make_completion(content: str | None):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=None,
    )


def make_status_error(status_code: int) -> APIStatusError:
    response = MagicMock()
    response.status_code = status_code

    return APIStatusError(
        message="Simulated API error",
        response=response,
        body=None,
    )


def make_client(monkeypatch, responses):
    fake_api = MagicMock()
    fake_api.chat.completions.create.side_effect = responses

    monkeypatch.setattr(
        llm_client,
        "OpenAI",
        lambda **kwargs: fake_api,
    )

    client = LLMClient(Settings(api_key="test-key", model="test-model"))
    return client, fake_api


def test_retry_after_connection_error(monkeypatch):
    delays = []
    monkeypatch.setattr(llm_client, "sleep", delays.append)

    error = APIConnectionError(request=MagicMock())
    client, fake_api = make_client(
        monkeypatch,
        [error, make_completion("Success")],
    )

    result = client.complete("system", "user")

    assert result == "Success"
    assert fake_api.chat.completions.create.call_count == 2
    assert delays == [1.0]


def test_retry_after_server_error(monkeypatch):
    delays = []
    monkeypatch.setattr(llm_client, "sleep", delays.append)

    client, fake_api = make_client(
        monkeypatch,
        [
            make_status_error(503),
            make_completion("Recovered"),
        ],
    )

    assert client.complete("system", "user") == "Recovered"
    assert fake_api.chat.completions.create.call_count == 2
    assert delays == [1.0]


def test_retry_limit(monkeypatch):
    delays = []
    monkeypatch.setattr(llm_client, "sleep", delays.append)

    client, fake_api = make_client(
        monkeypatch,
        [
            make_status_error(503),
            make_status_error(503),
            make_status_error(503),
        ],
    )

    with pytest.raises(APIStatusError):
        client.complete("system", "user")

    assert fake_api.chat.completions.create.call_count == 3
    assert delays == [1.0, 2.0]


def test_non_retryable_api_error(monkeypatch):
    delays = []
    monkeypatch.setattr(llm_client, "sleep", delays.append)

    client, fake_api = make_client(
        monkeypatch,
        [make_status_error(400)],
    )

    with pytest.raises(APIStatusError):
        client.complete("system", "user")

    assert fake_api.chat.completions.create.call_count == 1
    assert delays == []


@pytest.mark.parametrize("content", ["", "   ", None])
def test_empty_response(monkeypatch, content):
    client, fake_api = make_client(
        monkeypatch,
        [make_completion(content)],
    )

    with pytest.raises(ValueError, match="empty response"):
        client.complete("system", "user")

    assert fake_api.chat.completions.create.call_count == 1
