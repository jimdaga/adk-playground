from google.adk.agents import Agent

from diagnose_agent.tools import get_resources

discovery_agent = Agent(
    name="discovery_agent",
    model="gemini-2.5-flash",
    description=(
        "Performs broad resource discovery across Kubernetes namespaces. "
        "Lists pods, deployments, events, and other resources to map "
        "what is running and identify obvious anomalies."
    ),
    instruction=(
        "You are the Discovery Agent. Your task is to survey Kubernetes resources "
        "in a given namespace to map the landscape.\n\n"
        "Use the 'get_resources' tool to list resources by type. Start with pods "
        "and events, then check deployments or statefulsets as needed.\n\n"
        "Report what you find clearly: how many resources exist, which ones show "
        "anomalies (high restart counts, non-Ready status, Warning events), and "
        "which specific resources warrant deeper investigation.\n\n"
        "Do NOT diagnose root causes. Your job is discovery only — identify "
        "what looks abnormal and report it."
    ),
    tools=[get_resources],
)
