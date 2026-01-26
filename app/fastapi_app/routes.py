"""
FastAPI routes that provide READ-ONLY access to SmartCover API data.

This is a proxy service designed for sharing data with external parties
without exposing your SmartCover credentials or allowing write operations.

SECURITY: Only GET (read) operations are exposed. No write operations
(alarm acknowledgment, token refresh, etc.) are available through this API.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth import (
    get_current_user,
    verify_credentials,
    create_access_token,
    get_token_info,
    get_user_tokens,
    get_user_token_status,
)

security = HTTPBearer()
from .schemas import (
    TokenRequest,
    TokenResponse,
    TokenInfoResponse,
    TokenStatusResponse,
    UserTokensResponse,
)

# Import SmartCover API functions (READ-ONLY operations only)
import sys
sys.path.insert(0, "/app/app")
from api.smartcover import (
    get_locations as sc_get_locations,
    get_location_summary as sc_get_location_summary,
    get_historical_data as sc_get_historical_data,
    get_live_data as sc_get_live_data,
    get_alarms as sc_get_alarms,
    get_alerts as sc_get_alerts,
)


router = APIRouter()


# -------------------------
# Auth Endpoints
# -------------------------
@router.post("/auth/token", response_model=TokenResponse, tags=["Authentication"])
async def login(request: TokenRequest):
    """
    Authenticate and receive a JWT access token for this proxy API.

    Each token is assigned a unique name (API_1, API_2, API_3, etc.) for tracking.

    Use this token in the Authorization header as: `Bearer <token>`

    Note: This is YOUR proxy API token, not the SmartCover token.
    """
    if not verify_credentials(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token, expires_in, api_name = create_access_token(request.username)
    return TokenResponse(
        access_token=access_token,
        expires_in=expires_in,
        api_name=api_name,
    )


@router.get("/auth/token-info", response_model=TokenInfoResponse, tags=["Authentication"])
async def token_info(
    current_user: Annotated[str, Depends(get_current_user)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    """
    Get information about your current token including expiry time.

    Returns token validity, API name, issue time, expiry time, and human-readable time remaining.
    """
    return get_token_info(credentials.credentials)


@router.get("/auth/token-status", response_model=TokenStatusResponse, tags=["Authentication"])
async def token_status(
    current_user: Annotated[str, Depends(get_current_user)],
):
    """
    Check how many tokens you have remaining.

    Returns your active token count, token limit, and remaining slots.
    """
    return get_user_token_status(current_user)


@router.get("/auth/my-tokens", response_model=UserTokensResponse, tags=["Authentication"])
async def my_tokens(
    current_user: Annotated[str, Depends(get_current_user)],
):
    """
    List all your active API tokens.

    Returns all your active tokens with their API names (API_1, API_2, etc.),
    creation time, and expiry information.

    Useful if you've forgotten which tokens you have active.
    """
    tokens = get_user_tokens(current_user)
    return UserTokensResponse(
        username=current_user,
        tokens=tokens,
    )


# -------------------------
# Location List API
# -------------------------
@router.get("/locations/list", tags=["Locations"])
async def get_locations(
    current_user: Annotated[str, Depends(get_current_user)],
    organization: int | None = Query(default=None, description="Internal unique identifier for an organization"),
    archived: int | None = Query(default=None, description="1 to include archived locations, 0 otherwise (default)"),
    stock: int | None = Query(default=None, description="0 to exclude stock locations, 1 otherwise (default)"),
    geojson: int | None = Query(default=None, description="1 to use GeoJSON format, 0 otherwise (default)"),
    flat: int | None = Query(default=None, description="1 to use flattened JSON format, 0 otherwise (default)"),
    timezone: str | None = Query(default=None, description="Timezone string (defaults to UTC)"),
    date_format: int | None = Query(default=None, description="Format for DateTime (1=yyyy-MM-dd HH:mm, 2=MM/dd/yyyy HH:mm)"),
    locations: str | None = Query(default=None, description="Comma-delimited list of location ids to subset"),
):
    """
    Get all SmartCover monitoring locations.

    Returns location details including coordinates, alarm/alert states,
    and available data types with their last readings.
    """
    try:
        return sc_get_locations(
            organization=organization,
            archived=archived,
            stock=stock,
            geojson=geojson,
            flat=flat,
            timezone=timezone,
            date_format=date_format,
            locations=locations,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SmartCover API error: {str(e)}",
        )


@router.get("/locations/{location_id}", tags=["Locations"])
async def get_location_by_id(
    location_id: int,
    current_user: Annotated[str, Depends(get_current_user)],
    timezone: str | None = Query(default=None, description="Timezone string (defaults to UTC)"),
    date_format: int | None = Query(default=None, description="Format for DateTime objects"),
):
    """
    Get a specific location by ID.

    Convenience endpoint - filters the location list by ID.
    """
    try:
        response = sc_get_locations(
            locations=str(location_id),
            timezone=timezone,
            date_format=date_format,
        )
        locs = response.get("locations", [])
        if not locs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location {location_id} not found",
            )
        # Return in same format as list endpoint but with single location
        return {
            "response_code": response.get("response_code", 0),
            "locations": locs,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SmartCover API error: {str(e)}",
        )


# -------------------------
# Location Summary API
# -------------------------
@router.get("/locations/summary", tags=["Locations"])
async def get_location_summary(
    current_user: Annotated[str, Depends(get_current_user)],
    organization: int | None = Query(default=None, description="Internal unique identifier for an organization"),
):
    """
    Get quick overview of organization's locations.

    Returns counts of locations, alarms, alerts, and advisories.
    """
    try:
        return sc_get_location_summary(organization=organization)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SmartCover API error: {str(e)}",
        )


# -------------------------
# Historical Data API
# -------------------------
@router.get("/locations/data", tags=["Data"])
async def get_historical_data(
    current_user: Annotated[str, Depends(get_current_user)],
    location: int = Query(..., description="Internal unique identifier for location"),
    start_time: str = Query(..., description="Starting date/time (yyyy-MM-dd HH:mm)"),
    end_time: str = Query(..., description="Ending date/time (yyyy-MM-dd HH:mm)"),
    data_type: int = Query(..., description="Type of data (1=voltage, 2=level, 3=temp, 4=signal strength, etc.)"),
    distance_style: int | None = Query(default=None, description="Override distance style (1-4)"),
    timezone: str | None = Query(default=None, description="Timezone string (defaults to UTC)"),
    date_format: int | None = Query(default=None, description="Format for DateTime objects"),
    epoch_time: int | None = Query(default=None, description="1 for epoch timestamps, 0 for string"),
    long_filter: int | None = Query(default=None, description="1 to remove erroneous readings"),
    resample_interval: int | None = Query(default=None, description="Resample to interval (minutes)"),
    resample_gaps: int | None = Query(default=None, description="1 to fill gaps via interpolation"),
):
    """
    Get historical data for a specific location and data type.

    Maximum of 31 days can be retrieved per request.
    """
    try:
        return sc_get_historical_data(
            location_id=location,
            data_type=data_type,
            start_time=start_time,
            end_time=end_time,
            distance_style=distance_style,
            timezone=timezone,
            date_format=date_format,
            epoch_time=epoch_time,
            long_filter=long_filter,
            resample_interval=resample_interval,
            resample_gaps=resample_gaps,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SmartCover API error: {str(e)}",
        )


# -------------------------
# Live Data (Convenience)
# -------------------------
@router.get("/locations/live", tags=["Data"])
async def get_live_data(
    current_user: Annotated[str, Depends(get_current_user)],
    location: int = Query(..., description="Internal unique identifier for location"),
    data_type: int = Query(..., description="Type of data (1=voltage, 2=level, 3=temp, etc.)"),
    window_minutes: int = Query(default=15, ge=1, le=1440, description="Time window in minutes (default: 15)"),
    distance_style: int | None = Query(default=None, description="Override distance style (1-4)"),
    timezone: str | None = Query(default=None, description="Timezone string (defaults to UTC)"),
    date_format: int | None = Query(default=None, description="Format for DateTime objects"),
    epoch_time: int | None = Query(default=None, description="1 for epoch timestamps, 0 for string"),
    long_filter: int | None = Query(default=None, description="1 to remove erroneous readings"),
):
    """
    Get live/recent data for a location.

    Convenience endpoint that wraps the Historical Data API with a short time window.
    """
    try:
        return sc_get_live_data(
            location_id=location,
            data_type=data_type,
            window_minutes=window_minutes,
            distance_style=distance_style,
            timezone=timezone,
            date_format=date_format,
            epoch_time=epoch_time,
            long_filter=long_filter,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SmartCover API error: {str(e)}",
        )


# -------------------------
# Alarm List API (READ-ONLY)
# -------------------------
@router.get("/locations/alarms/list", tags=["Alarms"])
async def get_alarms(
    current_user: Annotated[str, Depends(get_current_user)],
    active: int | None = Query(default=None, description="1 for active only, 0 for archived only"),
    timezone: str | None = Query(default=None, description="Timezone string (defaults to UTC)"),
    date_format: int | None = Query(default=None, description="Format for DateTime objects"),
    length: int | None = Query(default=None, description="Maximum number of alarm events to return"),
    offset: int | None = Query(default=None, description="Pagination offset"),
    organization: int | None = Query(default=None, description="Filter by organization ID (option 1)"),
    location_id: int | None = Query(default=None, description="Filter by location ID (option 2/3)"),
    start_id: int | None = Query(default=None, description="Start alarm ID for filtering (option 3/4)"),
    end_id: int | None = Query(default=None, description="End alarm ID for filtering (option 4)"),
):
    """
    Get alarm events from SmartCover (READ-ONLY).

    Three ways to access alarms:
    - Option 1: By organization (pass organization param)
    - Option 2: By location (pass location_id param)
    - Option 3: By location with alarm ID range (pass location_id, start_id, optionally end_id)

    Note: Alarm acknowledgment is not available through this API.
    """
    try:
        return sc_get_alarms(
            active=active,
            timezone=timezone,
            date_format=date_format,
            length=length,
            offset=offset,
            organization=organization,
            location_id=location_id,
            start_id=start_id,
            end_id=end_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SmartCover API error: {str(e)}",
        )


# -------------------------
# Alert List API (READ-ONLY)
# -------------------------
@router.get("/locations/alerts/list", tags=["Alerts"])
async def get_alerts(
    current_user: Annotated[str, Depends(get_current_user)],
    organization: int | None = Query(default=None, description="Filter by organization ID"),
    active: int | None = Query(default=None, description="1 for active only, 0 for archived only"),
    timezone: str | None = Query(default=None, description="Timezone string (defaults to UTC)"),
    date_format: int | None = Query(default=None, description="Format for DateTime objects"),
    length: int | None = Query(default=None, description="Maximum number of alerts to return"),
    offset: int | None = Query(default=None, description="Pagination offset"),
):
    """
    Get alert events from SmartCover (READ-ONLY).

    Alert types:
    - 1: Low Battery
    - 2: Delayed Communications
    - 3: Suspect Sensor
    """
    try:
        return sc_get_alerts(
            organization=organization,
            active=active,
            timezone=timezone,
            date_format=date_format,
            length=length,
            offset=offset,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SmartCover API error: {str(e)}",
        )


# -------------------------
# Health Check
# -------------------------
@router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint (no auth required)."""
    return {"status": "healthy", "service": "smartcover-proxy"}
