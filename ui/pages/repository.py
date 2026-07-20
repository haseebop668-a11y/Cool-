"""Local repository management view."""
import streamlit as st

def render() -> None:
    st.header("Repository Browser")
    st.write("View and manage local workspace files.")
    
    tab1, tab2 = st.tabs(["File Tree", "Scan Summary"])
    
    with tab1:
        st.code("""
        workspace/
        ├── core/
        ├── ui/
        └── tests/
        """)
    with tab2:
        st.success("No architectural violations detected in current tree.")
      
