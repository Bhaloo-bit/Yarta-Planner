# 🧭 Yatra Planner

Weather, places and currency in one trip plan.

Enter a destination, dates and a budget. Yatra Planner returns a day-by-day weather forecast, top places to visit, and your budget converted into other currencies. Results can be streamed live.

## Features

- **Weather:** daily forecast for your travel dates (high/low, condition, humidity, cloud cover)
- **Places:** top attractions with category, rating, suggested time and description
- **Currency:** convert your budget into USD, EUR, GBP, AED and more
- **Live stream:** results appear section by section as they are ready

## Tech Stack

- Python
- FastAPI + Uvicorn (backend, streaming endpoint)
- httpx (async API calls)
- WeatherAPI (forecast)
- Currency exchange API (rates)

## Project Structure

```
yatra_agent/
├── app/
│   ├── routes/
│   │   └── stream.py      # streaming endpoint
│   └── services/
│       └── weather.py     # WeatherAPI client
├── .env                   # API keys (not committed)
├── requirements.txt
└── README.md
```

## Setup

1. Clone the repo and enter the folder:
   ```bash
   cd yatra_agent
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root:
   ```dotenv
   WEATHERAPI_API_KEY=your_weatherapi_key
   CURRENCY_API_KEY=your_currency_api_key
   ```
5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Keys

| Variable | Get it from |
|---|---|
| `WEATHERAPI_API_KEY` | https://www.weatherapi.com |
| `CURRENCY_API_KEY` | your currency API provider |

Never commit `.env`. Add it to `.gitignore`.

## Notes

- WeatherAPI's free plan limits `forecast.json` to **3 days** of forecast. Longer ranges need a paid plan.
- A `403 Forbidden` from the weather service usually means the API key is empty or not loaded. Check the `.env` variable name and that `load_dotenv()` runs first.

## Usage

1. Enter a destination (e.g. `mumbai`).
2. Pick a currency, travel dates and budget.
3. Toggle **Live stream** if you want progressive results.
4. Click **Plan my trip**.

## License

MIT