import json

import pytest

from llm_overall.validation import StructuredOutputError, parse_structured_output


def make_valid_payload() -> dict[str, object]:
    return {
        "summary": "Пользователь изучает Python",
        "category": "question",
        "sentiment": "neutral",
        "key_points": [
            "Изучает Python",
            "Интересуется JSON",
            "Просит совет",
        ],
        "final_answer": "Начните с модуля json.",
    }


def test_valid_json() -> None:
    payload = make_valid_payload()

    result = parse_structured_output(json.dumps(payload, ensure_ascii=False))

    assert result == payload


def test_whitespace_is_removed() -> None:
    payload = make_valid_payload()
    payload["summary"] = "  Текст  "

    result = parse_structured_output(json.dumps(payload))

    assert result["summary"] == "Текст"


def test_invalid_json() -> None:
    with pytest.raises(StructuredOutputError) as error:
        parse_structured_output("{broken")

    assert error.value.code == "invalid_json"


def test_missing_field() -> None:
    payload = make_valid_payload()
    del payload["sentiment"]

    with pytest.raises(StructuredOutputError) as error:
        parse_structured_output(json.dumps(payload))

    assert error.value.code == "missing_fields"
    assert "sentiment" in str(error.value)


def test_json_array_instead_of_object() -> None:
    with pytest.raises(StructuredOutputError) as error:
        parse_structured_output("[1, 2, 3]")

    assert error.value.code == "invalid_types"


@pytest.mark.parametrize(
    ("changes", "expected_code"),
    [
        ({"summary": 123}, "invalid_types"),
        ({"key_points": "not a list"}, "invalid_types"),
        ({"key_points": ["first", 123, "third"]}, "invalid_types"),
        ({"key_points": ["only one"]}, "invalid_schema"),
        ({"category": "unknown"}, "invalid_schema"),
        ({"final_answer": "   "}, "invalid_schema"),
        ({"unexpected": "extra field"}, "invalid_schema"),
    ],
)
def test_invalid_fields(changes: dict, expected_code: str) -> None:
    payload = make_valid_payload()
    payload.update(changes)

    with pytest.raises(StructuredOutputError) as error:
        parse_structured_output(json.dumps(payload))

    assert error.value.code == expected_code
