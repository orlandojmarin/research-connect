# ORLANDO

"""
Home utilities for ResearchConnect SCSU
Handles functionality and data management for the home page
Includes authentication page rendering functions
"""

import datetime
import streamlit as st
from utils.auth_utils import (
    db, sanitize_email, is_allowed_sc_su_email,
    strong_password, friendly_firebase_error,
    create_account, sign_in, logout, go,
    resend_verification_email, handle_verify_email_action,
    send_password_reset_email, handle_password_reset_action
)
from utils.profile_utils import get_user_profile


def get_quick_actions():
    """
    Define quick action buttons configuration
    
    Returns:
        list: List of quick action configurations
    """
    actions = [
        {
            "text": "🧠 Ask ResearchAI",
            "page": "pages/chatbot.py",
            "help": "Get instant answers about research opportunities"
        },
        {
            "text": "📋 Browse Research", 
            "page": "pages/listings.py",
            "help": "Explore current faculty-led projects"
        },
        {
            "text": "📚 Find Resources",
            "page": "pages/resources.py", 
            "help": "Discover campus support services"
        }
    ]
    return actions

def get_feature_descriptions():
    """
    Get detailed feature descriptions for the platform
    
    Returns:
        dict: Dictionary containing feature information
    """
    features = {
        "chatbot": {
            "title": "🧠 ResearchAI Chatbot",
            "subtitle": "Instant, intelligent assistance for all your research questions",
            "benefits": [
                "Ask about specific research opportunities",
                "Get guidance on application processes", 
                "Find information about faculty and their work",
                "Learn about internship and fellowship programs",
                "Discover campus support offices and services",
                "Available 24/7 to help you navigate your research journey"
            ]
        },
        "listings": {
            "title": "📋 Research Listings",
            "subtitle": "Comprehensive database of faculty-led research projects",
            "benefits": [
                "Browse opportunities by department or field",
                "Filter by research type and commitment level",
                "View detailed project descriptions",
                "Connect directly with faculty researchers", 
                "Find both undergraduate and graduate opportunities",
                "Updated regularly with new opportunities"
            ]
        },
        "resources": {
            "title": "📚 Campus Resources", 
            "subtitle": "Your comprehensive guide to SCSU's academic and career support services",
            "academic_support": [
                "Center for Academic Successs and Accessibility Services (CASAS)",
                "Mentor Academic Partnership (MAP) Program",
                "Faculty office hours",
                "Academic clubs", 
            ],
            "career_services": [
                "Office of Career and Professional Development",
                "Office for STEM Research and Innovation",
                "JOBSs Online Job Board",
                "Innovation Hub",
            ]
        }
    }
    return features

def initialize_session_state():
    """
    Initialize session state variables for the home page
    """
    if "home_visited" not in st.session_state:
        st.session_state.home_visited = True
        st.session_state.visit_time = datetime.datetime.now()

# ============================= AUTHENTICATION PAGES =============================

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

    # Forgot password link outside the form
    if st.button("🔑 Forgot Password?", use_container_width=False):
        go("forgot_password")
        st.rerun()

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

def render_forgot_password():
    """Render the forgot password page where users can request a reset email."""
    st.title("Forgot Password? 🔑")
    
    if st.button("← Back to Login"):
        go("login")
        st.rerun()
    
    st.info("**Enter your SCSU email address and we'll send you a password reset link.**\n\n"
            "The link will be valid for 1 hour.")
    
    with st.expander("📖 How to Add a Safe Sender in Outlook"):
        st.markdown("""
        **Step-by-step guide for Outlook:**
        
        1. Log into [Outlook Web](https://outlook.office.com) with your SCSU credentials
        2. Click the **Settings gear** (⚙️) in the top-right corner
        3. Click on **Junk email** under Mail settings
        4. Under **Safe senders and domains**, click **Add**
        5. Paste: `noreply@researchconnect-scsu-474217.firebaseapp.com`
        6. Click **Save**
        7. Return to this page and request your reset email
        
        **Why is this necessary?**  
        Outlook's security system may block emails from new senders. Adding this address to your 
        Safe Senders ensures the password reset email reaches your inbox immediately.
        """)
    
    with st.form("forgot_password_form"):
        email_raw = st.text_input("SCSU Email Address", placeholder="yourname@southernct.edu")
        submit = st.form_submit_button("📧 Send Reset Link", type="primary", use_container_width=True)
    
    if submit:
        email = sanitize_email(email_raw)
        
        if not email:
            st.error("❌ Please enter your email address.")
        elif not is_allowed_sc_su_email(email):
            st.error("❌ Please use your SCSU email address (@southernct.edu).")
        else:
            with st.spinner("Sending password reset email..."):
                success, message = send_password_reset_email(email)
            
            if success:
                st.success(f"✅ {message}")
                st.info("📧 **Check Your Email**\n\n"
                        f"We've sent a password reset link to **{email}**.\n\n"
                        "**Next Steps:**\n"
                        "1. Check your SCSU email inbox (should arrive within 1-2 minutes)\n"
                        "2. Click the reset link in the email\n"
                        "3. Enter your new password\n"
                        "4. Return here to log in\n\n"
                        "**Didn't receive it?** Check your spam folder or ensure you added the sender "
                        "to your Safe Senders list (see instructions above).")
            else:
                st.error(f"❌ {message}")

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

def render_password_reset_handler(oob_code: str):
    """Handle password reset when user clicks link in email"""
    
    st.title("Reset Your Password 🔑")
    
    st.info("**Enter your new password below.**\n\n"
            "Your password must be at least 8 characters and include both letters and numbers.")
    
    with st.form("reset_password_form"):
        new_password = st.text_input(
            "New Password *",
            type="password",
            placeholder="Enter your new password"
        )
        
        confirm_password = st.text_input(
            "Confirm New Password *",
            type="password",
            placeholder="Re-enter your new password"
        )
        
        submit = st.form_submit_button("🔒 Reset Password", type="primary", use_container_width=True)
    
    if submit:
        # Validation
        errors = []
        
        if not new_password:
            errors.append("❌ Please enter a new password.")
        if not confirm_password:
            errors.append("❌ Please confirm your new password.")
        
        if new_password and confirm_password and new_password != confirm_password:
            errors.append("❌ Passwords do not match.")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            with st.spinner("Resetting your password..."):
                success, message, email = handle_password_reset_action(oob_code, new_password)
            
            if success:
                st.success(f"✅ {message}")
                st.balloons()
                
                st.info("🎉 **Password Reset Complete!**\n\n"
                        "Your password has been successfully changed.\n\n"
                        "Redirecting you to the login page...")
                
                # Clear query params and redirect to login
                st.query_params.clear()
                st.session_state.user = None
                st.session_state.page = "login"
                
                import time
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"❌ {message}")
                
                # Show helpful guidance based on error
                if "expired" in message.lower():
                    st.warning("**This reset link has expired.**\n\n"
                              "Password reset links are valid for 1 hour.\n\n"
                              "Please request a new password reset link from the login page.")
                    
                    if st.button("🔑 Go to Login", use_container_width=True, type="primary"):
                        st.query_params.clear()
                        st.session_state.user = None
                        st.session_state.page = "login"
                        st.rerun()
                
                elif "invalid" in message.lower() or "already been used" in message.lower():
                    st.warning("**This reset link is invalid or has already been used.**\n\n"
                              "You may have already reset your password, or the link may be incorrect.\n\n"
                              "Try logging in with your current password, or request a new reset link.")
                    
                    if st.button("🔑 Go to Login", use_container_width=True, type="primary"):
                        st.query_params.clear()
                        st.session_state.user = None
                        st.session_state.page = "login"
                        st.rerun()

#-----END OF FILE-----