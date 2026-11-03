import json
from pathlib import Path
from time import perf_counter

from openai import APIError

from llm_overall.config import load_settings
from llm_overall.llm_client import LLMClient
from llm_overall.pipeline import run_pipeline
from llm_overall.validation import StructuredOutputError

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = PROJECT_ROOT / "examples" / "day03_inputs.json"
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "day03_results.json"


def main() -> None:
    examples = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    settings = load_settings()
    client = LLMClient(settings)

    results = []

    for example in examples:
        print(f"\nProcessing: {example['id']}")

        start_time = perf_counter()

        record = {
            "id": example["id"],
            "model": settings.model,
            "prompt_variant": "B",
        }

        try:
            result = run_pipeline(
                text=example["text"],
                client=client,
                prompt_variant="B",
            )

            record["status"] = "success"
            record["result"] = result

            print("Status: success")
            print(f"Category: {result['category']}")
            print(f"Sentiment: {result['sentiment']}")
            print(f"Summary: {result['summary']}")

        except (StructuredOutputError, APIError, ValueError) as exc:
            record["status"] = "error"
            record["error_type"] = type(exc).__name__
            record["error_message"] = str(exc)

            if isinstance(exc, StructuredOutputError):
                record["error_code"] = exc.code

            print(f"Status: error ({type(exc).__name__})")

        record["elapsed_seconds"] = round(
            perf_counter() - start_time,
            3,
        )

        results.append(record)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    successful = sum(record["status"] == "success" for record in results)

    print(f"\nSuccessful examples: {successful}/{len(results)}")
    print(f"Results saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
