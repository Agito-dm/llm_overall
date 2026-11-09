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
    FALLBACK_GENERATION_SYSTEM_PROMPT,
    build_chain_generation_prompt,
    build_fallback_generation_prompt,
)

logger = logging.getLogger(__name__)

MAX_FINAL_ANSWER_WORDS = 80
MAX_FINAL_ANSWER_CHARS = 2000
MAX_RAW_RESPONSE_CHARS = 12000


def validate_final_answer(raw_response: str) -> FinalAnswerResult:
    if len(raw_response) > MAX_RAW_RESPONSE_CHARS:
        raise ValueError("LLM returned an invalid final answer: raw response too long")

    try:
        answer = FinalAnswerResult.model_validate_json(
            normalize_json_response(raw_response)
        )
    except ValidationError as exc:
        raise ValueError("LLM returned an invalid final answer") from exc

    word_count = len(answer.final_answer.split())

    if word_count > MAX_FINAL_ANSWER_WORDS:
        raise ValueError("LLM returned an invalid final answer: too many words")

    if len(answer.final_answer) > MAX_FINAL_ANSWER_CHARS:
        raise ValueError("LLM returned an invalid final answer: too many characters")

    return answer


def generate_final_answer(
    client: ClassificationClient,
    user_prompt: str,
) -> FinalAnswerResult:
    try:
        raw_response = client.complete(
            system_prompt=CHAIN_GENERATION_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        return validate_final_answer(raw_response)
    except ValueError as exc:
        logger.warning(
            "Primary generation failed validation: %s",
            exc,
        )

    logger.info("Starting fallback generation")

    try:
        fallback_response = client.complete(
            system_prompt=FALLBACK_GENERATION_SYSTEM_PROMPT,
            user_prompt=build_fallback_generation_prompt(user_prompt),
        )
        answer = validate_final_answer(fallback_response)
    except ValueError as exc:
        logger.error("Fallback generation failed: %s", exc)
        raise ValueError("LLM returned an invalid final answer after fallback") from exc

    logger.info("Fallback generation succeeded")
    return answer


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

    answer = generate_final_answer(client, user_prompt)

    structured_fields["final_answer"] = answer.final_answer
    result = RoutedOutput.model_validate(structured_fields).model_dump(mode="json")

    result["intent"] = classification.intent
    result["important_details"] = meaning.important_details

    logger.info("Step 4/5 completed: final answer generated")

    # Step 5: Self-check result
    try:
        self_check = check_answer(
            text=text,
            important_details=meaning.important_details,
            final_answer=answer.final_answer,
            client=client,
        )
        result["self_check"] = self_check.model_dump()
    except ValueError as exc:
        logger.warning(
            "Self-check could not be validated: %s",
            exc,
        )
        result["self_check"] = {
            "is_valid": False,
            "contradictions": [],
            "missing_details": [],
            "error": "Self-check unavailable or invalid",
        }

    if not result["self_check"]["is_valid"]:
        logger.warning(
            "Pipeline completed with quality issues: %s",
            result["self_check"],
        )
    else:
        logger.info("Pipeline completed successfully: 5/5 steps")

    return result
