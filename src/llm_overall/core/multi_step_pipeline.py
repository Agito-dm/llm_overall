import logging

from pydantic import ValidationError

from llm_overall.classification.classifier import (
    ClassificationClient,
    classify_text,
)
from llm_overall.classification.routing import get_route
from llm_overall.core.meaning import extract_meaning
from llm_overall.core.self_check import check_answer
from llm_overall.models.chain_models import FinalAnswerResult
from llm_overall.models.json_normalization import normalize_json_response
from llm_overall.models.routed_output import RoutedOutput
from llm_overall.prompts.chain_generation_prompt import (
    CHAIN_GENERATION_SYSTEM_PROMPT,
    build_chain_generation_prompt,
)

logger = logging.getLogger(__name__)


def run_multi_step_pipeline(
    text: str,
    client: ClassificationClient,
) -> dict[str, object]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty")

    # Step 1: Extract meaning
    meaning = extract_meaning(text, client)

    # Step 2: Classify request
    logger.info("Step 2/5: Classify request started")

    classification_input = (
        f"Original request:\n{text}\n\n"
        f"Extracted meaning:\n{meaning.summary}\n\n"
        "Important details:\n" + "\n".join(meaning.important_details)
    )

    classification = classify_text(classification_input, client)
    route_instruction = get_route(classification.category)

    logger.info(
        "Step 2/5 completed: category=%s, intent=%s",
        classification.category.value,
        classification.intent,
    )

    # Step 3: Build structured fields
    logger.info("Step 3/5: Build structured fields started")

    structured_fields = {
        "summary": meaning.summary,
        "category": classification.category,
        "sentiment": meaning.sentiment,
        "key_points": meaning.key_points,
    }

    logger.info(
        "Step 3/5 completed: fields=%s",
        list(structured_fields),
    )

    # Step 4: Generate final answer
    logger.info("Step 4/5: Generate final answer started")

    user_prompt = build_chain_generation_prompt(
        text=text,
        meaning=meaning,
        classification=classification,
        route_instruction=route_instruction,
    )

    raw_response = client.complete(
        system_prompt=CHAIN_GENERATION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    try:
        answer = FinalAnswerResult.model_validate_json(
            normalize_json_response(raw_response)
        )
    except ValidationError as exc:
        logger.error("Final answer validation failed: %s", exc)
        raise ValueError("LLM returned an invalid final answer") from exc

    structured_fields["final_answer"] = answer.final_answer

    result = RoutedOutput.model_validate(structured_fields).model_dump(mode="json")
    result["intent"] = classification.intent
    result["important_details"] = meaning.important_details

    logger.info("Step 4/5 completed: final answer generated")

    # Step 5: Self-check result
    self_check = check_answer(
        text=text,
        important_details=meaning.important_details,
        final_answer=answer.final_answer,
        client=client,
    )

    result["self_check"] = self_check.model_dump()

    if not self_check.is_valid:
        logger.warning(
            "Pipeline completed with quality issues: %s",
            result["self_check"],
        )
    else:
        logger.info("Pipeline completed successfully: 5/5 steps")

    return result
