# home_utils.py
# ORLANDO

"""
Home utilities for ResearchConnect SCSU
Handles functionality and data management for the home page
Includes authentication page rendering functions
"""

import datetime
import streamlit as st
from utils.auth_utils import db
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
    """Render the landing page with logo and Microsoft login."""
    st.write("")
    st.write("")

    st.markdown("<h1 style='text-align: center;'>ResearchConnect SCSU</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 18px;'>Connecting Students with Research Opportunities</p>",
        unsafe_allow_html=True
    )
    st.write("")

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.image("images/logo.png", width="stretch")

    st.write("")

    left, center, right = st.columns([1, 2, 1])
    with center:
        st.info("**Welcome!** Please log in with your SCSU account to access ResearchConnect.")
        st.write("")
        if st.button("🔑 Log In with SCSU Account", width="stretch", type="primary"):
            st.login("microsoft")

def verify_scsu_email():
    """Verify that the logged-in user has an SCSU email and create/update their profile."""
    if not st.user.is_logged_in:
        return False
    
    email = st.user.email
    
    # Check if it's an SCSU email
    if not email.endswith("@southernct.edu"):
        st.error("❌ **Access Denied**\n\nPlease sign in with your SCSU email address (@southernct.edu).")
        if st.button("Log Out", width="stretch"):
            st.logout()
        st.stop()
        return False
    
    # Get or create user profile in Firebase
    # Use email as a unique identifier (hash it for safety)
    import hashlib
    uid = hashlib.sha256(email.encode()).hexdigest()[:28]  # Create consistent UID from email
    
    user_ref = db.child("users").child(uid)
    profile = user_ref.get()
    
    # Determine role
    admin_emails = (
        "marino1@southernct.edu",
        "engt1@southernct.edu",
        "muneerb1@southernct.edu",
        "hossainm3@southernct.edu"
    )
    
    faculty_emails = (
        "abdelraoufa1@southernct.edu",
        "alseesis1@southernct.edu",
        "antoniosi1@southernct.edu",
        "elahia1@southernct.edu",
        "islamm2@southernct.edu",
        "kimc1@southernct.edu",
        "lancorl1@southernct.edu",
        "podnarh1@southernct.edu",
        "seyedt1@southernct.edu",
        "shetaa1@southernct.edu",
        "upretya1@southernct.edu",
        "wuh2@southernct.edu",
        "yuw1@southernct.edu",
        "pangy1@southernct.edu",
        "lockwoodh1@southernct.edu",
        "facultytest@southernct.edu"
    )
    
    if email.lower() in admin_emails:
        role = "admin"
    elif email.lower() in faculty_emails:
        role = "faculty"
    else:
        role = "student"
    
    # ✅ FIX: Parse name from Microsoft format "Last, First" → "First Last"
    display_name = st.user.name or email.split("@")[0]
    
    if "," in display_name:
        # Microsoft format: "Marin, Orlando" → "Orlando Marin"
        parts = display_name.split(",", 1)
        last_name = parts[0].strip()
        first_name = parts[1].strip()
        proper_name = f"{first_name} {last_name}"
    else:
        # Already in correct format or single name
        proper_name = display_name
    
    # Create or update profile
    if not profile:
        # First time login - create profile with parsed name
        user_ref.set({
            "email": email,
            "name": proper_name,  # ✅ Store properly formatted name
            "role": role,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "email_verified": True,  # Microsoft handles verification
            "last_login": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
    else:
        # Existing user - use name from database (preserves user edits)
        proper_name = profile.get("name", proper_name)
        
        # Update last_login only if this is a new session (not just page navigation)
        if "login_tracked" not in st.session_state:
            user_ref.update({
                "last_login": datetime.datetime.now(datetime.timezone.utc).isoformat()
            })
            st.session_state.login_tracked = True
    
    # Store in session
    st.session_state.user = {
        "uid": uid,
        "email": email,
        "role": role,
        "email_verified": True,
        "name": proper_name  # ✅ Use properly formatted name
    }
    
    return True

#-----END OF FILE-----