import json
from typing import Protocol

from llm_overall.prompt_variants import PROMPT_VARIANTS


class TextGenerator(Protocol):
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str: ...


def run_pipeline(
    text: str,
    client: TextGenerator,
    prompt_variant: str | None = None,
) -> dict:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty")

    selected_variant = "B" if prompt_variant is None else prompt_variant

    if selected_variant not in PROMPT_VARIANTS:
        raise ValueError(f"Unknown prompt variant: {selected_variant}")

    variant = PROMPT_VARIANTS[selected_variant]

    system_prompt = variant.system_prompt
    user_prompt = variant.build_user_prompt(text)

    raw_response = client.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    try:
        result = json.loads(raw_response)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM returned invalid JSON") from exc

    if not isinstance(result, dict):
        raise TypeError("LLM result must be a JSON object")

    required_fields = {
        "summary",
        "key_points",
        "response",
    }

    if not required_fields.issubset(result):
        raise ValueError("LLM result is missing required fields")

    points = result["key_points"]

    if not isinstance(points, list) or len(points) != 3:
        raise ValueError("LLM must return exactly 3 key points")

    return result
