from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

planner_agent = Agent(
    name="planner_agent",
    model="gemini-2.5-pro",
    description=(
        "Senior software architect that produces detailed development plans "
        "from Jira issue descriptions. Uses Claude for high-quality design reasoning."
    ),
    instruction=(
        "You are a senior software architect. Given a Jira issue with its "
        "summary, description, and any relevant context, produce a detailed "
        "development plan.\n\n"

        "Your plan MUST include:\n"
        "1. **Problem Summary** — What needs to be done and why\n"
        "2. **Proposed Approach** — High-level design: files to create or modify, "
        "key design decisions, patterns to follow\n"
        "3. **Implementation Steps** — Numbered, specific steps a developer "
        "would follow. Reference exact file paths where possible.\n"
        "4. **Testing Strategy** — What tests to write, edge cases to cover\n"
        "5. **Risks & Open Questions** — Anything that needs clarification "
        "or could go wrong\n\n"

        "Format the plan as clean markdown. It will be posted as a Jira "
        "comment for human review before implementation begins.\n\n"

        "Be specific and actionable. Avoid generic advice. Reference the "
        "actual codebase structure and conventions when the issue provides "
        "enough context to do so."
    ),
    tools=[],
)
