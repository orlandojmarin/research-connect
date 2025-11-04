# ORLANDO (UI) 
# SANA (Authentication Functionality)
# Updated with email verification and custom action handler
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py
# firebase action URLs: http://localhost:8501 or https://researchconnect.streamlit.app

import streamlit as st
from datetime import datetime
from utils.auth_utils import (
    db, sanitize_email, is_allowed_sc_su_email,
    strong_password, friendly_firebase_error,
    create_account, sign_in, logout, go,
    check_email_verified, resend_verification_email,
    handle_verify_email_action
)
from utils.home_utils import (
    get_quick_actions, get_feature_descriptions,
    initialize_session_state
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

    # Check if user clicked verification link in email
    query_params = st.query_params
    mode = query_params.get("mode")
    oob_code = query_params.get("oobCode")
    
    # Handle email verification from link
    if mode == "verifyEmail" and oob_code:
        hide_sidebar()
        render_email_verification_handler(oob_code)
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

# ----- EMAIL VERIFICATION HANDLER -----
def render_email_verification_handler(oob_code: str):
    """Handle email verification when user clicks link in email"""
    
    st.title("Email Verification ✉️")
    
    with st.spinner("Verifying your email..."):
        success, message, email = handle_verify_email_action(oob_code)
    
    if success:
        # SUCCESS - Automatically redirect to login page
        st.success(f"✅ {message}")
        st.balloons()
        
        # Show brief confirmation message
        st.info("🎉 **Your email has been successfully verified!**\n\n"
                "Redirecting you to the login page...")
        
        # CRITICAL FIX: Clear query params FIRST, then redirect
        # This prevents the verification handler from running again
        st.query_params.clear()
        st.session_state.user = None
        st.session_state.page = "login"
        
        # Add a small delay so users can see the success message
        import time
        time.sleep(2)
        st.rerun()
            
    else:
        # FAILURE - Handle different error scenarios
        st.error("❌ Email Verification Failed")
        
        # Provide context-specific guidance based on the error
        if "already been used" in message.lower() or "invalid" in message.lower():
            st.warning("**This verification link has already been used or is invalid.**\n\n"
                      "Your email may already be verified! Try logging in with your credentials.")
            
            # Direct to login for already-verified users
            if st.button("🔑 Go to Login", width="stretch", type="primary"):
                # CRITICAL FIX: Clear query params FIRST
                st.query_params.clear()
                st.session_state.user = None
                st.session_state.page = "login"
                st.rerun()
                
        elif "expired" in message.lower():
            st.warning("**This verification link has expired.**\n\n"
                      "Verification links are valid for 24 hours.\n\n"
                      "**What to do next:**\n"
                      "1. Go to the login page\n"
                      "2. Enter your credentials\n"
                      "3. You'll be prompted to request a new verification email if needed")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔑 Go to Login", width="stretch", type="primary"):
                    # CRITICAL FIX: Clear query params FIRST
                    st.query_params.clear()
                    st.session_state.user = None
                    st.session_state.page = "login"
                    st.rerun()
            with col2:
                if st.button("✨ Create New Account", width="stretch"):
                    # CRITICAL FIX: Clear query params FIRST
                    st.query_params.clear()
                    st.session_state.user = None
                    st.session_state.page = "signup"
                    st.rerun()
        else:
            # Generic error - show both options
            st.warning("**Unable to verify your email at this time.**\n\n"
                      f"Error details: {message}\n\n"
                      "**What to do next:**\n"
                      "- Try logging in (you may already be verified)\n"
                      "- If you can't log in, request a new verification email")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔑 Go to Login", width="stretch", type="primary"):
                    # CRITICAL FIX: Clear query params FIRST
                    st.query_params.clear()
                    st.session_state.user = None
                    st.session_state.page = "login"
                    st.rerun()
            with col2:
                if st.button("✨ Create New Account", width="stretch"):
                    # CRITICAL FIX: Clear query params FIRST
                    st.query_params.clear()
                    st.session_state.user = None
                    st.session_state.page = "signup"
                    st.rerun()


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
    """Render the account creation page with form inputs and validation."""
    st.title("Create Account")

    # Back button
    if st.button("← Back"):
        go("landing")
        st.rerun()
    
    # Simplified email verification instructions
    st.warning("📧 **Important: Before Creating Your Account**\n\n"
               "To ensure you receive the verification email, add this email to your Outlook Safe Senders:\n\n"
               "`noreply@researchconnect-scsu-474217.firebaseapp.com`\n\n")
    
    with st.expander("📖 How to Add a Safe Sender in Outlook"):
        st.markdown("""
        **Step-by-step guide for Outlook:**
        
        1. Log into [Outlook Web](https://outlook.office.com) with your SCSU credentials
        2. Click the **Settings gear** (⚙️) in the top-right corner
        3. Click on **Junk email** under Mail settings
        4. Under **Safe senders and domains**, click **Add**
        5. Paste: `noreply@researchconnect-scsu-474217.firebaseapp.com`
        6. Click **Save**
        7. Return to this page and create your account
        
        **Why is this necessary?**  
        Outlook's security system may block emails from new senders. Adding this address to your 
        Safe Senders ensures the verification email reaches your inbox immediately.
        """)
    
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
                uid, id_token = create_account(email, password, first, last)
                st.session_state.verification_email = email
                st.session_state.account_created = True
                st.rerun()
            except Exception as e:
                st.error(friendly_firebase_error(e))

    # --- This part runs after rerun ---
    if st.session_state.get("account_created"):
        st.success("✅ Account created successfully!")
        st.balloons()
        st.info("📧 **Verification Email Sent!**\n\n"
                f"We've sent a verification email to **{st.session_state.get('verification_email')}**.\n\n"
                "**Next Steps:**\n"
                "1. Check your SCSU email inbox (should arrive within 1-2 minutes)\n"
                "2. Click the verification link in the email\n"
                "3. You'll be automatically redirected to the login page\n"
                "4. Log in with your credentials to access ResearchConnect\n\n"
                "**Didn't receive it?** Wait a few minutes, then check your spam folder. "
                "You can also request a new verification email after attempting to log in.")

def render_login():
    """Render the login page with form inputs and authentication handling."""
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
                uid, token, email_verified = sign_in(email, password)
                
                # Get user profile using Firebase Admin SDK syntax
                user_ref = db.child("users").child(uid)
                profile = user_ref.get() or {}
                
                # Store in session
                st.session_state.user = {
                    "uid": uid,
                    "email": email,
                    "idToken": token,
                    "role": profile.get("role", "student"),
                    "email_verified": email_verified
                }
                
                go("home")
                st.rerun()
                
            except Exception as e:
                st.error(friendly_firebase_error(e))

def render_verify_email():
    """Render the email verification page."""
    st.title("Verify Your Email 📧")

    user_session = st.session_state.user
    email = user_session.get("email", "")

    st.warning(f"Please verify your email address to continue.\n\nVerification will be sent to **{email}**")

    st.info(
        "📬 **Check Your Email:**\n\n"
        "1. Look for an email from `noreply@researchconnect-scsu-474217.firebaseapp.com`\n"
        "2. Click the verification link in the email\n"
        "3. A new tab will open to confirm verification\n"
        "4. Close that tab and log in again here\n\n"
        "**Tip:** If you don't see the email, check your spam folder or add the sender "
        "to your Safe Senders list and request a new verification email below."
    )
    
    with st.expander("📖 How to Add a Safe Sender in Outlook"):
        st.markdown("""
        **Step-by-step guide for Outlook:**
        
        1. Log into [Outlook Web](https://outlook.office.com) with your SCSU credentials
        2. Click the **Settings gear** (⚙️) in the top-right corner
        3. Click on **Junk email** under Mail settings
        5. Under **Safe senders and domains**, click **Add**
        6. Paste: `noreply@researchconnect-scsu-474217.firebaseapp.com`
        7. Click **Save**
        8. Return to this page and create your account
        
        **Why is this necessary?**  
        Outlook's security system may block emails from new senders. Adding this address to your 
        Safe Senders ensures the verification email reaches your inbox immediately.
        """)

    st.divider()
    st.subheader("Resend Verification Email")

    # FIXED: Capture password INSIDE the form submit check
    with st.form("resend_form", clear_on_submit=False):  # Don't clear on submit
        st.caption("Enter your password to receive a new verification email")
        resend_pwd = st.text_input("Password", type="password", key="resend_pwd")
        resend_submit = st.form_submit_button("📧 Resend Verification Email", width="stretch")
        
        # Process INSIDE the form context
        if resend_submit:
            if not resend_pwd:
                st.error("Please enter your password")
            else:
                with st.spinner("Sending verification email..."):
                    success, msg = resend_verification_email(email, resend_pwd)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    st.divider()

    if st.button("← Log Out"):
        logout()
        st.rerun()

# ----- RUN APP -----
if __name__ == "__main__":
    auth_gate()
    main()

#-----END OF FILE-----