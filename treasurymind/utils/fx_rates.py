"""FX Rate fetching utility using ExchangeRate-API."""
import os
import requests
from typing import Dict
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FX_API_KEY = os.getenv("FX_API_KEY", "")
BASE_URL = "https://v6.exchangerate-api.com/v6"


def get_live_rate(from_currency: str, to_currency: str = "MYR") -> float:
    """Fetch live exchange rate."""
    try:
        url = f"{BASE_URL}/{FX_API_KEY}/pair/{from_currency}/{to_currency}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("result") == "success":
            return data["conversion_rate"]
    except Exception:
        pass
    return get_fallback_rate(from_currency, to_currency)


def get_historical_rate(from_currency: str, to_currency: str, date: str) -> float:
    """Fetch historical rate for a specific date (YYYY-MM-DD)."""
    try:
        dt = datetime.strptime(date, "%Y-%m-%d")
        year, month, day = dt.year, dt.month, dt.day
        url = f"{BASE_URL}/{FX_API_KEY}/history/{from_currency}/{year}/{month}/{day}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get("result") == "success":
            rates = data.get("conversion_rates", {})
            return rates.get(to_currency, get_fallback_rate(from_currency, to_currency))
    except Exception:
        pass
    return get_fallback_rate(from_currency, to_currency)


def get_fallback_rate(from_currency: str, to_currency: str = "MYR") -> float:
    """Fallback rates when API is unavailable."""
    fallback_rates = {
        ("USD", "MYR"): 4.47,
        ("EUR", "MYR"): 4.85,
        ("GBP", "MYR"): 5.65,
        ("SGD", "MYR"): 3.35,
        ("AUD", "MYR"): 2.95,
        ("JPY", "MYR"): 0.030,
        ("CNY", "MYR"): 0.62,
        ("INR", "MYR"): 0.053,
    }
    if from_currency == to_currency:
        return 1.0
    return fallback_rates.get((from_currency.upper(), to_currency.upper()), 4.47)


def convert_to_myr(amount: float, from_currency: str, date: str = None) -> Dict:
    """Convert an amount to MYR with rate info."""
    if from_currency.upper() == "MYR":
        return {"original_amount": amount, "myr_amount": amount, "rate": 1.0, "currency": "MYR"}

    if date:
        rate = get_historical_rate(from_currency, "MYR", date)
    else:
        rate = get_live_rate(from_currency, "MYR")

    myr_amount = round(amount * rate, 2)
    return {
        "original_amount": amount,
        "myr_amount": myr_amount,
        "rate": rate,
        "currency": from_currency.upper(),
    }

