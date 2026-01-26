import os
import requests
from datetime import datetime, timedelta
from typing import Any

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


def _get(endpoint: str, params: dict | None = None) -> dict[str, Any]:
    """Make GET request to SmartCover API."""
    url = f"{SMARTCOVER_API_BASE}/{endpoint}"
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _post(endpoint: str, data: dict | None = None) -> dict[str, Any]:
    """Make POST request to SmartCover API."""
    url = f"{SMARTCOVER_API_BASE}/{endpoint}"
    resp = requests.post(url, headers=HEADERS, data=data, timeout=30)
    resp.raise_for_status()
    return resp.json()


# ------------------------
# Location List API
# ------------------------
def get_locations(
    organization: int | None = None,
    archived: int | None = None,
    stock: int | None = None,
    geojson: int | None = None,
    flat: int | None = None,
    timezone: str | None = None,
    date_format: int | None = None,
    locations: str | None = None,
) -> dict[str, Any]:
    """
    Get all locations from SmartCover API.

    Args:
        organization: Internal unique identifier for an organization
        archived: 1 to include archived locations, 0 otherwise (default)
        stock: 0 to exclude stock locations, 1 otherwise (default)
        geojson: 1 to use GeoJSON format, 0 otherwise (default)
        flat: 1 to use flattened JSON format, 0 otherwise (default)
        timezone: Timezone string (defaults to UTC)
        date_format: Format for DateTime objects (1=yyyy-MM-dd HH:mm, 2=MM/dd/yyyy HH:mm)
        locations: Comma-delimited list of location ids to subset

    Returns:
        Full API response dict with response_code and locations/data
    """
    params = {}
    if organization is not None:
        params["organization"] = organization
    if archived is not None:
        params["archived"] = archived
    if stock is not None:
        params["stock"] = stock
    if geojson is not None:
        params["geojson"] = geojson
    if flat is not None:
        params["flat"] = flat
    if timezone is not None:
        params["timezone"] = timezone
    if date_format is not None:
        params["date_format"] = date_format
    if locations is not None:
        params["locations"] = locations

    return _get("locations/list.php", params=params if params else None)


# ------------------------
# Location Summary API
# ------------------------
def get_location_summary(
    organization: int | None = None,
) -> dict[str, Any]:
    """
    Get quick overview of organization's locations.

    Args:
        organization: Internal unique identifier for an organization

    Returns:
        Full API response with num_locations, num_alarms, num_alerts, num_advisories
    """
    params = {}
    if organization is not None:
        params["organization"] = organization

    return _get("locations/summary.php", params=params if params else None)


# ------------------------
# Historical Data API
# ------------------------
def get_historical_data(
    location_id: int,
    data_type: int,
    start_time: datetime | str,
    end_time: datetime | str,
    distance_style: int | None = None,
    timezone: str | None = None,
    date_format: int | None = None,
    epoch_time: int | None = None,
    long_filter: int | None = None,
    resample_interval: int | None = None,
    resample_gaps: int | None = None,
) -> dict[str, Any]:
    """
    Get historical data for a location.

    Args:
        location_id: Internal unique identifier for location
        data_type: Type of data reading (1=voltage, 2=level, 3=temp, etc.)
        start_time: Starting date/time
        end_time: Ending date/time
        distance_style: Override location's distance style (1-4)
        timezone: Timezone string (defaults to UTC)
        date_format: Format for DateTime objects
        epoch_time: 1 for epoch timestamps, 0 for string
        long_filter: 1 to remove erroneous readings
        resample_interval: Resample data to interval (minutes)
        resample_gaps: 1 to fill gaps via interpolation

    Returns:
        Full API response with response_code and data array
    """
    # Format datetime if needed
    if isinstance(start_time, datetime):
        start_time = start_time.strftime("%Y-%m-%d %H:%M")
    if isinstance(end_time, datetime):
        end_time = end_time.strftime("%Y-%m-%d %H:%M")

    params = {
        "location": location_id,
        "data_type": data_type,
        "start_time": start_time,
        "end_time": end_time,
    }

    if distance_style is not None:
        params["distance_style"] = distance_style
    if timezone is not None:
        params["timezone"] = timezone
    if date_format is not None:
        params["date_format"] = date_format
    if epoch_time is not None:
        params["epoch_time"] = epoch_time
    if long_filter is not None:
        params["long_filter"] = long_filter
    if resample_interval is not None:
        params["resample_interval"] = resample_interval
    if resample_gaps is not None:
        params["resample_gaps"] = resample_gaps

    return _get("locations/data.php", params=params)


def get_live_data(
    location_id: int,
    data_type: int,
    window_minutes: int = 15,
    **kwargs,
) -> dict[str, Any]:
    """
    Get live/recent data for a location (convenience wrapper).

    Uses the Historical Data API with a short time window.
    """
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=window_minutes)

    return get_historical_data(
        location_id=location_id,
        data_type=data_type,
        start_time=start_time,
        end_time=end_time,
        **kwargs,
    )


# ------------------------
# Alarm List API
# ------------------------
def get_alarms(
    active: int | None = None,
    timezone: str | None = None,
    date_format: int | None = None,
    length: int | None = None,
    offset: int | None = None,
    organization: int | None = None,
    location_id: int | None = None,
    start_id: int | None = None,
    end_id: int | None = None,
) -> dict[str, Any]:
    """
    Get alarm events from SmartCover.

    Args:
        active: 1 for active only, 0 for archived only
        timezone: Timezone string (defaults to UTC)
        date_format: Format for DateTime objects
        length: Maximum number of alarm events to return
        offset: Pagination offset
        organization: Filter by organization ID (option 1)
        location_id: Filter by location ID (option 2/3)
        start_id: Start alarm ID for filtering (option 3/4)
        end_id: End alarm ID for filtering (option 4)

    Returns:
        Full API response with response_code, records_total, records_filtered, data
    """
    params = {}
    if active is not None:
        params["active"] = active
    if timezone is not None:
        params["timezone"] = timezone
    if date_format is not None:
        params["date_format"] = date_format
    if length is not None:
        params["length"] = length
    if offset is not None:
        params["offset"] = offset
    if organization is not None:
        params["organization"] = organization
    if location_id is not None:
        params["location_id"] = location_id
    if start_id is not None:
        params["start_id"] = start_id
    if end_id is not None:
        params["end_id"] = end_id

    return _get("locations/alarms/list.php", params=params if params else None)


# ------------------------
# Alarm Acknowledge API
# ------------------------
def acknowledge_alarms(
    all_org: int | None = None,
    location: int | None = None,
    start_id: int | None = None,
    end_id: int | None = None,
    holdoff: int | None = None,
) -> dict[str, Any]:
    """
    Acknowledge alarms for location or organization.

    Args:
        all_org: Organization ID to acknowledge all alarms (requires ADMIN+)
        location: Location ID to acknowledge alarms for
        start_id: First alarm ID to acknowledge
        end_id: Last alarm ID to acknowledge
        holdoff: Hours to hold off notifications (0-24, default 1)

    Returns:
        API response with response_code and response_text
    """
    data = {
        "api_token": SMARTCOVER_JWT,
    }
    if all_org is not None:
        data["all"] = all_org
    if location is not None:
        data["location"] = location
    if start_id is not None:
        data["start_id"] = start_id
    if end_id is not None:
        data["end_id"] = end_id
    if holdoff is not None:
        data["holdoff"] = holdoff

    return _post("locations/alarms/ack.php", data=data)


# ------------------------
# Alert List API
# ------------------------
def get_alerts(
    organization: int | None = None,
    active: int | None = None,
    timezone: str | None = None,
    date_format: int | None = None,
    length: int | None = None,
    offset: int | None = None,
) -> dict[str, Any]:
    """
    Get alert events from SmartCover.

    Args:
        organization: Filter by organization ID
        active: 1 for active only, 0 for archived only
        timezone: Timezone string (defaults to UTC)
        date_format: Format for DateTime objects
        length: Maximum number of alerts to return
        offset: Pagination offset

    Returns:
        Full API response with response_code, records_total, records_filtered, data
    """
    params = {}
    if organization is not None:
        params["organization"] = organization
    if active is not None:
        params["active"] = active
    if timezone is not None:
        params["timezone"] = timezone
    if date_format is not None:
        params["date_format"] = date_format
    if length is not None:
        params["length"] = length
    if offset is not None:
        params["offset"] = offset

    return _get("locations/alerts/list.php", params=params if params else None)


# ------------------------
# Token Refresh API
# ------------------------
def refresh_token() -> dict[str, Any]:
    """
    Refresh the SmartCover JWT token.

    Returns:
        API response with new token, days_remaining, user info
    """
    data = {
        "api_token": SMARTCOVER_JWT,
    }
    return _post("auth/refresh.php", data=data)
