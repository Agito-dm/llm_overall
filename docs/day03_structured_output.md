# Day 03 – Structured Output and JSON Validation

## Goal

Implement structured LLM output with Pydantic validation
and error handling.

## Implementation

- Defined StructuredOutput with five required fields.
- Added strict validation using Pydantic 2.
- Implemented parse_structured_output().
- Added StructuredOutputError with error codes.
- Updated prompt variants A, B, and C.
- Integrated validation into run_pipeline().
- Added unit tests and real Gemini API examples.

## Output schema

1. summary – nonempty string.
2. category – question, problem, feedback, other.
3. sentiment – positive, negative, neutral, mixed.
4. key_points – exactly three nonempty strings.
5. final_answer – nonempty string.

Additional fields are forbidden.

## Error handling

- invalid_json – malformed JSON.
- missing_fields – required fields are missing.
- invalid_types – incompatible field types.
- invalid_schema – invalid values or constraints.

## Real API results

Model: Gemini (see outputs/day03_results.json)
Prompt: B (Constrained)

| Example | Category | Sentiment | Status |
|---|---|---|---|
| ml_learning | question | neutral | success |
| python_error | problem | negative | success |
| customer_feedback | feedback | mixed | success |
| positive_feedback | feedback | positive | success |
| general_information | other | positive | success |

Successful examples: 5/5.

## Tests

- Ruff lint: passed.
- Ruff format: passed.
- pytest: 18 passed.
- Gemini API: 5/5 successful examples.

## Conclusion

The pipeline produces structured JSON validated by
Pydantic. Invalid responses are rejected with explicit
error codes. All Day 3 requirements are implemented.

Word limits are specified in prompts but are not
enforced by the schema.
