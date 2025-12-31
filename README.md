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
- **UI Framework:** Streamlit
- **Data Access:** Direct REST API calls
- **Mode:** Read-only
- **Persistence:** None (stateless)

There is **no database**, **no background worker**, and **no data modification**.

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

Once running, access the dashboard at:
```
http://localhost:8501
```

To stop the dashboard:
```bash
docker compose down
```

---

## Configuration

- API endpoints and refresh intervals are defined in the application code
- The dashboard refreshes live data at a fixed polling interval
- No credentials are stored or required for the tested endpoints

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