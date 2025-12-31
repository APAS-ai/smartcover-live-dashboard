import os
import requests
from datetime import datetime, timedelta

SMARTCOVER_API_BASE = os.getenv(
    "SMARTCOVER_API_BASE",
    "https://www.mysmartcover.com/api"
)
SMARTCOVER_JWT = os.getenv("SMARTCOVER_JWT")

if not SMARTCOVER_JWT:
    raise RuntimeError("SMARTCOVER_JWT not set in environment")

HEADERS = {
    "Authorization": f"Bearer {SMARTCOVER_JWT}"
}


def _get(endpoint: str, params: dict | None = None):
    url = f"{SMARTCOVER_API_BASE}/{endpoint}"
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if data.get("response_code", 0) != 0:
        raise RuntimeError(data.get("response_text", "Unknown API error"))

    return data


# ------------------------
# Core API functions
# ------------------------

def get_locations():
    data = _get("locations/list.php")
    return data.get("locations", [])


def get_live_data(location_id: int, data_type: int, window_minutes: int = 15):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=window_minutes)

    params = {
        "location": location_id,
        "data_type": data_type,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M"),
    }

    data = _get("locations/data.php", params=params)
    return data.get("data", [])


def get_historical_data(
    location_id: int,
    data_type: int,
    start_time: datetime,
    end_time: datetime,
):
    params = {
        "location": location_id,
        "data_type": data_type,
        "start_time": start_time.strftime("%Y-%m-%d %H:%M"),
        "end_time": end_time.strftime("%Y-%m-%d %H:%M"),
    }

    data = _get("locations/data.php", params=params)
    return data.get("data", [])


def get_alarms(active_only: bool = True):
    params = {}
    if active_only:
        params["active"] = 1

    data = _get("locations/alarms/list.php", params=params)
    return data.get("data", [])


def get_alerts(active_only: bool = True):
    params = {}
    if active_only:
        params["active"] = 1

    data = _get("locations/alerts/list.php", params=params)
    return data.get("data", [])
