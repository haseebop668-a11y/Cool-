"""View routing and navigation controller."""
import streamlit as st
from ui.state import StateManager
from ui.pages import dashboard, ai_chat, repository, github_page, settings, logs

class Router:
    """Maps state page names to actual View functions."""
    
    ROUTES = {
        "dashboard": dashboard.render,
        "ai_chat": ai_chat.render,
        "repository": repository.render,
        "github": github_page.render,
        "settings": settings.render,
        "logs": logs.render,
    }

    @classmethod
    def render_current_view(cls) -> None:
        current_page = StateManager.get_state().current_page
        view_func = cls.ROUTES.get(current_page, dashboard.render)
        
        try:
            view_func()
        except Exception as e:
            st.error(f"UI Rendering Error: Failed to load view '{current_page}'.")
            st.code(str(e))
          
