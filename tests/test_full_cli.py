import json
import sys
from types import SimpleNamespace

import main


def test_full_cli(monkeypatch, capsys):
    expected = {
        "summary": "Проблема после обновления",
        "category": "support",
        "sentiment": "negative",
        "key_points": ["Ошибка 503", "Не запускается", "Нужна помощь"],
        "final_answer": "Проверьте соединение.",
        "intent": "troubleshooting",
        "important_details": ["Windows 11"],
        "self_check": {
            "is_valid": True,
            "contradictions": [],
            "missing_details": [],
        },
    }

    calls = []

    def fake_pipeline(text, client):
        calls.append(text)
        return expected

    monkeypatch.setattr(
        main,
        "load_settings",
        lambda: SimpleNamespace(api_key="test", model="test"),
    )
    monkeypatch.setattr(main, "LLMClient", lambda settings: object())
    monkeypatch.setattr(
        main,
        "run_multi_step_pipeline",
        fake_pipeline,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--full", "--text", "Ошибка 503"],
    )

    main.main()

    output = json.loads(capsys.readouterr().out)

    assert output == expected
    assert calls == ["Ошибка 503"]
    assert output["self_check"]["is_valid"] is True


def test_full_demo_uses_five_examples(monkeypatch, capsys):
    monkeypatch.setattr(
        main,
        "load_settings",
        lambda: SimpleNamespace(api_key="test", model="test"),
    )
    monkeypatch.setattr(main, "LLMClient", lambda settings: object())

    calls = []

    def fake_pipeline(text, client):
        calls.append(text)
        return {
            "summary": "Test summary",
            "category": "general_question",
            "sentiment": "neutral",
            "key_points": ["One", "Two", "Three"],
            "final_answer": "Test answer",
            "intent": "information",
            "important_details": [],
            "self_check": {
                "is_valid": True,
                "contradictions": [],
                "missing_details": [],
            },
        }

    monkeypatch.setattr(
        main,
        "run_multi_step_pipeline",
        fake_pipeline,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", "--full", "--demo"],
    )

    main.main()

    results = json.loads(capsys.readouterr().out)

    assert len(results) == 5
    assert len(calls) == 5
    assert [item["id"] for item in results] == [
        "support",
        "feedback",
        "complaint",
        "sales",
        "general_question",
    ]
    assert all("self_check" in item for item in results)


def test_full_cli_saves_json(monkeypatch, tmp_path, capsys):
    output_path = tmp_path / "results" / "output.json"

    monkeypatch.setattr(
        main,
        "load_settings",
        lambda: SimpleNamespace(api_key="test", model="test"),
    )
    monkeypatch.setattr(main, "LLMClient", lambda settings: object())
    monkeypatch.setattr(
        main,
        "run_multi_step_pipeline",
        lambda text, client: {
            "summary": "Test summary",
            "category": "support",
            "final_answer": "Test answer",
            "self_check": {"is_valid": True},
        },
    )
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "--full",
            "--text",
            "Test input",
            "--output",
            str(output_path),
        ],
    )

    main.main()

    console_result = json.loads(capsys.readouterr().out)
    saved_result = json.loads(output_path.read_text(encoding="utf-8"))

    assert output_path.exists()
    assert saved_result == console_result
    assert saved_result["category"] == "support"
