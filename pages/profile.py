# ORLANDO
# Profile page where users can view, edit, and delete their account

import streamlit as st
from utils.auth_utils import delete_self_account, go
from utils.profile_utils import get_user_profile, delete_user_data, update_user_profile
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

def render_account_info(profile_data, uid):
    """Render the account information section with edit capability.
    
    Args:
        profile_data (dict): User profile data from Firebase
        uid (str): User ID
    """
    # Format the created_at timestamp
    created_at_raw = profile_data.get('created_at', 'N/A')
    if created_at_raw != 'N/A':
        try:
            from datetime import datetime
            # Parse ISO format timestamp
            dt = datetime.fromisoformat(created_at_raw.replace('Z', '+00:00'))
            # Convert UTC to local timezone
            dt = dt.astimezone()
            # Format as human-readable date
            created_at_display = dt.strftime('%B %d, %Y at %I:%M %p')
        except Exception:
            created_at_display = created_at_raw
    else:
        created_at_display = 'N/A'
    
    # Initialize edit mode state
    if "edit_profile_mode" not in st.session_state:
        st.session_state.edit_profile_mode = False
    
    with st.container(border=True):
        st.subheader("Account Information")
        
        # Edit Profile Button
        if not st.session_state.edit_profile_mode:
            # Display mode
            st.write(f"**Name:** {profile_data.get('name', 'N/A')}")
            st.write(f"**Email:** {profile_data.get('email', 'N/A')}")
            st.write(f"**Role:** {profile_data.get('role', 'student')}")
            st.write(f"**Account Created:** {created_at_display}")
            
            if st.button("✏️ Edit Profile", key="edit_profile_btn"):
                st.session_state.edit_profile_mode = True
                st.rerun()
        else:
            # Edit mode
            st.info("✏️ **Editing Profile** - Update your information below")
            
            # Get current name parts
            current_name = profile_data.get('name', '')
            name_parts = current_name.split(' ', 1)
            current_first = name_parts[0] if len(name_parts) > 0 else ''
            current_last = name_parts[1] if len(name_parts) > 1 else ''
            
            with st.form("edit_profile_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    new_first_name = st.text_input(
                        "First Name",
                        value=current_first,
                        placeholder="Enter your first name"
                    )
                
                with col2:
                    new_last_name = st.text_input(
                        "Last Name", 
                        value=current_last,
                        placeholder="Enter your last name"
                    )
                
                # Display non-editable fields
                st.text_input("Email (cannot be changed)", value=profile_data.get('email', 'N/A'), disabled=True)
                st.text_input("Role (cannot be changed)", value=profile_data.get('role', 'student'), disabled=True)
                
                col_save, col_cancel = st.columns(2)
                
                with col_save:
                    submit_edit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                
                with col_cancel:
                    cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            # Handle form submission
            if submit_edit:
                # Collect all validation errors
                errors = []
                
                if not new_first_name or not new_first_name.strip():
                    errors.append("❌ First name cannot be empty.")
                if not new_last_name or not new_last_name.strip():
                    errors.append("❌ Last name cannot be empty.")
                
                # Display all errors or proceed with update
                if errors:
                    st.error("**Please fix the following issues:**")
                    for error in errors:
                        st.error(error)
                else:
                    # Update profile
                    new_full_name = f"{new_first_name.strip()} {new_last_name.strip()}"
                    
                    try:
                        update_user_profile(uid, {"name": new_full_name})
                        st.success("✅ Profile updated successfully!")
                        st.session_state.edit_profile_mode = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to update profile: {e}")
            
            if cancel_edit:
                st.session_state.edit_profile_mode = False
                st.rerun()

def render_danger_zone(uid, id_token):
    """Render the account deletion section.
    
    Args:
        uid (str): User ID
        id_token (str): Firebase ID token
    """
    st.divider()
    st.subheader("⚠️ Danger Zone")
    st.write("Deleting your account will remove all of your data permanently. This action cannot be undone.")
    
    # Initialize session state for confirmation if not present
    if "delete_account_confirm" not in st.session_state:
        st.session_state.delete_account_confirm = False
    
    # If confirmation is active
    if st.session_state.delete_account_confirm:
        st.warning("⚠️ **Are you sure you want to delete your account?** This action cannot be undone!")
        st.write("**Please enter your password to confirm:**")
        
        password = st.text_input("Password", type="password", key="delete_password_confirm")
        
        col_yes, col_no = st.columns([1, 1])
        with col_yes:
            if st.button("Confirm Delete Account", type="primary", key="confirm_delete_account"):
                if not password:
                    st.error("Please enter your password to confirm deletion.")
                else:
                    with st.spinner("Deleting account..."):
                        try:
                            # Re-authenticate to get a fresh token
                            from utils.auth_utils import auth
                            user = st.session_state.get("user")
                            email = user.get("email")
                            
                            # Sign in again to get fresh token
                            fresh_user = auth.sign_in_with_email_and_password(email, password)
                            fresh_token = fresh_user["idToken"]
                            
                            # Delete user data and account
                            delete_user_data(uid)
                            delete_self_account(fresh_token)
                            
                            st.success("Your account has been deleted.")
                            st.session_state.user = None
                            st.session_state.delete_account_confirm = False
                            go("landing")
                            st.rerun()
                        except Exception as e:
                            error_msg = str(e)
                            if "INVALID_PASSWORD" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
                                st.error("Incorrect password. Please try again.")
                            else:
                                st.error(f"Failed to delete account: {e}")
        with col_no:
            if st.button("Cancel", key="cancel_delete_account"):
                st.session_state.delete_account_confirm = False
                st.rerun()
    else:
        if st.button("Delete My Account", type="primary"):
            st.session_state.delete_account_confirm = True
            st.rerun()

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
    render_account_info(profile_data, user_info['uid'])
    render_danger_zone(user_info['uid'], user_info['idToken'])

if __name__ == "__main__":
    main()

#-----END OF FILE-----