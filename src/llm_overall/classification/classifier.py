import logging
from typing import Protocol

from pydantic import ValidationError

from llm_overall.models.schemas import ClassificationResult
from llm_overall.prompts.classification_prompt import (
    CLASSIFICATION_SYSTEM_PROMPT,
    build_classification_prompt,
)

logger = logging.getLogger(__name__)


class ClassificationClient(Protocol):
    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str: ...


def classify_text(
    text: str,
    client: ClassificationClient,
) -> ClassificationResult:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty")

    logger.info("Starting request classification")

    raw_response = client.complete(
        system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
        user_prompt=build_classification_prompt(text),
    )

    try:
        result = ClassificationResult.model_validate_json(raw_response)
    except ValidationError as exc:
        logger.warning("Invalid classification response: %s", exc)
        raise ValueError("LLM returned an invalid classification") from exc

    logger.info(
        "Classification: category=%s, intent=%s",
        result.category.value,
        result.intent,
    )

    return result
