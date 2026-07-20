"""Configuration and preferences view."""
import streamlit as st
from ui.components.forms import secure_input

def render() -> None:
    st.header("Workbench Settings")
    
    with st.expander("API Credentials", expanded=True):
        secure_input("OpenAI API Key", "openai_key")
        secure_input("Anthropic API Key", "anthropic_key")
        secure_input("GitHub Token", "github_token")
        if st.button("Save Credentials", type="primary"):
            st.toast("Credentials securely cached in session state.")
            
    with st.expander("UI Preferences"):
        st.selectbox("Theme", ["Obsidian Luxury", "Light Mode"])
        st.toggle("Enable Screen Reader Assertions", value=True)
      
