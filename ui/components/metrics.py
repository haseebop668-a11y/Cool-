"""Dashboard KPI visualizers."""
import streamlit as st

def display_kpi(label: str, value: str, delta: str = None) -> None:
    """Renders a standard Streamlit metric."""
    st.metric(label=label, value=value, delta=delta)
  
