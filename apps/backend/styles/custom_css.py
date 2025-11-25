"""
Custom CSS styles for the Streamlit application
"""
import streamlit as st


def inject_custom_css():
    """Inject custom CSS styles into the Streamlit app"""
    st.markdown("""
        <style>
            /* Global modern styles */
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f4f7fa;
                color: #333;
            }
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            h1, h2, h3, h4 {
                color: #1f77b4;
                transition: color 0.3s ease;
            }
            .stButton > button {
                background-color: #1f77b4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                background-color: #135c94;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .stSelectbox, .stTextInput, .stRadio {
                transition: all 0.3s ease;
            }
            .stSelectbox:hover, .stTextInput:hover, .stRadio:hover {
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            /* Fade-in animation for containers */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .stContainer, div[data-testid="column"] {
                animation: fadeIn 0.5s ease-out;
            }
            /* Card styles with hover animation and consistent padding */
            .recommendation-card {
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                padding: 25px 30px;
                margin: 20px 15px;
                background-color: white;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                transition: all 0.3s ease;
            }
            .recommendation-card:hover {
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
                transform: translateY(-5px);
                padding: 25px 30px; /* Keep padding consistent on hover */
            }
            .recommendation-card h4 {
                margin: 0 0 12px 0;
                color: #1f77b4;
            }
            .recommendation-card p {
                margin: 8px 0;
                color: #555;
                line-height: 1.4;
            }
            /* Expander animation */
            .stExpander {
                transition: all 0.3s ease;
            }
            
            /* ========== FIXED SPINNER (Text does NOT rotate) ========== */
            /* Spinner icon - rotates */
            [data-testid="stSpinner"] > div:first-child {
                animation: spin 1s linear infinite !important;
            }
            
            /* Spinner text - does NOT rotate */
            [data-testid="stSpinner"] > div:last-child {
                animation: none !important;
                transform: none !important;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    """, unsafe_allow_html=True)
