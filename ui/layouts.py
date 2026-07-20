"""Global application layouts and structural shells."""
import streamlit as st
from ui.navigation import Router
from ui.sidebar import render_sidebar

def render_global_shell() -> None:
    """Renders the top-level application container, sidebar, and routes the active view."""
    # Main content anchor for accessibility skip link
    st.markdown('<div id="main-content"></div>', unsafe_allow_html=True)
    
    # Sidebar rendering
    with st.sidebar:
        render_sidebar()
    
    # View routing based on state
    Router.render_current_view()
  
