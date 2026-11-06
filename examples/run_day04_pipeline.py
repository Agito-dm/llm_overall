import json
import logging

from openai import APIError

from llm_overall.clients.llm_client import LLMClient
from llm_overall.config import load_settings
from llm_overall.core.routed_pipeline import run_routed_pipeline


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    settings = load_settings()
    client = LLMClient(settings)

    text = (
        "После обновления приложение перестало запускаться. "
        "Появляется ошибка при входе. Как это исправить?"
    )

    result = run_routed_pipeline(text, client)

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (APIError, ValueError) as exc:
        print(f"Error: {exc}")
        raise SystemExit(1) from exc
