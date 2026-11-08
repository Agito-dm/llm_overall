import pytest

from llm_overall.models.json_normalization import normalize_json_response


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('{"value": 1}', '{"value": 1}'),
        ('```json\n{"value": 1}\n```', '{"value": 1}'),
        ('```\n{"value": 1}\n```', '{"value": 1}'),
        ("```json\nnot JSON\n```", "not JSON"),
    ],
)
def test_normalize_json_response(raw: str, expected: str) -> None:
    assert normalize_json_response(raw) == expected
