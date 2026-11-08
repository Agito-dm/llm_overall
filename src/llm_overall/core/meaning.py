import logging

from pydantic import ValidationError

from llm_overall.classification.classifier import ClassificationClient
from llm_overall.models.chain_models import MeaningResult
from llm_overall.models.json_normalization import normalize_json_response
from llm_overall.prompts.meaning_prompt import (
    MEANING_SYSTEM_PROMPT,
    build_meaning_prompt,
)

logger = logging.getLogger(__name__)


def extract_meaning(
    text: str,
    client: ClassificationClient,
) -> MeaningResult:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty")

    logger.info("Step 1/5: Extract meaning started")

    raw_response = client.complete(
        system_prompt=MEANING_SYSTEM_PROMPT,
        user_prompt=build_meaning_prompt(text),
    )

    try:
        result = MeaningResult.model_validate_json(
            normalize_json_response(raw_response)
        )
    except ValidationError as exc:
        logger.error("Meaning extraction validation failed: %s", exc)
        raise ValueError("LLM returned invalid meaning data") from exc

    logger.info(
        "Step 1/5 completed: sentiment=%s, key_points=%d, details=%d",
        result.sentiment,
        len(result.key_points),
        len(result.important_details),
    )

    return result
