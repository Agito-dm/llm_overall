import json

from openai import APIError

from llm_overall.classification.classifier import classify_text
from llm_overall.clients.llm_client import LLMClient
from llm_overall.config import load_settings


def main() -> None:
    settings = load_settings()
    client = LLMClient(settings)

    text = (
        "После обновления приложение перестало запускаться. "
        "Появляется ошибка при входе. Как это исправить?"
    )

    result = classify_text(text, client)

    print("Input:", text)
    print(
        "Classification:",
        json.dumps(
            result.model_dump(mode="json"),
            ensure_ascii=False,
            indent=2,
        ),
    )


if __name__ == "__main__":
    try:
        main()
    except (APIError, ValueError) as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc
