"""Navigation drawer component."""
import streamlit as st
from ui.state import StateManager

def render_sidebar() -> None:
    """Renders the main navigation menu."""
    st.title("⚡ AI Workbench")
    st.divider()
    
    nav_items = {
        "dashboard": "📊 Dashboard",
        "ai_chat": "💬 AI Agents",
        "repository": "📁 Repository",
        "github": "🐙 GitHub Integration",
        "logs": "📜 Execution Logs",
        "settings": "⚙️ Settings"
    }
    
    current = StateManager.get_state().current_page
    
    for page_id, label in nav_items.items():
        # Visual indicator for active page
        is_active = (current == page_id)
        btn_type = "primary" if is_active else "secondary"
        
        if st.button(label, key=f"nav_{page_id}", use_container_width=True, type=btn_type):
            StateManager.update_page(page_id)
            st.rerun()
          
