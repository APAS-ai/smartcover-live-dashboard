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
        alarms = get_alarms(active_only=active_only)

    if not alarms:
        st.info("No alarms found.")
        return

    df = pd.DataFrame(alarms)
    st.dataframe(df, use_container_width=True)
