# ORLANDO (UI) 
# SANA (Authentication Functionality)
# Updated with email verification, custom action handler, and password reset
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py
# firebase action URLs: http://localhost:8501 or https://researchconnect.streamlit.app

import streamlit as st
from datetime import datetime
from utils.home_utils import (
    get_quick_actions, get_feature_descriptions, initialize_session_state,
    render_landing, render_signup, render_login, render_forgot_password,
    render_verify_email, render_email_verification_handler, render_password_reset_handler
)
from utils.profile_utils import get_user_profile
from utils.general_utils import render_sidebar_auth, render_theme_tip

# ----- DYNAMIC PAGE CONFIG -----
def configure_page():
    """Set the Streamlit page configuration with dynamic layout based on auth state."""
    # Check if user is logged in
    if "user" not in st.session_state:
        st.session_state.user = None
    
    # Set layout based on authentication state
    layout = "wide" if st.session_state.user is not None else "centered"
    
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
            user_name = profile["name"].split()[0]

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
    """Gate access based on authentication state and handle sidebar visibility."""

    # Check if user clicked verification link or password reset link in email
    query_params = st.query_params
    mode = query_params.get("mode")
    oob_code = query_params.get("oobCode")
    
    # Handle email verification from link
    if mode == "verifyEmail" and oob_code:
        hide_sidebar()
        render_email_verification_handler(oob_code)
        st.stop()
    
    # Handle password reset from link
    if mode == "resetPassword" and oob_code:
        hide_sidebar()
        render_password_reset_handler(oob_code)
        st.stop()

    # Ensure session keys exist
    if "user" not in st.session_state:
        st.session_state.user = None
    if "page" not in st.session_state:
        st.session_state.page = "landing"

    # If not logged in, hide sidebar and render auth screens
    if st.session_state.user is None:
        hide_sidebar() 
        page = st.session_state.page
        if page == "landing":
            render_landing()
        elif page == "signup":
            render_signup()
        elif page == "login":
            render_login()
        elif page == "forgot_password":
            render_forgot_password()
        st.stop()

    # Check if email is verified
    user_session = st.session_state.user
    if not user_session.get("email_verified", False):
        hide_sidebar()
        render_verify_email()
        st.stop()

    # If logged in and verified, show sidebar with logout
    with st.sidebar:
        render_sidebar_auth(show_role=True)
        st.divider()

        # Theme tip
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