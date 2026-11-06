import argparse
import json
import logging
from pathlib import Path

from openai import APIError

from llm_overall.clients.llm_client import LLMClient
from llm_overall.config import load_settings
from llm_overall.core.pipeline import run_pipeline

PROJECT_ROOT = Path(__file__).resolve().parent


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="LLM text processing pipeline")

    source = parser.add_mutually_exclusive_group(required=True)

    source.add_argument(
        "--text",
        type=str,
        help="Text to process",
    )

    source.add_argument(
        "--demo",
        action="store_true",
        help="Process predefined examples",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Save result as JSON",
    )

    args = parser.parse_args()

    try:
        settings = load_settings()
        client = LLMClient(settings)

        if args.demo:
            examples_path = PROJECT_ROOT / "examples" / "sample_inputs.json"

            examples = json.loads(examples_path.read_text(encoding="utf-8"))

            result = [
                {
                    "id": example["id"],
                    **run_pipeline(example["text"], client),
                }
                for example in examples
            ]
        else:
            result = run_pipeline(args.text, client)

        output = json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )

        print(output)

        if args.output:
            args.output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            args.output.write_text(
                output + "\n",
                encoding="utf-8",
            )

    except (APIError, TypeError, ValueError, OSError) as exc:
        parser.exit(
            status=1,
            message=f"Error: {exc}\n",
        )


if __name__ == "__main__":
    main()
