from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from ..callbacks import rate_limit_handler

research_agent = Agent(
    name="research_agent",
    model="gemini-2.5-flash",
    description=(
        "Searches the web for technical documentation, API references, "
        "library guides, and code examples relevant to a development task. "
        "Call this before planning to gather context."
    ),
    instruction=(
        "You are a technical researcher. Given a topic or question about "
        "a development task, search the web for relevant information.\n\n"
        "Focus on:\n"
        "- Official documentation for libraries, APIs, and frameworks\n"
        "- Code examples and best practices\n"
        "- Known issues, migration guides, or breaking changes\n"
        "- Architecture patterns relevant to the task\n\n"
        "Return a concise summary of your findings organized by relevance. "
        "Include specific details like function names, configuration options, "
        "and version requirements — not vague overviews.\n\n"
        "Do NOT make up information. If you can't find something, say so."
    ),
    tools=[google_search],
    on_model_error_callback=rate_limit_handler,
)

research_tool = AgentTool(agent=research_agent)
