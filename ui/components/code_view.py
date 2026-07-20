"""Syntax highlighting and snippet presentation."""
import streamlit as st

def render_snippet(code: str, language: str = "python") -> None:
    """Renders read-only code blocks."""
    st.code(code, language=language)
  
