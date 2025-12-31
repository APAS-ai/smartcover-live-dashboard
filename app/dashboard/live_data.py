import streamlit as st
from datetime import datetime
from api.smartcover import get_locations


def render(refresh_interval: int):
    st.header("Live Data")
    st.caption("Latest reported sensor values (near real-time)")

    # -----------------------------
    # Load locations
    # -----------------------------
    locations = get_locations()
    if not locations:
        st.info("No locations available.")
        st.stop()

    loc_map = {l["description"]: l for l in locations}

    location_name = st.selectbox(
        "Location",
        list(loc_map.keys()),
        key="live_location"
    )
    location = loc_map[location_name]

    data_types = location.get("data_types", [])
    if not data_types:
        st.info("No sensor data available.")
        st.stop()

    st.subheader("Current Readings")

    cols = st.columns(3)
    col_idx = 0

    for dt in data_types:
        col = cols[col_idx % 3]
        col_idx += 1

        label = dt["description"]
        unit = dt.get("unit", "")
        last = dt.get("last_reading")

        if not last or last[0] is None:
            col.metric(label, "—")
            continue

        timestamp, value = last

        col.metric(
            label=label,
            value=f"{value} {unit}".strip(),
            delta=f"Updated {timestamp}"
        )

    st.caption(f"Auto-refresh every {refresh_interval} seconds")
