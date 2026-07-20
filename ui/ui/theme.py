"""Design tokens and CSS injection."""
import streamlit as st
import os

THEME_NAME = "Obsidian Luxury"
THEME_VERSION = "1.2.0"
_THEME_INJECTION_KEY = "__theme_injected__"

def inject_theme() -> None:
    """Injects global CSS variables and styling overrides."""
    if st.session_state.get(_THEME_INJECTION_KEY):
        return

    # Base design tokens
    css = """
    <style>
    :root { 
        --bg-obsidian: #0B0C10; 
        --bg-surface: #1F2833;
        --accent-cyan: #66FCF1; 
        --accent-teal: #45A29E;
        --text-primary: #C5C6C7;
        --text-secondary: #8A8D91;
        --radius-md: 8px;
        --shadow-elevated: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    
    /* Streamlit Overrides */
    .stApp { 
        background-color: var(--bg-obsidian) !important; 
        color: var(--text-primary) !important;
    }
    
    .stSidebar {
        background-color: var(--bg-surface) !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--accent-cyan) !important;
        font-weight: 600 !important;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    
    # Load external CSS if present
    css_path = os.path.join(os.path.dirname(__file__), 'assets', 'custom.css')
    if os.path.exists(css_path):
        with open(css_path, 'r') as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
    st.session_state[_THEME_INJECTION_KEY] = True
  
