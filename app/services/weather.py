import os
from datetime import date
from model import WeatherResponseModel
import httpx
from services.cache import get_cache, set_cache
api_key= os.getenv("WEATHER_API_KEY")

async def fetch_weather(
        destination: str,
        start_date: date,
        end_date: date


)-> list[WeatherResponseModel]:
    api_key = os.getenv("WEATHER_API_KEY")

    cache_key = f"{destination}_{start_date}_{end_date}"   
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data


    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.weatherapi.com/v1/forecast.json",
            params={
                "key" : api_key,
                "q" : destination,
                "days": 14
            }
        )
        response.raise_for_status()
        data = response.json()

        forcasts = []

        days = [d for d in data["forecast"]["forecastday"]
            if start_date.isoformat() <= d["date"] <= end_date.isoformat()
        ]

        for day in days:
            forecast = WeatherResponseModel(
                destination= destination,
                date = day['date'],
                condition= day['day']['condition']['text'],
                temperature_high= day['day']['maxtemp_c'],
                temperature_low= day['day']['mintemp_c'],
                humidity= day['day']['avghumidity'],
                rain_chance= day['day']['daily_chance_of_rain']
                
            )

            forcasts.append(forecast)

        set_cache(cache_key, forcasts, ttl=3600)
        return forcasts