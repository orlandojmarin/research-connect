# ORLANDO
# Profile page where users can delete their account if needed

import streamlit as st
from utils.auth_utils import delete_self_account, go
from utils.profile_utils import get_user_profile, delete_user_data

# -------------------- PAGE CONFIG (MUST BE FIRST) --------------------
st.set_page_config(
    page_title="My Profile | ResearchConnect SCSU",
    page_icon="👤",
    layout="centered"
)

# -------------------- AUTH GATE --------------------
def auth_gate():
    """Ensure user is logged in, redirect to home if not."""
    if "user" not in st.session_state or st.session_state.user is None:
        st.switch_page("home.py")
        st.stop()

# -------------------- SIDEBAR --------------------
def render_sidebar():
    """Render the sidebar with user info and logout button."""
    st.logo("images/scsu_logo.jpg", size="large")
    
    with st.sidebar:
        user_session = st.session_state.get("user")
        st.success(f"Logged in as {user_session['email']}")
        
        st.divider()
        
        if st.button("Log Out"):
            st.session_state.user = None
            go("landing")
            st.rerun()

# -------------------- PROFILE CONTENT --------------------
def render_profile_header():
    """Render the profile page header."""
    st.title("👤 My Profile")
    st.markdown("Here you can view your account information and manage your profile.")

def render_account_info(profile_data):
    """Render the account information section.
    
    Args:
        profile_data (dict): User profile data from Firebase
    """
    with st.container(border=True):
        st.subheader("Account Information")
        st.write(f"**Name:** {profile_data.get('name', 'N/A')}")
        st.write(f"**Email:** {profile_data.get('email', 'N/A')}")
        st.write(f"**Role:** {profile_data.get('role', 'student')}")
        st.write(f"**Account Created:** {profile_data.get('created_at', 'N/A')}")

def render_danger_zone(uid, id_token):
    """Render the account deletion section.
    
    Args:
        uid (str): User ID
        id_token (str): Firebase ID token
    """
    st.divider()
    st.subheader("⚠️ Danger Zone")
    st.write("Deleting your account will remove all of your data permanently. This action cannot be undone.")
    
    if st.button("Delete My Account", type="primary"):
        with st.spinner("Deleting account..."):
            try:
                delete_user_data(uid)
                delete_self_account(id_token)
                
                st.success("Your account has been deleted.")
                st.session_state.user = None
                go("landing")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete account: {e}")

def render_profile_content():
    """Render the main profile page content."""
    render_profile_header()
    
    # Get user session data
    user_session = st.session_state.get("user")
    uid = user_session.get("uid")
    id_token = user_session.get("idToken")
    
    # Fetch profile info
    profile_data = get_user_profile(uid)
    
    if not profile_data:
        st.warning("No profile data found.")
        st.stop()
    
    # Render sections
    render_account_info(profile_data)
    render_danger_zone(uid, id_token)

# -------------------- MAIN --------------------
def main():
    """Main function to render the Profile page."""
    auth_gate()
    render_sidebar()
    render_profile_content()

if __name__ == "__main__":
    main()

#-----END OF FILE--------