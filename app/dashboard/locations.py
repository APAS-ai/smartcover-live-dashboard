import streamlit as st
import pandas as pd
from api.smartcover import get_locations


def render():
    st.header("Locations Overview")

    with st.spinner("Loading locations..."):
        response = get_locations()

    locations = response.get("locations", [])
    if not locations:
        st.info("No locations found.")
        return

    rows = []
    for loc in locations:
        rows.append({
            "ID": loc.get("id"),
            "Description": loc.get("description"),
            "Application": loc.get("application_description"),
            "Alarm": loc.get("alarm_state"),
            "Alert": loc.get("alert_state"),
            "Latitude": loc.get("latitude"),
            "Longitude": loc.get("longitude"),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)
