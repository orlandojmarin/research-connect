# ORLANDO (UI) 
# SANA (Authentication Functionality)
# Updated with Microsoft OIDC authentication
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py or python -m streamlit run home.py

import streamlit as st
from datetime import datetime
from utils.home_utils import (
    get_quick_actions, get_feature_descriptions, initialize_session_state,
    render_landing, verify_scsu_email
)
from utils.profile_utils import get_user_profile
from utils.general_utils import render_sidebar_auth, render_theme_tip

# ----- DYNAMIC PAGE CONFIG -----
def configure_page():
    """Set the Streamlit page configuration with dynamic layout based on auth state."""
    # Default to centered (for landing page)
    layout = "centered"
    
    # Try to check if user is logged in
    try:
        if hasattr(st, 'user') and hasattr(st.user, 'is_logged_in'):
            if st.user.is_logged_in:
                layout = "wide"
    except (AttributeError, Exception):
        # If OAuth isn't initialized yet or any error occurs, use centered
        layout = "centered"
    
    st.set_page_config(
        page_title="ResearchConnect SCSU",
        page_icon="🦉",
        layout=layout,
        initial_sidebar_state="expanded"
    )

# Must be called FIRST before any other Streamlit commands
configure_page()

# --------- HOME PAGE ----------
def main():
    """Render the main home page with header, quick actions, features, and footer."""
    initialize_session_state()
    st.logo("images/scsu_logo.jpg", size="large")

    render_header()
    render_quick_actions()
    st.divider()
    render_features()
    render_footer()

def render_header():
    """Render the header section with title, logo, and personalized greeting."""
    st.title("Welcome to ResearchConnect 🦉")
    st.divider()

    # Center the logo
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("images/logo.png", width=700)

    # Personalized greeting
    user_session = st.session_state.get("user")
    user_name = ""

    if user_session:
        uid = user_session.get("uid")
        profile = get_user_profile(uid)
        if profile and "name" in profile:
            # Extract first name if full name exists
            full_name = profile["name"]
            # Handle "Last, First" format from Microsoft
            if "," in full_name:
                parts = full_name.split(",", 1)
                user_name = parts[1].strip()  # Get first name (second part)
            else:
                user_name = full_name.split()[0]  # Get first word

    # Construct greeting message
    if user_name:
        greeting_msg = f"👋 **Hi {user_name}, I'm ResearchAI! I can help you find research opportunities, connect with faculty, or answer questions about academic resources.**"
    else:
        greeting_msg = "👋 **Hi, I'm ResearchAI! I can help you find research opportunities, connect with faculty, or answer questions about academic resources.**"     

    st.success(greeting_msg)
    st.divider()

def render_quick_actions():
    """Render quick action buttons that navigate to different pages."""
    st.subheader("🚀 Quick Actions")
    actions = get_quick_actions()
    cols = st.columns(len(actions))
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(
                action["text"],
                width="stretch",
                help=action["help"]
            ):
                st.switch_page(action["page"])

def render_features():
    """Render the platform's feature sections (chatbot, listings, resources)."""
    st.subheader("🌟 Platform Features")
    features = get_feature_descriptions()

    # Chatbot
    with st.container(border=True):
        st.subheader(features["chatbot"]["title"])
        st.write(f"**{features['chatbot']['subtitle']}**")
        render_feature_list(features["chatbot"]["benefits"])

    # Listings
    with st.container(border=True):
        st.subheader(features["listings"]["title"])
        st.write(f"**{features['listings']['subtitle']}**")
        render_feature_list(features["listings"]["benefits"], icon="🔍")

    # Resources
    with st.container(border=True):
        st.subheader(features["resources"]["title"])
        st.write(f"**{features['resources']['subtitle']}**")
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Academic Support:**")
            for item in features["resources"]["academic_support"]:
                st.write(f"✏️ {item}")
        with col2:
            st.write("**Career Services:**")
            for item in features["resources"]["career_services"]:
                st.write(f"💼 {item}")

def render_feature_list(items, icon="✅"):
    """Render a two-column list of features or benefits with optional icons.
    
    Args:
        items (list): List of feature/benefit strings to display.
        icon (str): Optional emoji or symbol to prefix each item.
    """
    col1, col2 = st.columns(2)
    mid = len(items) // 2
    for i, col in enumerate([col1, col2]):
        with col:
            for benefit in items[i*mid:(i+1)*mid]:
                st.write(f"{icon} {benefit}")

def render_footer():
    """Render the footer section with app info and developer credits."""
    st.divider()
    st.info("**ResearchConnect SCSU** | Connecting Students with Research Opportunities")
    st.caption("Developed by Tatiana Eng, Orlando Marin, and Sana Muneer | CSC 400 Capstone Project")

# ----- AUTH GATE -----
def auth_gate():
    """Gate access based on Microsoft OIDC authentication."""
    
    # Initialize session state
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # Safely check if user is logged in via Microsoft
    try:
        is_logged_in = hasattr(st, 'user') and hasattr(st.user, 'is_logged_in') and st.user.is_logged_in
    except (AttributeError, Exception):
        is_logged_in = False
    
    # Check if user is logged in via Microsoft
    if not is_logged_in:
        hide_sidebar()
        render_landing()
        st.stop()
    
    # Verify SCSU email and create/update profile
    from utils.home_utils import verify_scsu_email
    if not verify_scsu_email():
        st.stop()
    
    # Show sidebar with logout
    with st.sidebar:
        render_sidebar_auth(show_role=True)
        st.divider()
        render_theme_tip()

# ----- SIDEBAR HIDING -----
def hide_sidebar():
    """Hide the Streamlit sidebar for landing, login, and signup pages."""
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            nav[data-testid="stSidebarNav"] { display: none !important; }
            button[kind="header"] { visibility: hidden; }
            .block-container { padding-left: 2rem; padding-right: 2rem; }
        </style>
        """,
        unsafe_allow_html=True
    )

# ----- RUN APP -----
if __name__ == "__main__":
    auth_gate()
    main()

#-----END OF FILE-----