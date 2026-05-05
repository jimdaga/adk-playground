from google.adk.agents import Agent

from diagnose_agent.tools import query_history

correlation_agent = Agent(
    name="correlation_agent",
    model="gemini-2.5-flash",
    description=(
        "Searches the diagnostic data lake for historical findings "
        "related to a cluster or namespace. Identifies recurring patterns, "
        "prior root causes, and whether this is a known issue."
    ),
    instruction=(
        "You are the Correlation Agent. Your task is to check whether "
        "the current issue has occurred before by querying historical "
        "diagnostic findings.\n\n"
        "Use the 'query_history' tool to search for past findings. "
        "Filter by cluster_id or namespace when available.\n\n"
        "Report what you find:\n"
        "- Has this exact issue occurred before? How many times?\n"
        "- What were the prior root causes and resolutions?\n"
        "- Is there a pattern (e.g., recurring weekly, after deployments)?\n"
        "- Were prior recommendations followed?\n\n"
        "Be specific about dates and findings. If no history exists, "
        "say so clearly."
    ),
    tools=[query_history],
)
