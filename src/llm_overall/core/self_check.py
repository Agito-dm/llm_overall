import logging

from pydantic import ValidationError

from llm_overall.classification.classifier import ClassificationClient
from llm_overall.models.chain_models import SelfCheckResult
from llm_overall.models.json_normalization import normalize_json_response
from llm_overall.prompts.self_check_prompt import (
    SELF_CHECK_SYSTEM_PROMPT,
    build_self_check_prompt,
)

logger = logging.getLogger(__name__)


def check_answer(
    text: str,
    important_details: list[str],
    final_answer: str,
    client: ClassificationClient,
) -> SelfCheckResult:
    logger.info("Step 5/5: Self-check started")

    raw_response = client.complete(
        system_prompt=SELF_CHECK_SYSTEM_PROMPT,
        user_prompt=build_self_check_prompt(
            text=text,
            important_details=important_details,
            final_answer=final_answer,
        ),
    )

    try:
        result = SelfCheckResult.model_validate_json(
            normalize_json_response(raw_response)
        )
    except ValidationError as exc:
        logger.error("Self-check validation failed: %s", exc)
        raise ValueError("LLM returned an invalid self-check") from exc

    expected_valid = not (result.contradictions or result.missing_details)

    if result.is_valid != expected_valid:
        raise ValueError("Self-check returned inconsistent validation data")

    logger.info(
        "Step 5/5 completed: valid=%s, contradictions=%d, missing=%d",
        result.is_valid,
        len(result.contradictions),
        len(result.missing_details),
    )

    return result
