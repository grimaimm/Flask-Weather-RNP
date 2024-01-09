from flask import Flask, render_template, request, jsonify
from datetime import datetime
import threading
import requests
import time
# =========================================================
# // Inisiasi Flask App dan API Ke
app = Flask(__name__)
WHEATER_API_KEY = '5b38215163db47b298983112240501'
IPSTACK_API_KEY = '574c68acbf0ef45d1765a607356ea1cf'
# =========================================================

# =========================================================
# // Fungsi untuk mengonversi format tanggal ke hari
def format_date_to_day(date_string):
    date_obj = datetime.strptime(date_string, "%Y-%m-%d")
    return date_obj.strftime("%A")
# =========================================================

# =========================================================
# // Fungsi untuk mendapatkan data cuaca berdasarkan nama kota
def get_weather_data(city_name):
    weather_endpoint = f'http://api.weatherapi.com/v1/current.json?key={WHEATER_API_KEY}&q={city_name}'
    response = requests.get(weather_endpoint)

    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    return None
# =========================================================

# =========================================================
# // Fungsi untuk mendapatkan ramalan suhu selama satu minggu
def get_weekly_forecast(city_name, lang='en'):
    forecast_endpoint = f'http://api.weatherapi.com/v1/forecast.json?key={WHEATER_API_KEY}&q={city_name}&days=7&lang={lang}'
    response = requests.get(forecast_endpoint)

    if response.status_code == 200:
        forecast_data = response.json()
        for day in forecast_data['forecast']['forecastday']:
            day['formatted_date'] = format_date_to_day(day['date'])
        return forecast_data['forecast']['forecastday'][1:]
    return None
# =========================================================

# =========================================================
# // Fungsi untuk mendapatkan data cuaca dari WeatherAPI berdasarkan lokasi
def get_weather_data_by_location(latitude, longitude):
    base_url = f'http://api.weatherapi.com/v1/current.json?key={WHEATER_API_KEY}&q={latitude},{longitude}'
    response = requests.get(base_url)

    if response.status_code == 200:
        weather_data = response.json()
        return weather_data
    return None
# =========================================================

# =========================================================
# // Fungsi untuk mendapatkan lokasi pengguna berdasarkan alamat IP
def get_user_location():
    ipstack_endpoint = f'http://api.ipstack.com/check?access_key={IPSTACK_API_KEY}'
    response = requests.get(ipstack_endpoint)
    
    if response.status_code == 200:
        location_data = response.json()
        return location_data
    return None
# =========================================================

# =========================================================
# // Fungsi untuk memilih gambar berdasarkan waktu
def get_background_image(current_time):
    hour = int(current_time.split(':')[0])
    if 6 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 18:
        return 'afternoon'
    elif 18 <= hour < 24:
        return 'evening'
    else:
        return 'night'
# =========================================================

# =========================================================
# // Route Utama (Index)
@app.route('/')
def index():
    # Mendapatkan data lokasi pengguna secara otomatis
    user_location_data = get_user_location()
    
    if user_location_data:
        # Memanggil fungsi get_weather_data_by_location
        latitude = str(user_location_data['latitude'])
        longitude = str(user_location_data['longitude'])
        weather_data = get_weather_data_by_location(latitude, longitude)

        # Menyiapkan data cuaca untuk ditampilkan di halaman index
        city = weather_data['location']['name']
        region = weather_data['location']['region']
        country = weather_data['location']['country']
        description = weather_data['current']['condition']['text']
        temperature = weather_data['current']['temp_c']
        humidity = weather_data['current']['humidity']
        wind_speed = weather_data['current']['wind_kph']
        precip_mm = weather_data['current']['precip_mm']
        icon_url = weather_data['current']['condition']['icon']

        current_day = datetime.now().strftime("%A, %d %B %Y")
        current_time = datetime.now().strftime("%H:%M")

        # Memanggil fungsi get_weekly_forecast
        weekly_forecast = get_weekly_forecast(city)

        # Memanggil fungsi get_background_image
        time_of_day = get_background_image(current_time)

        return render_template('index.html',
            city=city, region=region, country=country, description=description, temperature=temperature, 
            humidity=humidity, wind_speed=wind_speed, precip_mm=precip_mm, current_day=current_day,
            current_time=current_time, time_of_day=time_of_day, icon_url=icon_url, weekly_forecast=weekly_forecast)
    else:
        # Menangani jika gagal mendapatkan lokasi pengguna
        error_message = 'Failed to get user location.'
        return render_template('error.html', error=error_message)
# =========================================================

# =========================================================
# // Route Prediksi (Result)
@app.route('/predict', methods=['POST'])
def predict():
    city_name = request.form['city']
    # memanggil fungsi get_weather_data
    weather_data = get_weather_data(city_name)

    if weather_data:
        # Menyiapkan data cuaca untuk ditampilkan di halaman result
        city = weather_data['location']['name']
        region = weather_data['location']['region']
        country = weather_data['location']['country']
        description = weather_data['current']['condition']['text']
        temperature = weather_data['current']['temp_c']
        humidity = weather_data['current']['humidity']
        wind_speed = weather_data['current']['wind_kph']
        precip_mm = weather_data['current']['precip_mm']
        icon_url = weather_data['current']['condition']['icon']
        local_time_str = weather_data['location']['localtime']

        local_time = datetime.now().strptime(local_time_str, "%Y-%m-%d %H:%M")
        formatted_day = local_time.strftime("%A, %d %B %Y")
        formatted_time = local_time.strftime("%H:%M")

        # Memanggil fungsi get_weekly_forecast
        weekly_forecast = get_weekly_forecast(city)

        # Memanggil fungsi get_background_image
        time_of_day = get_background_image(formatted_time)

        return render_template('result.html', 
            city=city, region=region, country=country, description=description, temperature=temperature, 
            humidity=humidity, wind_speed=wind_speed, precip_mm=precip_mm, formatted_day=formatted_day, 
            formatted_time=formatted_time, time_of_day=time_of_day, icon_url=icon_url, weekly_forecast=weekly_forecast)
    else:
        # Menangani jika gagal mendapatkan lokasi
        error_message = f'Failed to get weather data for {city_name}.'
        return render_template('error.html', error=error_message)
# =========================================================

# =========================================================
# // Menjalankan Flask App
if __name__ == '__main__':
    app.run(debug=True)
# =========================================================