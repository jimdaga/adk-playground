from google.adk.tools.tool_context import ToolContext


def get_weather(city: str, tool_context: ToolContext) -> dict:
    """Retrieves the current weather report for a specified city.

    Reads the user's preferred temperature unit from session state
    and formats the report accordingly (Celsius or Fahrenheit).

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").
        tool_context (ToolContext): Provided by ADK, gives access to session state.

    Returns:
        dict: A dictionary with 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    preferred_unit = tool_context.state.get(
        "user_preference_temperature_unit", "Celsius"
    )

    city_normalized = city.lower().replace(" ", "")

    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized not in mock_weather_db:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have weather information for '{city}'.",
        }

    data = mock_weather_db[city_normalized]
    temp_c = data["temp_c"]
    condition = data["condition"]

    if preferred_unit == "Fahrenheit":
        temp_value = (temp_c * 9 / 5) + 32
        temp_unit = "°F"
    else:
        temp_value = temp_c
        temp_unit = "°C"

    report = (
        f"The weather in {city.capitalize()} is {condition} "
        f"with a temperature of {temp_value:.0f}{temp_unit}."
    )

    tool_context.state["last_city_checked_stateful"] = city

    return {"status": "success", "report": report}
