from google.adk.agents import Agent

from multi_tool_agent.tools import say_hello

greeting_agent = Agent(
    name="greeting_agent",
    model="gemini-2.5-flash",
    description="Handles simple greetings and hellos using the 'say_hello' tool.",
    instruction=(
        "You are the Greeting Agent. Your ONLY task is to provide a friendly "
        "greeting using the 'say_hello' tool. If the user provides their name, "
        "pass it to the tool. Do not engage in any other conversation or tasks."
    ),
    tools=[say_hello],
)
