from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


def get_coordinates(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if "results" in data:
        location = data["results"][0]
        return {
            "name": location["name"],
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "country": location.get("country")
        }
    return None


@app.route("/api/get-weather", methods=["GET"])
def get_weather():
    location_str = request.args.get("location")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    location_dict = get_coordinates(location_str)
    if not location_dict:
        return jsonify({"error": "Location not found"}), 404

    params = {
        "latitude": location_dict["latitude"],
        "longitude": location_dict["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max",
                   "temperature_2m_min",
                   "precipitation_sum",
                   "windspeed_10m_max"],
        "temperature_unit": "celsius",
        "windspeed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": "auto"
    }
    response = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params)
    data = response.json()
    
    # Build list of daily data
    daily_data = []
    for i in range(len(data["daily"]["time"])):
        daily_data.append({
            "date": data["daily"]["time"][i],
            "max_temperature": data["daily"]["temperature_2m_max"][i],
            "min_temperature": data["daily"]["temperature_2m_min"][i],
            "precipitation": data["daily"]["precipitation_sum"][i],
            "windspeed": data["daily"]["windspeed_10m_max"][i]
        })
    
    return jsonify({"location": location_dict["name"],
                    "data": daily_data})


@app.route("/api/get-weather-forecast", methods=["GET"])
def get_weather_forecast():
    location_str = request.args.get("location")
    location_dict = get_coordinates(location_str)
    if not location_dict:
        return jsonify({"error": "Location not found"}), 404

    params = {
        "latitude": location_dict["latitude"],
        "longitude": location_dict["longitude"],
        "daily": ["temperature_2m_max",
                   "temperature_2m_min",
                   "precipitation_sum",
                   "windspeed_10m_max"],
        "temperature_unit": "celsius",
        "windspeed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": "auto"
    }
    response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    data = response.json()
    
    # Build list of daily data
    daily_data = []
    for i in range(len(data["daily"]["time"])):
        daily_data.append({
            "date": data["daily"]["time"][i],
            "max_temperature": data["daily"]["temperature_2m_max"][i],
            "min_temperature": data["daily"]["temperature_2m_min"][i],
            "precipitation": data["daily"]["precipitation_sum"][i],
            "windspeed": data["daily"]["windspeed_10m_max"][i]
        })
    
    return jsonify({"location": location_dict["name"],
                    "data": daily_data})


if __name__ == "__main__":
    app.run(debug=True)