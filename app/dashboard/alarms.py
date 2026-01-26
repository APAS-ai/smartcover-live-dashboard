import streamlit as st
import pandas as pd
from api.smartcover import get_alarms


def render():
    st.header("Alarms")

    active_only = st.checkbox(
        "Show active alarms only",
        value=True,
        key="alarms_active_only"
    )
    with st.spinner("Loading alarms..."):
        response = get_alarms(active=1 if active_only else 0)

    alarms = response.get("data", [])
    if not alarms:
        st.info("No alarms found.")
        return

    df = pd.DataFrame(alarms)
    st.dataframe(df, use_container_width=True)
