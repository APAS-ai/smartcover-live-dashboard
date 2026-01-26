# SmartCover Live Dashboard

A read-only, containerized dashboard for validating and visualizing SmartCover API data. This project uses **Docker** to provide a one-command setup that fetches, renders, and refreshes SmartCover telemetry locally.

The dashboard is intended for **API testing, validation, and demonstration**. It does not write back to SmartCover systems.

---

## What This Project Does

This repository demonstrates that the SmartCover API can be:

- Successfully accessed and parsed
- Used to retrieve near real-time sensor readings
- Queried for historical telemetry
- Queried for alarms and alerts
- Rendered into a usable dashboard without any proprietary tooling

All screenshots in this repository are generated from live API responses.

---

## Key Features

### Locations
Lists all locations returned by the SmartCover API and displays:
- Location ID
- Description
- Application type
- Alarm and alert state
- Latitude and longitude

### Live Data (Near Real-Time)
Shows latest reported sensor values for a selected location. Common metrics include:
- PowerPack Voltage
- Water Level / Distance
- Temperature
- Signal Strength
- Signal Quality

Displays the timestamp of the last reading and auto-refreshes at a fixed interval (poll-based).

### Historical Trends
- Select location, data type, and date range
- Renders time-series plots
- Allows CSV export for offline analysis

### Alarms
Displays historical alarm events with details including:
- Alarm type
- Duration
- Depth thresholds
- Start and end timestamps
- Acknowledgement state

### Alerts
Displays alert events such as:
- Low Battery
- Delayed Communication
- Suspect Sensor

Supports filtering for active alerts only.

---

## Data Source

All data is retrieved from SmartCover's API endpoints.

Example:
```
https://www.mysmartcover.com/api/locations/list.php
```

Important notes based on testing:
- API responses are JSON
- Live data is **poll-based**, not streaming
- Not all locations report the same telemetry
- Timestamps vary by sensor and device type

---

## Architecture

- **Runtime:** Docker container
- **UI Framework:** Streamlit (port 8501)
- **API Proxy:** FastAPI (port 8080)
- **Data Access:** Direct REST API calls
- **Mode:** Read-only
- **Persistence:** None (stateless)

There is **no database**, **no background worker**, and **no data modification**.

---

## FastAPI Proxy API (Port 8080)

The project includes a FastAPI-based proxy service that exposes SmartCover data through authenticated REST endpoints. This allows you to provide controlled access to SmartCover data without sharing your SmartCover credentials.

### Setup

**1. Configure environment variables in `.env`:**

```bash
# Required: Your SmartCover JWT token
SMARTCOVER_JWT=your-smartcover-jwt-token

# Required: Secret key for signing proxy API tokens (generate a random string)
JWT_SECRET_KEY=generate-a-long-random-string-here

# Required: Password for the external user to authenticate
API_ADMIN_PASSWORD=password-you-give-to-external-user

# Optional: Token expiration in minutes (default: 60)
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
```

**2. Generate a secure JWT_SECRET_KEY:**

```bash
# Linux/Mac
openssl rand -hex 32

# Or Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Authentication

The API uses JWT Bearer tokens. The external user authenticates with username `admin` and the password you set in `API_ADMIN_PASSWORD`.

**Step 1: Get a token**
```bash
curl -X POST http://localhost:8080/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password-you-give-to-external-user"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Step 2: Use the token for API calls**
```bash
# Set token as variable for convenience
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Get all locations
curl "http://localhost:8080/api/v1/locations/list" \
  -H "Authorization: Bearer $TOKEN"

# Get location summary
curl "http://localhost:8080/api/v1/locations/summary" \
  -H "Authorization: Bearer $TOKEN"

# Get historical data (replace 123 with actual location ID)
curl "http://localhost:8080/api/v1/locations/data?location=123&data_type=2&start_time=2025-01-01%2000:00&end_time=2025-01-07%2000:00" \
  -H "Authorization: Bearer $TOKEN"

# Get live data
curl "http://localhost:8080/api/v1/locations/live?location=123&data_type=2&window_minutes=30" \
  -H "Authorization: Bearer $TOKEN"

# Get active alarms
curl "http://localhost:8080/api/v1/locations/alarms/list?active=1" \
  -H "Authorization: Bearer $TOKEN"

# Get active alerts
curl "http://localhost:8080/api/v1/locations/alerts/list?active=1" \
  -H "Authorization: Bearer $TOKEN"
```

### Available Endpoints (READ-ONLY)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/token` | POST | Get proxy API token |
| `/api/v1/locations/list` | GET | List all locations |
| `/api/v1/locations/summary` | GET | Location/alarm/alert counts |
| `/api/v1/locations/{id}` | GET | Get specific location |
| `/api/v1/locations/data` | GET | Historical sensor data |
| `/api/v1/locations/live` | GET | Live sensor data |
| `/api/v1/locations/alarms/list` | GET | Alarm events |
| `/api/v1/locations/alerts/list` | GET | Alert events |
| `/api/v1/health` | GET | Health check (no auth required) |

**Security:** This API is READ-ONLY. Write operations (alarm acknowledgment, token refresh) are intentionally not exposed to protect your SmartCover account.

All endpoints support the same query parameters as the official SmartCover API (timezone, date_format, etc.). See the interactive docs for full parameter details.

### Interactive Documentation

Once running, access the auto-generated API docs:
- **Swagger UI:** http://localhost:8080/docs (try endpoints interactively)
- **ReDoc:** http://localhost:8080/redoc (detailed documentation)

---

## Requirements

- Docker
- Docker Compose (recommended)

No local Python installation is required.

---

## Running the Dashboard (Docker)

Clone the repository:
```bash
git clone <repo-url>
cd smartcover-live-dashboard
```

Build and start the container:
```bash
docker compose up --build
```

Once running, access:
- **Dashboard:** http://localhost:8501
- **API Docs:** http://localhost:8080/docs
- **API Health:** http://localhost:8080/api/v1/health

To stop the dashboard:
```bash
docker compose down
```

---

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:

| Variable | Description |
|----------|-------------|
| `SMARTCOVER_JWT` | Your SmartCover API JWT token |
| `JWT_SECRET_KEY` | Secret key for signing proxy API tokens |
| `API_ADMIN_PASSWORD` | Password for the `admin` API user |

Optional:

| Variable | Default | Description |
|----------|---------|-------------|
| `REFRESH_INTERVAL_SECONDS` | 15 | Dashboard auto-refresh interval |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 60 | API token expiration time |

---

## Limitations

- This is **not a real-time streaming system**
- Data freshness depends entirely on device reporting frequency
- Some telemetry types may not exist for certain locations
- This is not production-hardened (no auth, rate limiting, or caching)

---

## Intended Use

- API validation
- Technical due diligence
- Internal demos
- Data exploration
- Foundation for future analytics or operational tooling

---

## Status

- API tested and verified
- Live data confirmed for multiple locations
- Historical data retrieval confirmed
- Alarms and alerts successfully parsed
- Dashboard fully operational via Docker

---

## License / Usage

This project is provided for internal evaluation and demonstration purposes. Usage is subject to SmartCover API terms and conditions.