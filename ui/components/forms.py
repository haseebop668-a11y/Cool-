"""Styled input abstractions."""
import streamlit as st

def secure_input(label: str, key: str, help_text: str = "") -> str:
    """Renders a password/token input field."""
    return st.text_input(label, type="password", key=key, help=help_text)
  
