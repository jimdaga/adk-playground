from typing import Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

MIN_ITERATIONS_FOR_CONCLUSION = 3


def budget_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Tracks investigation depth and rejects premature conclusions.

    Increments an iteration counter in session state each time the model
    is called. If the model's previous response attempted to call
    conclude_diagnosis before the minimum iteration threshold, this
    callback blocks the call and nudges the model to investigate further.
    """
    count = callback_context.state.get("iteration_count", 0) + 1
    callback_context.state["iteration_count"] = count

    if count <= MIN_ITERATIONS_FOR_CONCLUSION:
        last_model_text = ""
        if llm_request.contents:
            for content in reversed(llm_request.contents):
                if content.role == "model" and content.parts:
                    for part in content.parts:
                        if hasattr(part, "function_call") and part.function_call:
                            if part.function_call.name == "conclude_diagnosis":
                                return LlmResponse(
                                    content=types.Content(
                                        role="model",
                                        parts=[types.Part(text=(
                                            f"Investigation is only at iteration {count}. "
                                            f"You need at least {MIN_ITERATIONS_FOR_CONCLUSION} "
                                            "rounds of evidence gathering before concluding. "
                                            "Use your diagnostic tools to gather more evidence."
                                        ))],
                                    )
                                )
                    break

    return None
