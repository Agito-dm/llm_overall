import json
import logging
import time
from pathlib import Path

from openai import APIError

from llm_overall.clients.llm_client import LLMClient
from llm_overall.config import load_settings
from llm_overall.core.routed_pipeline import run_routed_pipeline

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "examples" / "day04_inputs.json"
OUTPUT_PATH = ROOT / "outputs" / "day04_results.json"


def main() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    examples = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    client = LLMClient(load_settings())

    results = []
    category_correct = 0
    intent_correct = 0

    for index, example in enumerate(examples, start=1):
        if index > 1:
            time.sleep(10)
        print(f"\n[{index}/{len(examples)}] {example['id']}")

        record = {
            "id": example["id"],
            "input": example["text"],
            "expected_category": example["expected_category"],
            "expected_intent": example["expected_intent"],
        }

        try:
            output = run_routed_pipeline(example["text"], client)

            category_ok = output["category"] == example["expected_category"]
            intent_ok = output["intent"] == example["expected_intent"]

            category_correct += int(category_ok)
            intent_correct += int(intent_ok)

            record.update(
                {
                    "status": "success",
                    "category_correct": category_ok,
                    "intent_correct": intent_ok,
                    "output": output,
                }
            )

            print(f"Category: {output['category']} | OK: {category_ok}")
            print(f"Intent: {output['intent']} | OK: {intent_ok}")
            print(f"Answer: {output['final_answer']}")

        except (APIError, ValueError) as exc:
            record.update(
                {
                    "status": "error",
                    "error": str(exc),
                }
            )
            print(f"ERROR: {exc}")

        results.append(record)

    total = len(examples)
    successful = sum(record["status"] == "success" for record in results)

    summary = {
        "total": total,
        "successful": successful,
        "category_correct": category_correct,
        "intent_correct": intent_correct,
        "category_accuracy": category_correct / total if total else 0,
        "intent_accuracy": intent_correct / total if total else 0,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(
            {"summary": summary, "results": results},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("\n=== DAY 4 EVALUATION ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Results saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
