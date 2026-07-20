"""Dataframe and data grid wrappers."""
import streamlit as st
import pandas as pd

def render_data_table(data: list[dict]) -> None:
    """Renders an interactive dataframe."""
    if not data:
        st.info("No data available.")
        return
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)
  
