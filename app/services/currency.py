import os
from datetime import datetime
import httpx
from services.cache import get_cache, set_cache
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")

async def fetch_currency_rates(base_currency: str) -> dict[str, float]:
    """Fetech currency exchange rates form an exterenal api"""

    cache_key = f"currency:{base_currency}"
    cached_data = get_cache(cache_key)

    if cached_data:
        return cached_data

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/{base_currency}"
        )
        response.raise_for_status()
        data = response.json()

        rates = data.get("conversion_rates",{})
        set_cache(cache_key, rates, ttl= 300)
        return rates