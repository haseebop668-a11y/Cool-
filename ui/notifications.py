"""Toast and alert system."""
import streamlit as st
from ui.accessibility import announce_to_screen_reader

def show_toast(message: str, icon: str = "ℹ️") -> None:
    """Displays a transient toast and announces it to screen readers."""
    st.toast(message, icon=icon)
    announce_to_screen_reader(message)

def show_error(title: str, exception_msg: str) -> None:
    """Displays a persistent error alert."""
    st.error(title)
    with st.expander("Details"):
        st.code(exception_msg)
    announce_to_screen_reader(f"Error: {title}", assertiveness="assertive")
  
