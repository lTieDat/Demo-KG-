"""
Toast notification helper to prevent duplicate toasts on rerun
"""
import streamlit as st


def show_toast(message, key=None):
    """
    Show toast notification only once per action
    Uses session state to track shown toasts
    """
    if key is None:
        # Generate key from message
        key = f"toast_{hash(message)}"
    
    # Check if already shown in this session
    if f"shown_{key}" not in st.session_state:
        st.toast(message)
        st.session_state[f"shown_{key}"] = True


def clear_toast_history():
    """Clear all toast history from session state"""
    keys_to_delete = [k for k in st.session_state.keys() if k.startswith("shown_toast_")]
    for key in keys_to_delete:
        del st.session_state[key]
