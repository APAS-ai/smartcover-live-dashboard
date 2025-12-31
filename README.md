# SmartCover Live Dashboard

A read-only, local dashboard built to explore and validate SmartCover API capabilities. This project demonstrates successful ingestion and visualization of SmartCover data, including near real-time sensor readings, historical trends, alarms, and alerts.

The dashboard is intended for **API validation, exploration, and demonstration purposes**. It does not modify or write back to SmartCover systems.

---

## Overview

This application consumes SmartCover's public API endpoints and renders the data into a structured dashboard with the following goals:

- Validate API availability and stability
- Understand the structure and freshness of live telemetry
- Visualize historical sensor trends
- Inspect alarms and alerts in a human-readable format
- Provide a foundation for future product or demo work

---

## Features

### Locations Overview

Lists all available locations returned by the API and displays metadata such as:

- Location ID
- Description
- Application type
- Alarm and alert state
- Latitude and longitude

### Live Data

Displays the **latest reported sensor readings** for a selected location. Supports commonly available data types such as:

- PowerPack Voltage
- Water Level / Distance
- Temperature
- Signal Strength
- Signal Quality

Shows the timestamp of the last reported value and auto-refreshes at a fixed interval to reflect near real-time updates.

### Historical Trends

Allows selection of location, data type, and date range. Renders time-series plots for historical sensor data and supports CSV export for offline analysis.

### Alarms

Displays historical and recent alarm events with details such as:

- Alarm type
- Duration
- Start and end times
- Depth thresholds
- Acknowledgement state

### Alerts

Displays alert-level events such as low battery, delayed communication, and suspect sensor. Supports filtering for active alerts only.

---

## Data Source

All data is fetched from the SmartCover API.

Example endpoint used:

```
https://www.mysmartcover.com/api/locations/list.php
```

Key characteristics of the API based on testing:

- Returns structured JSON responses
- Includes latest sensor readings per location
- Supports historical data access
- Provides alarm and alert metadata
- Data is near real-time, not true streaming (poll-based updates)

---

## Architecture

- **Frontend:** Streamlit
- **Data Access:** Direct REST API calls
- **Mode:** Read-only
- **Deployment:** Local execution

There is **no backend database or caching layer**. The dashboard reflects the API responses as-is.

---

## Installation

### Prerequisites

- Python 3.9+
- pip or virtualenv

### Setup

Clone the repository:

```bash
git clone <repo-url>
cd smartcover-live-dashboard
```

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the App

Start the Streamlit application:

```bash
streamlit run app.py
```

The dashboard will be available at:

```
http://localhost:8501
```

---

## Configuration

- API base URLs and refresh intervals are configurable in the code
- The application is intentionally kept simple and transparent for inspection and iteration

---

## Limitations

- This is not a real-time streaming system; data updates rely on periodic polling
- Data availability depends entirely on what each location reports
- No authentication, write-back, or control functionality is included
- UI is designed for clarity and validation, not production deployment

---

## Intended Use

- API validation and exploration
- Internal demos and walkthroughs
- Understanding SmartCover data semantics
- Foundation for future analytics or operational tooling

---

## License

This project is provided for internal evaluation and demonstration purposes. Usage is subject to SmartCover API terms and conditions.

---

## Next Possible Extensions

- Per-metric live tiles for critical telemetry
- Aggregated views across multiple locations
- Alert prioritization and severity scoring
- Export-ready reports for operations teams
- Integration with downstream analytics pipelines

---

## Contributing

Contributions and feedback are welcome. Please open an issue or submit a pull request for any improvements or suggestions.