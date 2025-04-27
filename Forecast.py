# Forecast.py
import requests
import json
import os
from datetime import datetime
from collections import defaultdict
from setup import API_KEY

# === CONFIG ===
LAT = 35.7796
LON = -78.6382
SAVE_PATH_JSON = "./weather_data/openweather_5day_summary.json"
SAVE_PATH_MD = "./weather_data/openweather_5day_summary.md"
SAVE_PATH_HTML = "./weather_data/openweather_5day_summary.html"
SPLIT_DIR = "./weather_data/split_days"

# === Fetch 5-day forecast ===
def fetch_openweather_5day():
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={LAT}&lon={LON}&units=imperial&appid={API_KEY}"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

# === Build daily summary line ===
def get_icon(desc, pop, humidity, wind, clouds):
    desc_lower = desc.lower()
    if "thunder" in desc_lower:
        icon = ""
    elif "snow" in desc_lower:
        icon = ""
    elif "rain" in desc_lower:
        icon = ""
    elif "cloud" in desc_lower:
        icon = "" if "overcast" in desc_lower else ""
    elif "clear" in desc_lower:
        icon = ""
    else:
        icon = ""

    mods = []
    if pop >= 70:
        mods.append("")
    if humidity >= 80:
        mods.append("")
    if wind >= 15:
        mods.append("")
    if clouds >= 80:
        mods.append("")

    return f"{icon} {' '.join(mods)}"

def generate_summary(desc, pop, humidity, wind, clouds):
    summary = []
    summary.append(get_icon(desc, pop, humidity, wind, clouds))
    summary.append(desc.capitalize())

    if pop >= 70:
        summary.append("• likely rain")
    elif 30 < pop < 70:
        summary.append("• chance of showers")
    elif 10 < pop <= 30:
        summary.append("• slight chance")

    if humidity >= 80:
        summary.append("• humid")
    elif humidity <= 30:
        summary.append("• dry")

    if wind >= 15:
        summary.append("• windy")
    elif wind <= 5:
        summary.append("• calm")

    if clouds >= 80:
        summary.append("• overcast")
    elif clouds <= 20:
        summary.append("• mostly clear")

    return " ".join(summary)

# === Process forecast ===
def process_forecast(data):
    daily_data = defaultdict(lambda: {
        "temps": [],
        "weather": [],
        "pop": [],
        "humidity": [],
        "wind": [],
        "clouds": [],
    })

    for entry in data.get("list", []):
        date = entry["dt_txt"].split()[0]
        daily_data[date]["temps"].append(entry["main"]["temp"])
        daily_data[date]["pop"].append(entry.get("pop", 0) * 100)
        daily_data[date]["humidity"].append(entry["main"]["humidity"])
        daily_data[date]["wind"].append(entry["wind"]["speed"])
        daily_data[date]["clouds"].append(entry["clouds"]["all"])
        daily_data[date]["weather"].append(entry["weather"][0]["description"])

    simplified = []
    for date, values in daily_data.items():
        temps = values["temps"]
        pop = round(sum(values["pop"]) / len(values["pop"]), 1)
        humidity = round(sum(values["humidity"]) / len(values["humidity"]), 1)
        wind = round(sum(values["wind"]) / len(values["wind"]), 1)
        clouds = round(sum(values["clouds"]) / len(values["clouds"]), 1)

        weather_counts = defaultdict(int)
        for desc in values["weather"]:
            weather_counts[desc] += 1
        common_weather = max(weather_counts, key=weather_counts.get)

        summary_line = generate_summary(common_weather, pop, humidity, wind, clouds)
        weekday = datetime.strptime(date, "%Y-%m-%d").strftime("%a")

        summary = {
            "date": date,
            "weekday": weekday,
            "temp_min": round(min(temps), 1),
            "temp_max": round(max(temps), 1),
            "weather": common_weather,
            "avg_precip_prob_%": pop,
            "avg_humidity_%": humidity,
            "avg_wind_mph": wind,
            "avg_cloudiness_%": clouds,
            "summary": summary_line
        }
        simplified.append(summary)

    return simplified

# === Save JSON, Markdown, and HTML ===
def save_forecast(data):
    os.makedirs(os.path.dirname(SAVE_PATH_JSON), exist_ok=True)
    os.makedirs(SPLIT_DIR, exist_ok=True)

    with open(SAVE_PATH_JSON, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[✓] Forecast saved to {SAVE_PATH_JSON}")

    md_lines = ["# 5-Day Weather Forecast\n"]
    html_lines = ["<html><body><h1>5-Day Weather Forecast</h1>"]

    for day in data:
        md = [
            f"**{day['weekday']} {day['date']}**  ",
            f"{day['temp_min']}°F / {day['temp_max']}°F  ",
            f"{day['summary']}  ",
            f"Precip: {day['avg_precip_prob_%']}%  ",
            f"Humidity: {day['avg_humidity_%']}%  ",
            f"Wind: {day['avg_wind_mph']} mph  ",
            f"Clouds: {day['avg_cloudiness_%']}%  "
        ]
        md_lines.extend(md + ["\n"])

        html = f"""
        <div>
            <h2>{day['weekday']} {day['date']}</h2>
            <p><strong>{day['temp_min']}°F / {day['temp_max']}°F</strong></p>
            <p>{day['summary']}</p>
            <ul>
                <li>Precip: {day['avg_precip_prob_%']}%</li>
                <li>Humidity: {day['avg_humidity_%']}%</li>
                <li>Wind: {day['avg_wind_mph']} mph</li>
                <li>Clouds: {day['avg_cloudiness_%']}%</li>
            </ul>
        </div>
        """
        html_lines.append(html)

        split_path = os.path.join(SPLIT_DIR, f"{day['date']}.json")
        with open(split_path, "w") as sf:
            json.dump(day, sf, indent=2)

    html_lines.append("</body></html>")

    with open(SAVE_PATH_MD, "w") as f:
        f.write("\n".join(md_lines))
    print(f"[✓] Markdown forecast saved to {SAVE_PATH_MD}")

    with open(SAVE_PATH_HTML, "w") as f:
        f.write("\n".join(html_lines))
    print(f"[✓] HTML forecast saved to {SAVE_PATH_HTML}")

# === Print summary ===
def print_forecast(data):
    print("\n📅 5-Day Forecast:")
    for day in data:
        print(f"{day['weekday']} {day['date']} — {day['temp_min']}°F / {day['temp_max']}°F")
        print(f"   {day['summary']}. Precip: {day['avg_precip_prob_%']}%, "
              f"Humidity: {day['avg_humidity_%']}%, Wind: {day['avg_wind_mph']} mph, Clouds: {day['avg_cloudiness_%']}%")
        print()

# === Run it ===
if __name__ == "__main__":
    raw = fetch_openweather_5day()
    forecast = process_forecast(raw)
    save_forecast(forecast)
    print_forecast(forecast)
