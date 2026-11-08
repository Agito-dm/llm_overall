import argparse
import json
import logging

from llm_overall.clients.llm_client import LLMClient
from llm_overall.config import load_settings
from llm_overall.core.multi_step_pipeline import run_multi_step_pipeline

EXAMPLES = [
    {
        "name": "support",
        "text": (
            "После обновления приложения на Windows 11 "
            "оно перестало запускаться. Появляется ошибка 503. "
            "Перезагрузка компьютера не помогла. "
            "Что ещё можно проверить?"
        ),
    },
    {
        "name": "feedback",
        "text": (
            "Пользуюсь сервисом уже три месяца. "
            "Интерфейс удобный, особенно поиск документов. "
            "Но хотелось бы добавить тёмную тему "
            "и возможность сохранять фильтры."
        ),
    },
    {
        "name": "complaint",
        "text": (
            "Я оплатил заказ 15 октября, доставка была обещана "
            "до 20 октября. Сегодня уже 25 октября, "
            "заказ не пришёл. Поддержка дважды обещала "
            "ответить, но так и не связалась со мной. "
            "Прошу разобраться и вернуть деньги."
        ),
    },
    {
        "name": "sales",
        "text": (
            "Интересует корпоративная подписка на сервис "
            "для команды из 12 человек. "
            "Какие есть тарифы и скидки при оплате за год? "
            "Также важно узнать, можно ли получить счёт "
            "для юридического лица."
        ),
    },
    {
        "name": "general_question",
        "text": (
            "Объясните простыми словами, чем отличается "
            "обучение с учителем от обучения без учителя. "
            "Приведите по одному примеру каждого подхода "
            "из машинного обучения."
        ),
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 5 multi-step LLM chain demo")
    parser.add_argument(
        "--example",
        type=int,
        choices=range(1, len(EXAMPLES) + 1),
        required=True,
        help="Example number from 1 to 5",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(name)s | %(message)s",
    )

    example = EXAMPLES[args.example - 1]
    client = LLMClient(load_settings())

    print(f"\nExample {args.example}: {example['name']}")
    print(f"Input: {example['text']}\n")

    result = run_multi_step_pipeline(
        text=example["text"],
        client=client,
    )

    print("\nFINAL STRUCTURED RESULT")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\nQUALITY CHECK")
    if result["self_check"]["is_valid"]:
        print("PASS: No issues detected by self-check")
    else:
        print("REVIEW: Self-check detected potential issues")
        print(
            "Contradictions:",
            result["self_check"]["contradictions"],
        )
        print(
            "Missing details:",
            result["self_check"]["missing_details"],
        )


if __name__ == "__main__":
    main()
