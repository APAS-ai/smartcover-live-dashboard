import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from api.smartcover import get_locations, get_historical_data


def render():
    st.header("Historical Trends")

    locations = get_locations()
    if not locations:
        st.info("No locations available.")
        st.stop()

    loc_map = {l["description"]: l for l in locations}

    location_name = st.selectbox(
        "Location",
        list(loc_map.keys()),
        key="historical_location"
    )
    location = loc_map[location_name]

    data_types = {
        dt["description"]: dt["id"]
        for dt in location.get("data_types", [])
    }

    if not data_types:
        st.info("No data types available for this location.")
        st.stop()

    data_type_name = st.selectbox(
        "Data Type",
        list(data_types.keys()),
        key="historical_datatype"
    )
    data_type_id = data_types[data_type_name]

    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input(
            "Start date",
            datetime.utcnow().date() - timedelta(days=7),
            key="historical_start"
        )
    with col2:
        end = st.date_input(
            "End date",
            datetime.utcnow().date(),
            key="historical_end"
        )

    if start >= end:
        st.error("Start date must be before end date.")
        st.stop()

    with st.spinner("Fetching historical data..."):
        series = get_historical_data(
            location_id=location["id"],
            data_type=data_type_id,
            start_time=datetime.combine(start, datetime.min.time()),
            end_time=datetime.combine(end, datetime.min.time()),
        )

    if not series or not series[0]:
        st.info("No historical data available.")
        return

    timestamps, values = zip(*series[0])
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamps),
        "value": values
    })

    fig = px.line(df, x="timestamp", y="value")
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "Download CSV",
        df.to_csv(index=False),
        file_name="historical_data.csv",
        key="historical_download"
    )
