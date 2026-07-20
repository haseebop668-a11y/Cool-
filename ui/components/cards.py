"""Glassmorphism container equivalents for Streamlit."""
import streamlit as st
from contextlib import contextmanager

@contextmanager
def render_card(title: str):
    """Renders content inside a visually distinct container."""
    container = st.container(border=True)
    with container:
        st.subheader(title)
        yield
      
