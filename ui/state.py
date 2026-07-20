"""Typed UI Session State Manager."""
import streamlit as st
from pydantic import BaseModel, Field

class UIState(BaseModel):
    """Pydantic model representing strictly presentation state."""
    current_page: str = Field(default="dashboard")
    is_loading: bool = Field(default=False)
    sidebar_expanded: bool = Field(default=True)

class StateManager:
    """Proxy for safe interaction with Streamlit session state."""
    
    @staticmethod
    def initialize() -> None:
        if "ui_state" not in st.session_state:
            st.session_state.ui_state = UIState()
            
    @staticmethod
    def get_state() -> UIState:
        return st.session_state.ui_state
        
    @staticmethod
    def update_page(page_name: str) -> None:
        st.session_state.ui_state.current_page = page_name
        
    @staticmethod
    def set_loading(status: bool) -> None:
        st.session_state.ui_state.is_loading = status
      
