import asyncio
import logging
from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

log = logging.getLogger(__name__)

MAX_RETRIES = 3
BACKOFF_SECONDS = [15, 30, 60]


async def rate_limit_handler(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
    error: Exception,
) -> Optional[LlmResponse]:
    """Handle 429 rate limit errors with exponential backoff.

    Retries the model call up to MAX_RETRIES times with increasing
    delays. If all retries fail, returns a graceful error message
    instead of crashing the invocation.
    """
    error_str = str(error)
    if "429" not in error_str and "RESOURCE_EXHAUSTED" not in error_str:
        return None

    retry_count = callback_context.state.get("temp:rate_limit_retries", 0)

    if retry_count >= MAX_RETRIES:
        log.warning("Rate limit: max retries (%d) exceeded. Returning error.", MAX_RETRIES)
        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=(
                    "I'm being rate limited by the AI service and have exhausted "
                    "my retries. Please try again in a few minutes."
                ))],
            )
        )

    delay = BACKOFF_SECONDS[min(retry_count, len(BACKOFF_SECONDS) - 1)]
    log.info("Rate limit hit. Retrying in %ds (attempt %d/%d).", delay, retry_count + 1, MAX_RETRIES)

    callback_context.state["temp:rate_limit_retries"] = retry_count + 1

    await asyncio.sleep(delay)

    return None
