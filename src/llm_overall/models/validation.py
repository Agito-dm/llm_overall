from pydantic import ValidationError

from llm_overall.models.schemas import StructuredOutput


class StructuredOutputError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


def parse_structured_output(raw_response: str) -> dict[str, object]:
    try:
        result = StructuredOutput.model_validate_json(raw_response)
    except ValidationError as exc:
        errors = exc.errors()
        error_types = {error["type"] for error in errors}

        if "json_invalid" in error_types:
            raise StructuredOutputError(
                "invalid_json", "LLM returned invalid JSON"
            ) from exc

        if "model_type" in error_types:
            raise StructuredOutputError(
                "invalid_types", "LLM output must be a JSON object"
            ) from exc

        missing_fields = [
            str(error["loc"][0]) for error in errors if error["type"] == "missing"
        ]
        if missing_fields:
            raise StructuredOutputError(
                "missing_fields",
                "Missing required fields: " + ", ".join(missing_fields),
            ) from exc

        if error_types & {"string_type", "list_type"}:
            raise StructuredOutputError(
                "invalid_types", "LLM returned fields with invalid types"
            ) from exc

        raise StructuredOutputError(
            "invalid_schema", "LLM returned data that violates the schema"
        ) from exc

    return result.model_dump()
