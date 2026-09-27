from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import sys
import hashlib
from flask_cors import CORS

# Ensure backend directory is on sys.path so local modules import reliably
sys.path.insert(0, os.path.dirname(__file__))

from helpers import c_to_f, heat_index, wind_chill, comfort_index, advice
from cache import get_cache, set_cache


def resolve_debug_mode() -> bool:
    """Avoid debug reloader in non-interactive terminals while still allowing debug mode."""
    value = os.environ.get("FLASK_DEBUG", "0").strip().lower()
    return value in {"1", "true", "yes", "on", "y"}


app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("OPENWEATHER_API_KEY", "4c90a22e3106aa423582d37bf8016ce9")


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def normalize_location(name: str) -> str:
    """Normalize user-provided city or state names."""
    if not name:
        return ""
    return name.strip()


def generate_demo_data(city: str):
    """Generate deterministic but unique demo data for a city or state based on its name hash."""
    # Create a deterministic hash-based seed from city/state name
    city_hash = int(hashlib.md5(city.lower().encode()).hexdigest(), 16)
    
    # Generate pseudo-random values based on city/state hash (but deterministic)
    temp_base = 15 + (city_hash % 20)  # 15-35°C   
    humidity = 35 + ((city_hash // 1000) % 50)  # 35-85%
    wind_speed = 2 + ((city_hash // 100000) % 8)  # 2-10 m/s
    pressure = 1000 + ((city_hash // 10000000) % 40)  # 1000-1040 hPa
    
    conditions = [
        "clear sky",
        "partly cloudy",
        "overcast",
        "light rain",
        "moderate rain",
        "cloudy with sunshine",
        "scattered clouds",
        "broken clouds"
    ]
    condition_idx = (city_hash // 1000000000) % len(conditions)
    condition = conditions[condition_idx]
    
    return {
        "temp": temp_base,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "pressure": pressure,
        "condition": condition
    }


@app.route("/")
def home():
    # Serve the frontend index.html from project root
    return send_from_directory(BASE_DIR, 'index.html')


@app.route("/weather", methods=["GET"]) 
def get_weather():
    city = normalize_location(request.args.get("city"))

    if not city:
        return jsonify({"error": "City/State is required"}), 400

    # decide whether to use live API or fallback demo data
    use_demo = API_KEY in (None, "", "YOUR_API_KEY_HERE")

    # check cache
    cache_key = f"weather:{city.lower()}"
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached)

    if not use_demo:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url, timeout=8)
            data = response.json()
            if response.status_code == 200:
                weather_data = {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "condition": data["weather"][0]["description"],
                    "wind_speed": data["wind"].get("speed", 0),
                    "demo": False
                }
                set_cache(f"weather:{city.lower()}", weather_data, ttl=180)
                return jsonify(weather_data)
            else:
                # If we have an API key but the API returns an error (eg. city not found),
                # forward the error to the client instead of falling back to demo data.
                print(f"OpenWeather error for {city}: {data}", flush=True)
                return jsonify({"error": data.get("message", "OpenWeather error")}), response.status_code
        except Exception as e:
            print(f"OpenWeather request failed: {e}", flush=True)
            return jsonify({"error": "OpenWeather request failed"}), 502

    # Demo/fallback data when API is missing or invalid
    if use_demo:
        demo_values = generate_demo_data(city)
        demo = {
            "city": city.title(),
            "country": "--",
            "temperature": demo_values["temp"],
            "feels_like": demo_values["temp"],
            "humidity": demo_values["humidity"],
            "pressure": demo_values["pressure"],
            "condition": demo_values["condition"] + " (demo)",
            "wind_speed_m_s": demo_values["wind_speed"],
            "demo": True
        }
        set_cache(f"weather:{city.lower()}", demo, ttl=180)
        return jsonify(demo)

    weather_data = {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "condition": data["weather"][0]["description"],
        "wind_speed": data["wind"].get("speed", 0),
        "demo": False
    }

    # cache short-term
    set_cache(f"weather:{city.lower()}", weather_data, ttl=180)

    return jsonify(weather_data)


@app.route("/weather/extended", methods=["GET"]) 
def get_weather_extended():

    city = normalize_location(request.args.get("city"))

    if not city:
        return jsonify({"error": "City/State is required"}), 400

    # decide whether to use live API or fallback demo data
    use_demo = API_KEY in (None, "", "YOUR_API_KEY_HERE")

    # check cache
    cache_key = f"weather_ext:{city.lower()}"
    cached = get_cache(cache_key)
    if cached:
        return jsonify(cached)
    if not use_demo:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        try:
            response = requests.get(url, timeout=8)
            data = response.json()
            if response.status_code == 200:
                temp = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"].get("speed", 0)
                condition = data["weather"][0]["description"]

                extended = {
                    "city": data["name"],
                    "country": data["sys"]["country"],
                    "temperature_c": temp,
                    "temperature_f": round(c_to_f(temp), 1),
                    "feels_like_c": data["main"]["feels_like"],
                    "feels_like_f": round(c_to_f(data["main"]["feels_like"]), 1),
                    "humidity": humidity,
                    "pressure": data["main"]["pressure"],
                    "condition": condition,
                    "wind_speed_m_s": wind_speed,
                    "wind_chill_c": round(wind_chill(temp, wind_speed), 1),
                    "heat_index_c": round(heat_index(temp, humidity), 1),
                    "comfort_index": comfort_index(temp, humidity),
                    "advice": advice(condition, temp, humidity, wind_speed),
                    "demo": False
                }
                set_cache(f"weather_ext:{city.lower()}", extended, ttl=180)
                return jsonify(extended)
            else:
                # Forward API errors (e.g., city not found) to client when API key is present
                print(f"OpenWeather error for {city}: {data}", flush=True)
                return jsonify({"error": data.get("message", "OpenWeather error")}), response.status_code
        except Exception as e:
            print(f"OpenWeather request failed: {e}", flush=True)
            return jsonify({"error": "OpenWeather request failed"}), 502

    if use_demo:
        demo_values = generate_demo_data(city)
        temp = demo_values["temp"]
        humidity = demo_values["humidity"]
        wind_speed = demo_values["wind_speed"]
        condition = demo_values["condition"] + " (demo)"
        extended = {
            "city": city.title(),
            "country": "--",
            "temperature_c": temp,
            "temperature_f": round(c_to_f(temp), 1),
            "feels_like_c": temp,
            "feels_like_f": round(c_to_f(temp), 1),
            "humidity": humidity,
            "pressure": demo_values["pressure"],
            "condition": condition,
            "wind_speed_m_s": wind_speed,
            "wind_chill_c": round(wind_chill(temp, wind_speed), 1),
            "heat_index_c": round(heat_index(temp, humidity), 1),
            "comfort_index": comfort_index(temp, humidity),
            "advice": advice(condition, temp, humidity, wind_speed),
            "demo": True
        }
        set_cache(f"weather_ext:{city.lower()}", extended, ttl=180)
        return jsonify(extended)


# Serve frontend assets from project root (placed after API routes so they aren't
@app.route("/api/forecast")
def get_forecast():
    city = normalize_location(request.args.get("city"))

    if not city:
        return jsonify({"error": "City/State is required"}), 400

    use_demo = API_KEY in (None, "", "YOUR_API_KEY_HERE")

    if use_demo:
        return jsonify({"error": "Weather API key is not configured"}), 500

    url = (
        f"http://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=8)
        data = response.json()

        if response.status_code != 200:
            print(f"OpenWeather forecast error for {city}: {data}", flush=True)
            return jsonify({
                "error": data.get("message", "OpenWeather forecast error")
            }), response.status_code

        forecast = []

        # OpenWeather gives forecast data every 3 hours.
        # Select one forecast around midday for each day.
        days = {}

        for item in data.get("list", []):
            date = item["dt_txt"].split(" ")[0]

            if date not in days:
                days[date] = item

            # Prefer the forecast around 12:00
            if "12:00:00" in item["dt_txt"]:
                days[date] = item

        for date, item in list(days.items())[:5]:
            forecast.append({
                "date": date,
                "temperature_c": round(item["main"]["temp"], 1),
                "feels_like_c": round(item["main"]["feels_like"], 1),
                "humidity": item["main"]["humidity"],
                "condition": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"],
                "wind_speed_m_s": item["wind"].get("speed", 0),
                "rain_chance": round(item.get("pop", 0) * 100)
            })

        return jsonify({
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecast": forecast,
            "demo": False
        })

    except Exception as e:
        print(f"Forecast request failed: {e}", flush=True)
        return jsonify({"error": "Forecast request failed"}), 502# shadowed by the catch-all path)
@app.route('/<path:filename>')
def static_files(filename):
    # Serve a small whitelist of frontend assets from project root
    if filename in ('index.html', 'style.css', 'script.js'):
        return send_from_directory(BASE_DIR, filename)
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = resolve_debug_mode()
    # Debug: print the API key as seen by the running process
    print("OPENWEATHER_API_KEY_ON_START:", API_KEY, flush=True)
    app.run(host=HOST, port=PORT, debug=DEBUG, use_reloader=False)