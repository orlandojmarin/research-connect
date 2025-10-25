# ORLANDO
# Profile page where users can delete their account if needed

import streamlit as st
from utils.auth_utils import delete_self_account, go
from utils.profile_utils import get_user_profile, delete_user_data
from utils.general_utils import (
    auth_gate, get_current_user, configure_page,
    render_scsu_logo, render_sidebar_auth
)

# Configure page FIRST
configure_page(
    title="My Profile | ResearchConnect SCSU",
    icon="👤",
    layout="centered"
)

# Auth gate
auth_gate()

# Get user info
user_info = get_current_user()

# Sidebar
render_scsu_logo()
with st.sidebar:
    render_sidebar_auth(show_role=True)

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

def main():
    """Main function to render the Profile page."""
    render_profile_header()
    
    # Fetch profile info
    profile_data = get_user_profile(user_info['uid'])
    
    if not profile_data:
        st.warning("No profile data found in database.")
        st.info("Your authentication account exists, but your profile data is missing. Let's fix that!")
        
        # Create profile restoration form
        with st.form("restore_profile"):
            st.write("**Enter your information to restore your profile:**")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            submit = st.form_submit_button("Restore Profile")
            
            if submit:
                if first_name and last_name:
                    from datetime import datetime
                    from utils.auth_utils import db
                    
                    # Determine role based on email
                    admin_emails = (
                        "marino1@southernct.edu",
                        "engt1@southernct.edu",
                        "muneerb1@southernct.edu"
                    )
                    role = "admin" if user_info['email'].lower() in admin_emails else "student"
                    
                    # Recreate profile data
                    db.child("users").child(user_info['uid']).set({
                        "email": user_info['email'],
                        "name": f"{first_name} {last_name}".strip(),
                        "role": role,
                        "created_at": datetime.utcnow().isoformat() + "Z",
                    })
                    
                    st.success("✅ Profile restored! Refreshing page...")
                    st.rerun()
                else:
                    st.error("Please enter both first and last name.")
        st.stop()
    
    # Render sections
    render_account_info(profile_data)
    render_danger_zone(user_info['uid'], user_info['idToken'])

if __name__ == "__main__":
    main()

#-----END OF FILE-----