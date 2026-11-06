import json
import logging

from pydantic import ValidationError

from llm_overall.classification.classifier import (
    ClassificationClient,
    classify_text,
)
from llm_overall.classification.routing import get_route
from llm_overall.models.routed_output import RoutedOutput
from llm_overall.prompts.generation_prompt import (
    build_generation_prompts,
)

logger = logging.getLogger(__name__)
OPTIONAL_GENERATED_FIELDS = frozenset({"intent", "detected_intent", "additional_data"})


def run_routed_pipeline(
    text: str,
    client: ClassificationClient,
) -> dict[str, object]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Input text must not be empty")

    classification = classify_text(text, client)

    route_instruction = get_route(classification.category)

    logger.info(
        "Selected route: %s",
        classification.category.value,
    )

    system_prompt, user_prompt = build_generation_prompts(
        text=text,
        category=classification.category,
        intent=classification.intent,
        route_instruction=route_instruction,
    )

    raw_response = client.complete(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
    )

    try:
        response_data = json.loads(raw_response)

        if not isinstance(response_data, dict):
            raise TypeError("Generated JSON must be an object")

        extra_fields = set(response_data) - set(RoutedOutput.model_fields)

        if extra_fields:
            if not extra_fields <= OPTIONAL_GENERATED_FIELDS:
                raise ValueError(f"Unexpected output fields: {sorted(extra_fields)}")

            logger.warning(
                "Removing redundant generated fields: %s",
                sorted(extra_fields),
            )

            for field in extra_fields:
                response_data.pop(field)

        generated = RoutedOutput.model_validate_json(
            json.dumps(response_data, ensure_ascii=False)
        )

    except (TypeError, ValueError, ValidationError) as exc:
        logger.error("Routed output validation failed: %s", exc)
        raise ValueError("LLM returned an invalid routed response") from exc

    if generated.category != classification.category:
        raise ValueError("Generated category does not match classification")

    result = generated.model_dump(mode="json")
    result["intent"] = classification.intent

    logger.info("Routed pipeline completed successfully")

    return result
