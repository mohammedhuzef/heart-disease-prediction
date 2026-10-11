"""
CardioCheck — Educational Clinical Decision-Support Web Application
Neo-Brutalist UI/UX Design for Heart-Disease Risk Prediction
"""

from pathlib import Path
import joblib
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

APP_DIR = Path(__file__).parent.resolve()
MODEL_PATH = APP_DIR / "heart_disease_model.pkl"

st.set_page_config(
    page_title="CardioCheck | Heart Risk Decision Support",
    page_icon="♥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom minimal CSS for Streamlit wrapper
st.markdown(
    """
    <style>
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    .block-container {
        padding: 0rem 0rem 1rem 0rem !important;
        max-width: 100% !important;
    }
    .stApp {
        background-color: #F7F3E8;
    }
    iframe {
        border: none !important;
        width: 100% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def load_estimator():
    """Load the trained Random Forest model once per session."""
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None

def get_bundled_html():
    """Read index.html, styles.css, and app.js and inline them for high-fidelity rendering."""
    index_file = APP_DIR / "index.html"
    css_file = APP_DIR / "styles.css"
    js_file = APP_DIR / "app.js"

    html_code = index_file.read_text(encoding="utf-8")
    css_code = css_file.read_text(encoding="utf-8")
    js_code = js_file.read_text(encoding="utf-8")

    # Inline CSS
    bundled = html_code.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>\n{css_code}\n</style>'
    )
    # Inline JS
    bundled = bundled.replace(
        '<script src="app.js"></script>',
        f'<script>\n{js_code}\n</script>'
    )
    return bundled

# Render the complete CardioCheck Neo-Brutalist Web Application
try:
    full_html = get_bundled_html()
    components.html(full_html, height=1250, scrolling=True)
except Exception as e:
    st.error(f"Error loading CardioCheck interface: {e}")
