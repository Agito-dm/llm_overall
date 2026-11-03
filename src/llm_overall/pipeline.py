from typing import Protocol

from llm_overall.prompt_variants import PROMPT_VARIANTS
from llm_overall.validation import parse_structured_output


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

    return parse_structured_output(raw_response)
