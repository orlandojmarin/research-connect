# SANA (Authentication and all Functionality)
# ORLANDO (UI) 
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py

import streamlit as st
from datetime import datetime
from utils.auth_utils import (
    auth, db, sanitize_email, is_allowed_sc_su_email,
    strong_password, friendly_firebase_error,
    create_account, sign_in, logout, go
)
from utils.home_utils import (
    get_quick_actions, get_feature_descriptions,
    initialize_session_state
)
from utils.profile_utils import get_user_profile
from utils.general_utils import render_sidebar_auth, render_theme_tip 

from dotenv import load_dotenv
load_dotenv()

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

def render_theme_tip():
    """Render a tip message encouraging users to use the custom theme"""
    st.info("💡 **Tip:** For the best experience, use the Custom Theme!\n\n"
            'Menu -> Settings -> "Custom Theme"')

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
        st.stop()

    # If logged in, show sidebar with logout
    with st.sidebar:
        render_sidebar_auth(show_role=True)
        st.divider()

        # Theme tip
        render_theme_tip()

# ----- LANDING / LOGIN / SIGNUP -----
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

def render_landing():
    """Render the landing page with logo, title, and login/signup buttons."""
    st.write("")
    st.write("")

    # --- Title & subtitle remain full width and centered ---
    st.markdown("<h1 style='text-align: center;'>ResearchConnect SCSU</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px;'>Connecting Students with Research Opportunities</p>",
        unsafe_allow_html=True
    )
    st.write("")

    # --- Logo inside center column to control its width ---
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.image("images/logo.png", width="stretch")

    st.write("")

    # --- Buttons in the same column setup ---
    left, center, right = st.columns([1, 2, 1])
    with center:
        st.info("**Welcome!** Please log in or create an account to access ResearchConnect.")
        st.write("")
        if st.button("🔑 Log In", width="stretch"):
            go("login")
            st.rerun()
        st.write("")
        if st.button("✨ Create Account", width="stretch"):
            go("signup")
            st.rerun()


def render_signup():
    """Render the account creation page with form inputs and validation.
    
    Includes a back button to return to the landing page.
    """
    st.title("Create Account")

    # Back button
    if st.button("← Back"):
        go("landing")
        st.rerun()
    
    # Helpful information box
    st.info("📝 **Account Requirements:**\n"
            "- Use your SCSU email address (@southernct.edu)\n"
            "- Password must be at least 8 characters\n"
            "- Password must include both letters and numbers")
    
    # Form
    with st.form("signup_form"):
        col1, col2 = st.columns(2)
        first = col1.text_input("First name")
        last = col2.text_input("Last name")
        email_raw = col1.text_input("SCSU email address", placeholder="yourname@southernct.edu")
        password = col2.text_input("Password", type="password", 
                                   help="Must be at least 8 characters with letters and numbers")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create Account")

    if submitted:
        # Collect all validation errors
        errors = []
        
        email = sanitize_email(email_raw)
        
        # Validate email domain
        if not email:
            errors.append("❌ Please enter an email address.")
        elif not is_allowed_sc_su_email(email):
            errors.append("❌ Please use your SCSU email address (@southernct.edu).")
        
        # Validate password strength
        if not password:
            errors.append("❌ Please enter a password.")
        else:
            ok, msg = strong_password(password)
            if not ok:
                errors.append(f"❌ {msg}")
        
        # Validate password confirmation
        if password and confirm and password != confirm:
            errors.append("❌ Passwords do not match.")
        elif not confirm:
            errors.append("❌ Please confirm your password.")
        
        # Validate names
        if not first or not first.strip():
            errors.append("❌ Please enter your first name.")
        if not last or not last.strip():
            errors.append("❌ Please enter your last name.")
        
        # Display all errors or proceed with account creation
        if errors:
            st.error("**Please fix the following issues:**")
            for error in errors:
                st.error(error)
        else:
            try:
                create_account(email, password, first, last)
                st.session_state.account_created = True  # ✅ flag for next render
                st.rerun()  # triggers rerun so flag takes effect
            except Exception as e:
                st.error(friendly_firebase_error(e))

    # --- This part runs after rerun ---
    if st.session_state.get("account_created"):
        st.success("✅ Account created successfully! You can now log in below when you're ready.")
        st.balloons()
        if st.button("🔑 Go to Login", width="stretch"):
            st.session_state.account_created = False
            go("login")
            st.rerun()

def render_login():
    """Render the login page with form inputs and authentication handling.
    
    Includes a back button to return to the landing page.
    """
    st.title("Log In")
    if st.button("← Back"):
        go("landing")
        st.rerun()

    with st.form("login_form"):
        email_raw = st.text_input("SCSU email address", placeholder="yourname@southernct.edu")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log In")

    if submitted:
        # Collect validation errors
        errors = []
        
        email = sanitize_email(email_raw)
        
        if not email:
            errors.append("❌ Please enter your email address.")
        elif not is_allowed_sc_su_email(email):
            errors.append("❌ Please use your SCSU email address (@southernct.edu).")
        
        if not password:
            errors.append("❌ Please enter your password.")
        
        # Display validation errors or attempt login
        if errors:
            for error in errors:
                st.error(error)
        else:
            try:
                uid, token = sign_in(email, password)
                st.session_state.user = {"uid": uid, "email": email, "idToken": token}
                profile = db.child("users").child(uid).get().val() or {}
                st.session_state.user["role"] = profile.get("role", "student")
                go("home")
                st.rerun()
            except Exception as e:
                st.error(friendly_firebase_error(e))

# ----- RUN APP -----
if __name__ == "__main__":
    auth_gate()
    main()

#-----END OF FILE-----