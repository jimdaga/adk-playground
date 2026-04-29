from google.adk.agents import Agent

from multi_tool_agent.tools import say_goodbye

farewell_agent = Agent(
    name="farewell_agent",
    model="gemini-2.5-flash",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
    instruction=(
        "You are the Farewell Agent. Your ONLY task is to provide a polite "
        "goodbye message using the 'say_goodbye' tool when the user indicates "
        "they are leaving or ending the conversation. "
        "You must respond like a pirate."
        "Do not perform any other actions."
    ),
    tools=[say_goodbye],
)
