from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

planner_agent = Agent(
    name="planner_agent",
    model="gemini-2.5-pro",
    description=(
        "Senior software architect that produces detailed development plans. "
        "Give it an issue key, summary, description, and any research context. "
        "Returns a structured plan with implementation steps."
    ),
    instruction=(
        "You are a senior software architect. Given a Jira issue and optional "
        "research context, produce a detailed development plan.\n\n"
        "Output ONLY the plan content — no introductory sentences, "
        "no preamble like 'Here is a plan for...', no sign-offs. "
        "Start directly with the first section heading.\n\n"
        "Include these sections:\n"
        "1. Problem Summary — What needs to be done and why\n"
        "2. Proposed Approach — Files to create or modify, key design decisions\n"
        "3. Implementation Steps — Numbered, specific steps\n"
        "4. Testing Strategy — What tests to write, edge cases to cover\n"
        "5. Risks & Open Questions — Anything that needs clarification\n\n"
        "Be specific and actionable. Reference exact file paths, function names, "
        "and configuration values when the context provides enough detail."
    ),
    tools=[],
    output_key="last_plan",
)

planner_tool = AgentTool(agent=planner_agent)
