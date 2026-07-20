"""Semantic indicators."""
import streamlit as st

def render_badge(status: str) -> None:
    """Renders a visual badge based on status text."""
    colors = {
        "success": "green",
        "error": "red",
        "warning": "orange",
        "info": "blue"
    }
    color = colors.get(status.lower(), "gray")
    st.markdown(f":{color}[**{status.upper()}**]")
  
