from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from .forms import Weather
from geopy.geocoders import Photon
from django.urls import reverse
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
# Create your views here.

def get_coordinates(city_name):
    geolocator = Photon(user_agent="geoapiExercises")
    location = geolocator.geocode(city_name)
    if location:
        return {'latitude': location.latitude, 'longitude': location.longitude}
    else:
        return "Город не найден"
def index(request):
    forms = Weather(request.POST)  # Заполнена значениями, которые пришли из post запроса.
    if request.method == "POST":
        if forms.is_valid():
            cordinate = get_coordinates(forms.cleaned_data['city'])
            if cordinate == 'Город не найден':
                context = {'errors': forms.cleaned_data['city']}
                return render(request=request, template_name='weather_apps/errors.html', context=context)
            else:
                redirect_weather = reverse('weather', kwargs=cordinate)
                return HttpResponseRedirect(redirect_weather)
    else:
        forms = Weather() #Не заполнена значениями, которые пришли с get запроса
    return render(request=request, template_name='weather_apps/base.html', context={'form': forms})


def weather(request, latitude, longitude):
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        'latitude' : latitude,
        'longitude' : longitude,
        'hourly': ["temperature_2m", "precipitation_probability"],
        "forecast_days": 1
    }

    responses = openmeteo.weather_api(url, params=params)
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability
    hourly_dataframe = pd.DataFrame(data=hourly_data)
    weathers = hourly_dataframe.values.tolist()
    context = {'weathers': weathers}
    return render(request=request, template_name='weather_apps/weather_page.html', context= context)
