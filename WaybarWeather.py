#!/usr/bin/env python3
import requests
import json


try:
    url = "http://wttr.in/Raleigh?format=j1"
    response = requests.get(url, timeout=5)
    response.raise_for_status()

    weather_data = response.json()

    temp = weather_data["current_condition"][0]["temp_F"]
    condition = weather_data["current_condition"][0]["weatherDesc"][0]["value"]

    # Icons mapping based on weather description
    icons = {

        "Clear": "", "Sunny": "",
        "Partly cloudy": "",
        "Cloudy": "", "Overcast": "",
        "Patchy rain possible": "",
        "Light rain": "", "Showers": "", "Moderate rain": "",
        "Heavy rain": "", "Torrential rain": "",
        "Mist": "", "Fog": "",
        "Patchy snow possible": "", "Light snow": "",
        "Moderate snow": "", "Heavy snow": "",
        "Thunderstorm": "", "Drizzle": ""
    }

    # Default icon if unknown condition
    icon = icons.get(condition, "")

    # Output to Waybar as JSON
    print(json.dumps({
        "text": f"{icon} {temp}°F",
        "tooltip": condition,
        "class": condition.lower().replace(" ", "-")
    }))

except Exception as e:
    # Return valid JSON even on failure
    print(json.dumps({
        "temp": "N/A",
        "condition": "Unavailable",
        "icon": ""
    }))

