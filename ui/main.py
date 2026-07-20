"""Global application layout wrapper and entry point."""
import streamlit as st
from ui.theme import inject_theme
from ui.accessibility import inject_a11y_core_styles, inject_skip_link
from ui.layouts import render_global_shell
from ui.state import StateManager

def bootstrap() -> None:
    """Initializes the Streamlit application shell."""
    st.set_page_config(
        page_title="AI Engineering Workbench",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    inject_theme()
    inject_a11y_core_styles()
    inject_skip_link(target_anchor="main-content")
    
    StateManager.initialize()
    render_global_shell()

if __name__ == "__main__":
    bootstrap()
  
