from fastapi import APIRouter, HTTPException
from model import TravelRequestModel
from fastapi.responses import StreamingResponse
import json
from services.currency import fetch_currency_rates
from services.weather import fetch_weather
from services.places import fetch_palces
from pydantic import BaseModel

router = APIRouter(
    prefix="/stream",
    tags=["Streaming"]
)
def _default(o):
    if isinstance(o, BaseModel):
        return o.model_dump(mode="json")
    raise TypeError(f"Not serializable: {type(o).__name__}")

def format_sse(data: dict, event: str | None = None) -> str:
    json_data = json.dumps(data, default=_default)
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {json_data}\n\n"

async def stream_generator(travel_request: TravelRequestModel):
     yield format_sse({"message": "Starting travel plan aggregation..."}, event = "start")
     yield format_sse({"message": "Fetching weathet data.."}, event="weather")
     weather_data = await fetch_weather(
          destination= travel_request.destination,
          start_date=travel_request.start_date,
          end_date=travel_request.end_date
     )
     yield format_sse({"weather_data":weather_data}, event = "weathe_complete")
     yield format_sse({"message":"fetching travel options..,"}, event ="options")
     places_data = await fetch_palces(travel_request.destination)
     yield format_sse({"places_data":places_data}, event = "Options_complete")

     yield format_sse({"message":"fetching currecncy data..."}, event= "currency")
     currency_data = await fetch_currency_rates(travel_request.base_currency)
     yield format_sse({"currency_data":currency_data}, event="currency_complete")
     yield format_sse({"message":"Travel plan aggregation complete"}, event="complete")

@router.post("/plan", response_class= StreamingResponse)
async def stream_travel_plan(travel_request: TravelRequestModel):

    """ Stream Weather, Currency, and places date in real-time based on the travel request"""
    if travel_request.start_date > travel_request.end_date:
            raise HTTPException(
                status_code= 400,
                detail= "start date cannot be after end date"
            )
    
    trip_days = (travel_request.end_date - travel_request.start_date).days
    
    if trip_days < 1:
        raise HTTPException(
            status_code=400,
            detail="Travel plan must be at least 1 day long"
        )
    
    if trip_days > 14:
        raise HTTPException(
            status_code=400,
            detail= "Travel Plan cannot be longer than 14 days"
        )

    return StreamingResponse(
         stream_generator(travel_request),
         media_type="text/event-stream",
         headers={"Cache-Control":"no-cache", "Connection":"keep-alive"}
    )