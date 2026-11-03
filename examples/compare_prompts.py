import json
import logging
from pathlib import Path
from time import perf_counter

from openai import APIError

from llm_overall.config import load_settings
from llm_overall.llm_client import LLMClient
from llm_overall.pipeline import run_pipeline
from llm_overall.prompt_variants import PROMPT_VARIANTS

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def count_words(text: str) -> int:
    return len(text.split())


def evaluate_result(result: dict) -> dict:
    summary = result.get("summary")
    points = result.get("key_points")
    response = result.get("final_answer")

    checks = {
        "summary_valid": (isinstance(summary, str) and 0 < count_words(summary) <= 50),
        "key_points_valid": (
            isinstance(points, list)
            and len(points) == 3
            and all(isinstance(point, str) and point.strip() for point in points)
        ),
        "response_valid": (
            isinstance(response, str) and 0 < count_words(response) <= 80
        ),
    }

    return {
        "checks": checks,
        "score": sum(checks.values()),
        "max_score": len(checks),
    }


def main() -> None:
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    examples_path = PROJECT_ROOT / "examples" / "sample_inputs.json"

    examples = json.loads(examples_path.read_text(encoding="utf-8"))

    settings = load_settings()
    client = LLMClient(settings)

    results = []

    for example in examples:
        for variant_id, variant in PROMPT_VARIANTS.items():
            print(f"Running {example['id']} with prompt {variant_id}...")

            started = perf_counter()

            record = {
                "example_id": example["id"],
                "variant": variant_id,
                "prompt_name": variant.name,
                "model": settings.model,
            }

            try:
                result = run_pipeline(
                    example["text"],
                    client,
                    prompt_variant=variant_id,
                )

                elapsed = perf_counter() - started

                record.update(
                    {
                        "status": "success",
                        "elapsed_seconds": round(elapsed, 3),
                        "evaluation": evaluate_result(result),
                        "result": result,
                    }
                )

            except (APIError, ValueError, TypeError) as exc:
                elapsed = perf_counter() - started

                record.update(
                    {
                        "status": "error",
                        "elapsed_seconds": round(elapsed, 3),
                        "error_type": type(exc).__name__,
                    }
                )

                print(f"Failed: {type(exc).__name__}")

            results.append(record)

            output_path = PROJECT_ROOT / "outputs" / "day02_comparison.json"

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_path.write_text(
                json.dumps(
                    results,
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

    print("\nComparison summary:")

    for variant_id in PROMPT_VARIANTS:
        records = [item for item in results if item["variant"] == variant_id]

        successful = [item for item in records if item["status"] == "success"]

        average_time = (
            sum(item["elapsed_seconds"] for item in successful) / len(successful)
            if successful
            else None
        )

        total_score = sum(item["evaluation"]["score"] for item in successful)

        print(
            f"{variant_id}: "
            f"success={len(successful)}/{len(records)}, "
            f"score={total_score}/{len(records) * 3}, "
            f"avg_time={average_time}"
        )

    print("\nResults saved to outputs/day02_comparison.json")


if __name__ == "__main__":
    main()
