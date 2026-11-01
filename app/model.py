from pydantic import BaseModel, field_validator
from datetime import date
from typing import Optional

class TravelRequestModel(BaseModel):
    destination: str
    start_date: date
    end_date: date
    base_currency: str = "INR"

    @field_validator("destination")
    @classmethod
    def normalize_destination(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("base_currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.strip().upper()

class WeatherResponseModel(BaseModel):
    date: date
    destination: str
    condition: str
    temperature_high : float
    temperature_low : float
    humidity: float
    rain_chance : float

class PlaceofInterestModel(BaseModel):
    name: str
    description: str
    category : str
    rating : float
    estimated_time_hours: float
    entry_fee: Optional[float] = None
