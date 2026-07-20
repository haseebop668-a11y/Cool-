"""Main system dashboard view."""
import streamlit as st
from ui.components.metrics import display_kpi
from ui.components.cards import render_card

def render() -> None:
    st.header("System Dashboard")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with render_card("Active Agents"):
            display_kpi("Total", "4", delta="+1")
    with col2:
        with render_card("System Health"):
            display_kpi("Status", "Optimal")
    with col3:
        with render_card("Repository Operations"):
            display_kpi("Commits", "142", delta="12 today")
            
    st.subheader("Recent Activity")
    st.info("Waiting for telemetry data...")
  
