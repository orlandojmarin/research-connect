# ORLANDO
# profile.py
# Profile page where users can view, edit, and delete their account
# Admins can also manage user roles through the Admin tab

import streamlit as st
from utils.auth_utils import delete_self_account, go, db, firebaseConfig
from utils.profile_utils import (
    get_user_profile, delete_user_data, update_user_profile,
    get_all_users, update_user_role, count_admins
)
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

def render_danger_zone(uid):
    """Render the account deletion section.
    
    Args:
        uid (str): User ID
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
        
        col_yes, col_no = st.columns([1, 1])
        with col_yes:
            if st.button("Confirm Delete Account", type="primary", key="confirm_delete_account"):
                with st.spinner("Deleting account..."):
                    try:
                        # Delete user data from Firebase
                        delete_user_data(uid)
                        
                        # Clear session and redirect to landing
                        st.success("Your account has been deleted.")
                        st.session_state.user = None
                        st.session_state.delete_account_confirm = False
                        go("landing")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete account: {e}")
        with col_no:
            if st.button("Cancel", key="cancel_delete_account"):
                st.session_state.delete_account_confirm = False
                st.rerun()
    else:
        if st.button("Delete My Account", type="primary"):
            st.session_state.delete_account_confirm = True
            st.rerun()

def render_admin_user_management():
    """Render the admin interface for managing user roles."""
    st.header("👑 User Role Management")
    st.markdown("As an admin, you can view and modify user roles across the platform.")
    
    # Safety notice
    st.info("⚠️ **Safety Rule**: At least 2 admin accounts must exist at all times. "
            "You cannot demote an admin if only 2 admins remain.")
    
    # Fetch all users
    all_users = get_all_users()
    
    if not all_users:
        st.info("No users found in the database.")
        return
    
    # Sort users by role first (admin, faculty, student), then by name alphabetically
    role_priority = {"admin": 0, "faculty": 1, "student": 2}
    all_users.sort(key=lambda x: (
        role_priority.get(x.get('role', 'student'), 3),  # Sort by role priority first
        x.get('name', '').lower()  # Then by name alphabetically
    ))
    
    # Initialize session state for editing
    if "editing_user_role" not in st.session_state:
        st.session_state.editing_user_role = None
    
    # Filters row
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search users by name or email", placeholder="Type to filter users...")
    
    with col2:
        role_filter = st.selectbox(
            "Filter by Role",
            options=["All Roles", "Admin", "Faculty", "Student"],
            index=0
        )
    
    # Filter users based on search and role
    filtered_users = all_users
    
    # Apply search filter
    if search_term:
        filtered_users = [
            user for user in filtered_users 
            if search_term.lower() in user.get('name', '').lower() 
            or search_term.lower() in user.get('email', '').lower()
        ]
    
    # Apply role filter
    if role_filter != "All Roles":
        role_map = {"Admin": "admin", "Faculty": "faculty", "Student": "student"}
        filtered_users = [
            user for user in filtered_users
            if user.get('role', 'student') == role_map[role_filter]
        ]
    
    # Count admins (for safety check)
    total_admin_count = sum(1 for user in all_users if user.get('role') == 'admin')
    
    # Display count with breakdown
    if role_filter == "All Roles":
        admin_count = sum(1 for u in all_users if u.get('role') == 'admin')
        faculty_count = sum(1 for u in all_users if u.get('role') == 'faculty')
        student_count = sum(1 for u in all_users if u.get('role') == 'student')
        st.caption(f"Showing {len(filtered_users)} of {len(all_users)} users "
                  f"({admin_count} admins, {faculty_count} faculty, {student_count} students)")
    else:
        st.caption(f"Showing {len(filtered_users)} {role_filter.lower()}(s)")
    
    # Display users in cards
    for idx, user in enumerate(filtered_users):
        uid = user.get('uid')
        
        # Skip if no UID
        if not uid:
            continue
        
        # Check if this user is being edited
        is_editing = st.session_state.editing_user_role == uid
        
        with st.container(border=True):
            if is_editing:
                # Edit mode
                st.subheader(f"Editing: {user.get('name', 'Unknown')}")
                
                with st.form(key=f"edit_role_form_{uid}"):
                    st.write(f"**Email:** {user.get('email', 'N/A')}")
                    st.write(f"**Current Role:** {user.get('role', 'student')}")
                    
                    # Role selector
                    current_role = user.get('role', 'student')
                    role_options = ["student", "faculty", "admin"]
                    current_index = role_options.index(current_role) if current_role in role_options else 0
                    
                    new_role = st.selectbox(
                        "New Role *",
                        options=role_options,
                        index=current_index,
                        key=f"role_select_{uid}"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    
                    with col_save:
                        submit_role = st.form_submit_button("💾 Save Role", type="primary", use_container_width=True)
                    
                    with col_cancel:
                        cancel_role = st.form_submit_button("❌ Cancel", use_container_width=True)
                
                # Handle form submission
                if submit_role:
                    if new_role == current_role:
                        st.info("No changes made - role is the same.")
                    else:
                        # Safety check: prevent demoting admin if only 2 admins remain
                        if current_role == "admin" and new_role != "admin":
                            if total_admin_count <= 2:
                                st.error("❌ **Cannot demote this admin!**\n\n"
                                        f"Only {total_admin_count} admin(s) currently exist. "
                                        "At least 2 admins must remain for safety.\n\n"
                                        "**To proceed:** First promote another user to admin, "
                                        "then you can demote this user.")
                            else:
                                # Safe to demote - more than 2 admins exist
                                try:
                                    update_user_role(uid, new_role)
                                    st.success(f"✅ Role updated successfully! {user.get('name', 'User')} is now a {new_role}.")
                                    st.session_state.editing_user_role = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Failed to update role: {e}")
                        else:
                            # Not demoting an admin, or promoting someone - safe to proceed
                            try:
                                update_user_role(uid, new_role)
                                st.success(f"✅ Role updated successfully! {user.get('name', 'User')} is now a {new_role}.")
                                st.session_state.editing_user_role = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Failed to update role: {e}")
                
                if cancel_role:
                    st.session_state.editing_user_role = None
                    st.rerun()
            
            else:
                # Display mode
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Name with role badge
                    role = user.get('role', 'student')
                    role_emoji = {"admin": "👑", "faculty": "🍎", "student": "🎓"}
                    role_color = {"admin": "red", "faculty": "blue", "student": "green"}
                    
                    st.subheader(user.get('name', 'Unknown'))
                    st.markdown(f":{role_color[role]}[{role_emoji[role]} {role.title()}]")
                    st.write(f"**Email:** {user.get('email', 'N/A')}")
                    
                    # Format account creation date
                    created_at = user.get('created_at', 'N/A')
                    if created_at != 'N/A':
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            dt = dt.astimezone()
                            created_display = dt.strftime('%B %d, %Y')
                            st.write(f"**Joined:** {created_display}")
                        except:
                            st.write(f"**Joined:** {created_at}")
                
                with col2:
                    # Edit button with conditional warning for last admins
                    if user.get('role') == 'admin' and total_admin_count <= 2:
                        st.caption("⚠️ Protected")
                        if st.button("✏️ View", key=f"edit_role_{uid}_{idx}", use_container_width=True):
                            st.session_state.editing_user_role = uid
                            st.rerun()
                    else:
                        if st.button("✏️ Edit Role", key=f"edit_role_{uid}_{idx}", use_container_width=True):
                            st.session_state.editing_user_role = uid
                            st.rerun()

def main():
    """Main function to render the Profile page."""
    # Verify user_info and role are available
    if not user_info or 'role' not in user_info:
        st.error("Unable to load user information. Please log out and log in again.")
        st.stop()
    
    profile_data = get_user_profile(user_info['uid'])
    
    # Handle missing profile data
    if not profile_data:
        st.warning("No profile data found in database.")
        st.info("Your authentication account exists, but your profile data is missing.")
        st.stop()
    
    # Show tabs for admin, single page for others
    if user_info['role'] == "admin":
        tab1, tab2 = st.tabs(["👤 Profile", "👑 Admin"])
        
        with tab1:
            render_profile_header()
            render_account_info(profile_data, user_info['uid'])
            render_danger_zone(user_info['uid'])
        
        with tab2:
            render_admin_user_management()
    else:
        # Faculty and students see only their profile
        render_profile_header()
        render_account_info(profile_data, user_info['uid'])
        render_danger_zone(user_info['uid'])

if __name__ == "__main__":
    main()

#-----END OF FILE-----