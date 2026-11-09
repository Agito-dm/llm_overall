import logging
from time import perf_counter, sleep

from openai import APIConnectionError, APIStatusError, OpenAI

from llm_overall.config import Settings

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 3
RETRY_BASE_DELAY = 1.0
RETRYABLE_STATUS_CODES = {408, 409, 429}


def is_retryable_error(error: Exception) -> bool:
    if isinstance(error, APIConnectionError):
        return True

    if isinstance(error, APIStatusError):
        return error.status_code in RETRYABLE_STATUS_CODES or error.status_code >= 500

    return False


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        client_options = {
            "api_key": settings.api_key,
            "timeout": 60.0,
            "max_retries": 0,
        }

        if settings.base_url:
            client_options["base_url"] = settings.base_url

        self._client = OpenAI(**client_options)
        self._model = settings.model

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            logger.info(
                "Sending request to model=%s, attempt=%d/%d",
                self._model,
                attempt,
                MAX_ATTEMPTS,
            )

            start_time = perf_counter()

            try:
                completion = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": user_prompt,
                        },
                    ],
                )

            except (APIConnectionError, APIStatusError) as exc:
                retryable = is_retryable_error(exc)

                logger.warning(
                    "LLM API error: type=%s, attempt=%d/%d, retryable=%s",
                    type(exc).__name__,
                    attempt,
                    MAX_ATTEMPTS,
                    retryable,
                )

                if not retryable or attempt == MAX_ATTEMPTS:
                    logger.error("LLM request failed without further retries")
                    raise

                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                logger.info("Retrying LLM request in %.1f seconds", delay)
                sleep(delay)
                continue

            finally:
                elapsed = perf_counter() - start_time
                logger.info("LLM request time: %.2f seconds", elapsed)

            if completion.usage is not None:
                logger.info(
                    "Tokens: input=%s, output=%s",
                    completion.usage.prompt_tokens,
                    completion.usage.completion_tokens,
                )

            if not completion.choices:
                raise ValueError("LLM returned no choices")

            content = completion.choices[0].message.content

            if not content or not content.strip():
                raise ValueError("LLM returned an empty response")

            logger.info("LLM request succeeded on attempt %d", attempt)
            return content.strip()

        raise RuntimeError("Unexpected retry loop termination")
