"""Modal and overlay handling utilizing Streamlit dialogs."""
import streamlit as st

@st.dialog("Confirm Action")
def confirm_action_dialog(message: str, on_confirm: callable) -> None:
    """Generic confirmation modal."""
    st.write(message)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel"):
            st.rerun()
    with col2:
        if st.button("Confirm", type="primary"):
            on_confirm()
            st.rerun()
          
