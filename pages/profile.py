import streamlit as st
from utils.auth_utils import delete_self_account
from utils.profile_utils import get_user_profile, delete_user_data

# -------------------- SIDEBAR (Auth + Logout) --------------------
def render_sidebar():
    """Render the sidebar with user info and logout button."""
    user_session = st.session_state.get("user")
    if not user_session:
        st.warning("Not logged in.")
        return

    st.success(f"Logged in as {user_session['email']}")

    if st.button("Log Out"):
        st.session_state.user = None
        st.session_state.page = "landing"
        st.rerun()

#------------ TEST ABOVE--------

def render_profile():
    st.title("👤 My Profile")
    st.markdown("Here you can view your account information and manage your profile.")

    # Get UID from session
    user_session = st.session_state.get("user")
    if not user_session:
        st.error("You must be logged in to view this page.")
        st.stop()

    uid = user_session.get("uid")
    id_token = user_session.get("idToken")

    # Fetch profile info
    profile_data = get_user_profile(uid)

    if not profile_data:
        st.warning("No profile data found.")
        st.stop()

    # Display user info
    with st.container(border=True):
        st.subheader("Account Information")
        st.write(f"**Name:** {profile_data.get('name', 'N/A')}")
        st.write(f"**Email:** {profile_data.get('email', 'N/A')}")
        st.write(f"**Role:** {profile_data.get('role', 'student')}")
        st.write(f"**Account Created:** {profile_data.get('created_at', 'N/A')}")

    st.divider()

    # Delete account section
    st.subheader("⚠️ Danger Zone")
    st.write("Deleting your account will remove all of your data permanently. This action cannot be undone.")

    if st.button("Delete My Account", type="primary"):
        with st.spinner("Deleting account..."):
            try:
                delete_user_data(uid)
                delete_self_account(id_token)

                st.success("Your account has been deleted.")
                st.session_state.user = None
                st.session_state.page = "landing"
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete account: {e}")

def main():
    """Main function to render the Profile page"""
    st.logo("images/scsu_logo.jpg", size="large")
    
    st.set_page_config(page_title="My Profile | ResearchConnect SCSU", page_icon="👤", layout="centered")

    # Sidebar
    with st.sidebar:
        render_sidebar()
    
    render_profile()

if __name__ == "__main__":
    main()