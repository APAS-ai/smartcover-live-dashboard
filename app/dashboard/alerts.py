import streamlit as st
import pandas as pd
from api.smartcover import get_alerts


def render():
    st.header("Alerts")

    active_only = st.checkbox(
        "Show active alerts only",
        value=True,
        key="alerts_active_only"
    )

    with st.spinner("Loading alerts..."):
        alerts = get_alerts(active_only=active_only)

    if not alerts:
        st.info("No alerts found.")
        return

    df = pd.DataFrame(alerts)
    st.dataframe(df, use_container_width=True)
