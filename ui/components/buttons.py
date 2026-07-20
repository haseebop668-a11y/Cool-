"""Styled presentation buttons."""
import streamlit as st

def primary_action(label: str, key: str, help_text: str = "") -> bool:
    """Renders a primary action button."""
    return st.button(label, key=key, type="primary", help=help_text, use_container_width=True)
  
