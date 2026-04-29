from google.adk.agents import Agent

from multi_tool_agent.tools import get_weather, get_current_time
from multi_tool_agent.sub_agents import greeting_agent, farewell_agent

root_agent = Agent(
    name="weather_agent_team",
    model="gemini-2.5-flash",
    description=(
        "Main coordinator agent. Provides weather information (state-aware "
        "temperature units) and current time, delegates greetings and "
        "farewells to specialist sub-agents."
    ),
    instruction=(
        "You are the main Weather Agent coordinating a team. "
        "Your primary responsibility is to provide weather and time information. "
        "Use the 'get_weather' tool for weather requests. "
        "The tool formats temperature based on user preference stored in state. "
        "Use the 'get_current_time' tool for time requests. "
        "You have specialized sub-agents: "
        "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. "
        "Delegate to it for these. "
        "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. "
        "Delegate to it for these. "
        "Analyze the user's query. If it's a greeting, delegate to "
        "'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
        "If it's a weather or time request, handle it yourself. "
        "For anything else, respond appropriately or state you cannot handle it."
    ),
    tools=[get_weather, get_current_time],
    sub_agents=[greeting_agent, farewell_agent],
    output_key="last_weather_report",
)
