import os
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from dashboard import (
    locations,
    live_data,
    historical,
    alarms,
    alerts,
)


# -----------------------------
# Configuration
# -----------------------------
REFRESH_INTERVAL = int(
    os.getenv("REFRESH_INTERVAL_SECONDS", "15")
)

st.set_page_config(
    page_title="SmartCover Live Dashboard",
    layout="wide",
)

st.title("SmartCover Live Dashboard")
st.caption("Local • Open-Source • Read-Only")

# -----------------------------
# AUTO-REFRESH (GLOBAL)
# -----------------------------
# This refreshes the *entire app* at a fixed interval.
# Safe because all calls are read-only.
st_autorefresh(
    interval=REFRESH_INTERVAL * 1000,
    key="global_autorefresh"
)

# -----------------------------
# Tabs
# -----------------------------
tab_locations, tab_live, tab_historical, tab_alarms, tab_alerts = st.tabs(
    [
        "Locations",
        "Live Data",
        "Historical",
        "Alarms",
        "Alerts",
    ]
)

with tab_locations:
    locations.render()

with tab_live:
    live_data.render(refresh_interval=REFRESH_INTERVAL)

    
with tab_historical:
    historical.render()

with tab_alarms:
    alarms.render()

with tab_alerts:
    alerts.render()
