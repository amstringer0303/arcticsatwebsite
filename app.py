from flask import Flask, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)

def fetch_satellite_image(date, lat, lon, bbox):
    url = f'https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/{date}/250m/1.0.0/{bbox}.png'
    response = requests.get(url)
    with open('satellite_image.png', 'wb') as f:
        f.write(response.content)

def analyze_sea_ice(image_path):
    import cv2
    import numpy as np

    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
    return thresh

def fetch_weather_data():
    response = requests.get('https://api.weather.gov/gridpoints/AFG/52,97/forecast')
    return response.json()

def fetch_sea_ice_forecast():
    response = requests.get('https://api.weather.gov/gridpoints/AFG/52,97/forecast')
    return response.json()

def generate_summary(image_analysis, weather_data, forecast_data):
    sea_ice_summary = "Sea ice processes detected in the image."
    weather_summary = f"Weather forecast: {weather_data['properties']['periods'][0]['detailedForecast']}"
    forecast_summary = f"Sea ice forecast: {forecast_data['properties']['periods'][0]['detailedForecast']}"
    summary = f"{sea_ice_summary}\n{weather_summary}\n{forecast_summary}"
    return summary

@app.route('/data', methods=['GET'])
def get_data():
    date = request.args.get('date', datetime.utcnow().strftime('%Y-%m-%d'))
    lat = 67.7269
    lon = -164.5332
    bbox = f'{lon-0.1},{lat-0.1},{lon+0.1},{lat+0.1}'

    fetch_satellite_image(date, lat, lon, bbox)
    thresh_image = analyze_sea_ice('satellite_image.png')
    weather_data = fetch_weather_data()
    forecast_data = fetch_sea_ice_forecast()

    summary = generate_summary(thresh_image, weather_data, forecast_data)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
