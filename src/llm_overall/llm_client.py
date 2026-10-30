import logging
from time import perf_counter

from openai import OpenAI

from llm_overall.config import Settings

logger = logging.getLogger(__name__)


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
        logger.info("Sending request to model: %s", self._model)

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

        return content.strip()
