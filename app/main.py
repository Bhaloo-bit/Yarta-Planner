from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from routes.planner import router as planner_router



# routes/planner.py
from services.weather import fetch_weather

# services/weather.py
from services.cache import get_cache, set_cache
from routes.stream import router as streaming_router

app = FastAPI(
    title="Yatra Planner API", 
    description="Aggregates data from multiple sources to provide singal plan with SSE support.", 
    version="1.0.0"
)

@app.get("/")
async def root():
    return {
        "app": "Yatra Planner API",
        "version": "1.0.0",
        "endpoints": {
            "/plan": "POST - Create a travel plan (Aggregated)",
            "/plan/stream": "GET - Stream a travel plan (SSE)",
            "/plan/cache-stats": "GET -View cache statistics for the travel plan",
            "/DELETE /plan/cache": "DELETE - Clear the travel plan"

        }
    }

app.include_router(planner_router)
app.include_router(streaming_router)