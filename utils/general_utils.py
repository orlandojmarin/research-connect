# ORLANDO
# GENERAL UTILITIES
# Common functions used across multiple pages

import streamlit as st

def auth_gate():
    """
    Ensure user is logged in, redirect to home.py if not.
    Should be called at the top of every protected page.
    """
    if "user" not in st.session_state or st.session_state.user is None:
        st.switch_page("home.py")
        st.stop()

def get_current_user():
    """
    Get the current user's information from session state.
    
    Returns:
        dict: Dictionary containing uid, email, and role
        
    Example:
        user_info = get_current_user()
        print(user_info['email'])  # Access email
        print(user_info['uid'])    # Access user ID
        print(user_info['role'])   # Access role
    """
    if "user" not in st.session_state or st.session_state.user is None:
        return None
    
    user = st.session_state.user
    return {
        "uid": user.get("uid", ""),
        "email": user.get("email", ""),
        "role": user.get("role", "student"),
        "name": user.get("name", "")
    }

def render_sidebar_auth(show_role=False):
    """
    Render the standard sidebar authentication section with user info and logout button.
    
    Args:
        show_role (bool): Whether to display the user's role. Default is False.
    """
    user_info = get_current_user()
    if not user_info:
        return
    
    st.success(f"Logged in as {user_info['email']}")
    
    if show_role:
        st.caption(f"Role: {user_info['role']}")
    
    # Updated to use st.logout() instead of Firebase logout
    if st.button("🚪 Log Out", width="stretch"):
        # Clear session state
        st.session_state.user = None
        # Use Streamlit's native logout
        st.logout()

def configure_page(title, icon="🦉", layout="wide", sidebar_state="expanded"):
    """
    Configure Streamlit page settings with consistent defaults.
    Must be called BEFORE any other Streamlit commands.
    
    Args:
        title (str): Page title to display in browser tab
        icon (str): Page icon emoji. Default is "🦉"
        layout (str): Page layout - "wide" or "centered". Default is "wide"
        sidebar_state (str): Initial sidebar state - "expanded" or "collapsed". Default is "expanded"
    """
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout,
        initial_sidebar_state=sidebar_state
    )

def render_scsu_logo():
    """
    Render the SCSU logo in the sidebar.
    Call this at the top of your sidebar content.
    """
    st.logo("images/scsu_logo.jpg", size="large")

def render_theme_tip():
    """
    Render a tip message encouraging users to use the custom theme.
    Useful for the main home page or settings areas.
    """
    st.info("💡 **Tip:** For the best experience, use the Custom Theme!\n\n"
            'Menu -> Settings -> "Custom Theme"')

#-----END OF FILE-----