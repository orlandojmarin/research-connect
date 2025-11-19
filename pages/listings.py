# TATIANA
# listings.py

import streamlit as st
from datetime import datetime
from utils.listings_utils import (
    initialize_listing_session_state,
    filter_listings,
    save_listing_to_firebase,
    get_all_listings_from_firebase,
    get_user_listings_from_firebase,
    delete_listing_from_firebase,
    get_user_favorite_listings,
    render_sidebar_filters,
    render_edit_form,
    render_listings,
    SKILLS_OPTIONS_SORTED
)
from utils.profile_utils import get_user_profile
from utils.general_utils import (
    auth_gate, get_current_user, configure_page,
    render_scsu_logo, render_sidebar_auth
)

# Configure page FIRST
configure_page(
    title="Research Opportunities 🔍",
    icon="🔍",
    layout="wide"
)

# Auth gate
auth_gate()

# Get user info
user_info = get_current_user()

# Sidebar
render_scsu_logo()
with st.sidebar:
    render_sidebar_auth(show_role=True)
    st.divider()


def render_page_header():
    """Render the main page header."""
    st.title("Research Opportunities 🔍")


def render_form_progress_bar():
    """Render the form progress bar and page indicator."""
    progress = 0.5 if st.session_state.form_page == 1 else 1.0
    st.progress(progress)
    st.caption(f"Page {st.session_state.form_page} of 2")
    st.write("")


def render_form_page1_fields(form_key, saved_data):
    """Render all input fields for form page 1 (Basic Information).
    
    Args:
        form_key: Unique key for form inputs
        saved_data: Dictionary of saved form data
        
    Returns:
        dict: Dictionary containing all page 1 form values
    """
    st.subheader("Basic Information")
    
    title = st.text_input(
        "Project Title *", 
        value=saved_data.get('title', ''), 
        placeholder="ex. Biometric Authentication in Smartphones", 
        key=f"title_input_{form_key}"
    )
    
    team = st.text_input(
        "Additional Collaborators", 
        value=saved_data.get('team', ''), 
        placeholder="ex. Grace Hopper, John von Neumann", 
        key=f"team_input_{form_key}"
    )
    
    # Department dropdown
    dept_options = ["Computer Science", "Data Science"]
    dept_default_index = dept_options.index(saved_data['department']) if saved_data.get('department') in dept_options else 0
    department = st.selectbox(
        "Department/Lab *", 
        options=dept_options, 
        index=dept_default_index, 
        key=f"dept_input_{form_key}"
    )
    
    openings = st.number_input(
        "Number of Openings *", 
        min_value=1, 
        max_value=10, 
        value=saved_data.get('openings', 1), 
        step=1, 
        key=f"openings_input_{form_key}"
    )
    
    start_date_default = saved_data.get('start_date', datetime.now().date())
    start_date = st.date_input(
        "Start Date *", 
        value=start_date_default, 
        key=f"start_date_input_{form_key}"
    )
    
    if start_date:
        st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
    else:
        st.caption("Please select a start date")
    
    # Duration dropdown
    duration_options = ["1 semester", "2 semesters", "More than 2 semesters"]
    duration_default_index = duration_options.index(saved_data['duration']) if saved_data.get('duration') in duration_options else 0
    duration = st.selectbox(
        "Duration *", 
        options=duration_options, 
        index=duration_default_index, 
        key=f"duration_input_{form_key}"
    )
    
    weekly_hours = st.number_input(
        "Number of Hours per Week *", 
        min_value=1, 
        value=saved_data.get('weekly_hours', 10),
        step=1, 
        key=f"hours_input_{form_key}"
    )
    
    return {
        'title': title,
        'team': team,
        'department': department,
        'openings': openings,
        'start_date': start_date,
        'duration': duration,
        'weekly_hours': weekly_hours
    }


def render_form_page2_fields(form_key, saved_data):
    """Render all input fields for form page 2 (Details & Compensation).
    
    Args:
        form_key: Unique key for form inputs
        saved_data: Dictionary of saved form data
        
    Returns:
        dict: Dictionary containing all page 2 form values
    """
    st.subheader("Details & Compensation")
    
    comp_index = None
    if saved_data.get('compensation_type') == 'Paid':
        comp_index = 0
    elif saved_data.get('compensation_type') == 'Unpaid':
        comp_index = 1
    
    compensation_type = st.radio(
        "Compensation Type *", 
        ["Paid", "Unpaid"], 
        index=comp_index, 
        key=f"comp_type_{form_key}"
    )
    
    pay_rate = st.number_input(
        "Hourly Pay Rate ($)",
        min_value=16.35,
        value=saved_data.get('pay_rate', 16.35),
        step=0.01,
        format="%.2f",
        key=f"pay_rate_input_{form_key}"
    )
    st.caption("Note: Pay rate will be displayed as N/A when compensation type is unpaid.")

    st.write("Skills Required *")
    skills = st.multiselect(
        "Select skills",
        options=SKILLS_OPTIONS_SORTED,
        default=saved_data.get('skills', []),
        placeholder="Select all that apply",
        label_visibility="collapsed",
        key=f"skills_input_{form_key}"
    )

    website_urls = st.text_input(
        "Website URL", 
        value=saved_data.get('website_urls', ''), 
        placeholder="ex. https://example.com", 
        key=f"website_input_{form_key}"
    )
    
    summary = st.text_area(
        "Summary/Description *", 
        value=saved_data.get('summary', ''), 
        key=f"summary_input_{form_key}"
    )
    
    st.write("Preferred Method of Communication *")
    communication = st.multiselect(
        "Select communication methods",
        options=["Email", "Teams"],
        default=saved_data.get('communication', []),
        placeholder="Select all that apply",
        label_visibility="collapsed",
        key=f"comm_input_{form_key}"
    )
    
    return {
        'compensation_type': compensation_type,
        'pay_rate': pay_rate,
        'skills': skills,
        'website_urls': website_urls,
        'summary': summary,
        'communication': communication
    }


def validate_listing_form(page1_data, page2_data):
    """Validate all required fields from both form pages.
    
    Args:
        page1_data: Dictionary of page 1 form data
        page2_data: Dictionary of page 2 form data
        
    Returns:
        list: List of error messages for missing/invalid fields
    """
    errors = []
    
    # Page 1 validations
    if not page1_data.get('title', '').strip():
        errors.append("Project Title")
    if not page1_data.get('department'):
        errors.append("Department/Lab")
    if page1_data.get('openings', 0) < 1:
        errors.append("Number of Openings")
    if not page1_data.get('start_date'):
        errors.append("Start Date")
    if not page1_data.get('duration'):
        errors.append("Duration")
    if page1_data.get('weekly_hours', 0) < 1:
        errors.append("Number of Hours per Week")
    
    # Page 2 validations
    if not page2_data.get('compensation_type'):
        errors.append("Compensation Type")
    if not page2_data.get('skills'):
        errors.append("Skills Required")
    if not page2_data.get('summary', '').strip():
        errors.append("Summary/Description")
    if not page2_data.get('communication'):
        errors.append("Preferred Method of Communication")
    
    return errors


def create_listing_data(page1_data, page2_data, user_info):
    """Create a new listing dictionary from form data.
    
    Args:
        page1_data: Dictionary of page 1 form data
        page2_data: Dictionary of page 2 form data
        user_info: Current user information
        
    Returns:
        dict: Complete listing data ready for Firebase
    """
    date_posted_formatted = datetime.now().strftime("%B %d, %Y")
    profile_data = get_user_profile(user_info['uid'])
    posted_by = profile_data.get('name', 'Unknown') if profile_data else 'Unknown'
    start_date_formatted = page1_data['start_date'].strftime("%B %d, %Y")
    skills_str = ", ".join(page2_data['skills'])
    communication_str = ", ".join(page2_data['communication'])
    
    return {
        "title": page1_data['title'],
        "pi": posted_by,
        "team": page1_data['team'] if page1_data['team'] else "n/a",
        "department": page1_data['department'],
        "skills": skills_str,
        "openings": page1_data['openings'],
        "start_date": start_date_formatted,
        "duration": page1_data['duration'],
        "pay_rate": page2_data['pay_rate'] if page2_data['compensation_type'] == "Paid" else 0,
        "weekly_hours": page1_data['weekly_hours'],
        "summary": page2_data['summary'],
        "date_posted": date_posted_formatted,
        "compensation_type": page2_data['compensation_type'].lower(),
        "website_urls": page2_data['website_urls'] if page2_data['website_urls'] else "n/a",
        "communication": communication_str,
        "posted_by_uid": user_info['uid']
    }


def handle_form_submission(page1_data, page2_data, user_info):
    """Handle form submission, validation, and saving.
    
    Args:
        page1_data: Dictionary of page 1 form data
        page2_data: Dictionary of page 2 form data
        user_info: Current user information
    """
    # Validate all fields
    errors = validate_listing_form(page1_data, page2_data)
    
    if errors:
        error_message = "Please fill out the following required fields:\n" + "\n".join([f"* {error}" for error in errors])
        st.error(error_message)
    else:
        # Create and save listing
        new_listing = create_listing_data(page1_data, page2_data, user_info)
        
        try:
            listing_id = save_listing_to_firebase(new_listing)
            st.session_state.listing_created = True
            st.session_state.listing_title = page1_data['title']
            st.session_state.form_counter += 1
            st.session_state.form_page = 1  # Reset to page 1
            # Clear saved form data
            st.session_state.form_page1_data = {}
            st.session_state.form_page2_data = {}
            st.rerun()
        except Exception as e:
            st.error(f"Failed to create listing: {e}")


def render_form_page1():
    """Render page 1 of the listing creation form."""
    form_key = st.session_state.form_counter
    saved_data = st.session_state.form_page1_data
    
    # Render all fields and get values
    page1_data = render_form_page1_fields(form_key, saved_data)
    
    # Navigation button
    if st.button("Next →", width="stretch"):
        st.session_state.form_page1_data = page1_data
        st.session_state.form_page = 2
        st.rerun()


def render_form_page2(user_info):
    """Render page 2 of the listing creation form.
    
    Args:
        user_info: Current user information
    """
    form_key = st.session_state.form_counter
    saved_data = st.session_state.form_page2_data
    
    # Render all fields and get values
    page2_data = render_form_page2_fields(form_key, saved_data)
    
    # Navigation buttons
    col_back, col_submit = st.columns(2)
    with col_back:
        if st.button("← Back", width="stretch"):
            st.session_state.form_page2_data = page2_data
            st.session_state.form_page = 1
            st.rerun()
    with col_submit:
        submitted = st.button("Post Listing", width="stretch")
    
    # Handle form submission
    if submitted:
        page1_data = st.session_state.form_page1_data
        handle_form_submission(page1_data, page2_data, user_info)


def render_create_listing_form(user_info):
    """Render the complete two-page listing creation form.
    
    Args:
        user_info: Current user information
    """
    st.header("Create a New Research Listing")
    
    # Initialize session state
    initialize_listing_session_state()
    
    # Narrower columns
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        # Progress bar
        render_form_progress_bar()
        
        # Form container
        with st.container(border=True):
            if st.session_state.form_page == 1:
                render_form_page1()
            else:
                render_form_page2(user_info)
        
        # Show success message below the form
        if st.session_state.get("listing_created", False):
            st.success(f"Listing '{st.session_state.listing_title}' successfully created!")
            st.session_state.listing_created = False


def render_browse_listings_tab(user_info):
    """Render the Browse Listings tab.
    
    Args:
        user_info: Current user information
    """
    # Get all listings
    all_listings = get_all_listings_from_firebase()
    
    # Render filters in sidebar
    hours_filter, compensation_filter, faculty_filter = render_sidebar_filters(all_listings)
    
    # Filter and reverse for display
    filtered_listings = filter_listings(all_listings, hours_filter, compensation_filter, faculty_filter)
    filtered_listings = filtered_listings[::-1]  # Reverse to show newest first
    
    # Show admin edit/delete capability notice
    if user_info['role'] == "admin":
        st.info("👑 **Admin View:** You can edit or delete any listing from this tab.")
    
    if filtered_listings:
        render_listings(
            filtered_listings, 
            show_edit=(user_info['role'] == "admin"),
            show_delete=(user_info['role'] == "admin"),
            show_favorite=(user_info['role'] == "student"),
            user_info=user_info,
            tab_prefix="browse"
        )
    else:
        st.info("No listings match your filters.")


def render_create_listing_tab(user_info):
    """Render the Create Listing tab (faculty/admin only).
    
    Args:
        user_info: Current user information
    """
    render_create_listing_form(user_info)


def render_favorite_listings(user_info):
    """Render favorite listings for students.
    
    Args:
        user_info: Current user information
    """
    st.header("My Favorite Listings")
    
    # Get favorited listing IDs
    favorited_ids = get_user_favorite_listings(user_info['uid'])
    
    if favorited_ids:
        # Get all listings and filter to favorites
        all_listings = get_all_listings_from_firebase()
        favorite_listings = [l for l in all_listings if l.get("listing_id") in favorited_ids]
        
        if favorite_listings:
            render_listings(
                favorite_listings[::-1],
                show_edit=False,
                show_delete=False,
                show_favorite=True,
                user_info=user_info,
                tab_prefix="favorites"
            )
        else:
            st.info("You haven't favorited any listings yet. Click the ☆ icon on listings in the Browse tab to save them here!")
    else:
        st.info("You haven't favorited any listings yet. Click the ☆ icon on listings in the Browse tab to save them here!")


def render_my_listings_display(listing, listing_id, idx):
    """Render the display view of a single listing in My Listings tab.
    
    Args:
        listing: Listing data dictionary
        listing_id: Unique listing ID
        idx: Index for unique key generation
    """
    
    st.subheader(listing["title"])
    st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
    st.write(f"**Additional Collaborators:** {listing['team']}")
    st.write(f"**Department/Lab:** {listing['department']}")
    st.write(f"**Number of Openings:** {listing['openings']}")
    st.write(f"**Start Date:** {listing['start_date']}")
    st.write(f"**Duration:** {listing['duration']}")
    st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
    
    # Display pay rate based on compensation type
    if listing['compensation_type'] == 'paid':
        st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']:.2f}")
    else:
        st.write(f"**Hourly Pay Rate:** N/A")
    
    st.write(f"**Skills Required:** {listing['skills']}")
    if "website_urls" in listing and listing["website_urls"] != "n/a":
        st.write(f"**Website URL:** {listing['website_urls']}")
    st.write(f"**Summary/Description:** {listing['summary']}")
    if "communication" in listing and listing["communication"]:
        st.write(f"**Preferred Method of Communication:** {listing['communication']}")
    st.write("")

def render_listing_action_buttons(listing_id):
    """Render edit and delete action buttons for a listing.
    
    Args:
        listing_id: Unique listing ID
    """
    button_cols = st.columns([1, 1, 4])
    
    # Edit button
    with button_cols[0]:
        if st.button("✏️ Edit", key=f"edit_my_{listing_id}", width="stretch"):
            st.session_state.editing_listing = listing_id
            st.session_state.editing_tab = "my"
            st.rerun()

    # Delete button
    with button_cols[1]:
        if st.button("🗑️ Delete", key=f"delete_my_{listing_id}", width="stretch"):
            st.session_state.delete_confirm_my[listing_id] = True
            st.rerun()

def render_my_created_listings(user_info):
    """Render created listings for faculty/admin.
    
    Args:
        user_info: Current user information
    """
    st.header("My Listings")
    
    # Get user's listings
    my_listings = get_user_listings_from_firebase(user_info['uid'])
    
    if my_listings:
        # Use the same render_listings function as Browse tab for consistency
        render_listings(
            my_listings[::-1],  # Reverse to show newest first
            show_edit=True,
            show_delete=True,
            show_favorite=False,
            user_info=user_info,
            tab_prefix="my"
        )
    else:
        st.info("You haven't created any listings yet.")

def render_my_listings_tab(user_info):
    """Render the My Listings tab (favorites for students, created for faculty/admin).
    
    Args:
        user_info: Current user information
    """
    if user_info['role'] == "student":
        render_favorite_listings(user_info)
    else:
        render_my_created_listings(user_info)


def main():
    """Main entry point for the Research Opportunities page."""
    render_page_header()
    
    # Initialize session state
    initialize_listing_session_state()

    # Show tabs based on role
    if user_info['role'] in ("faculty", "admin"):
        tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "My Listings"])
        
        with tab1:
            render_browse_listings_tab(user_info)
        
        with tab2:
            render_create_listing_tab(user_info)
        
        with tab3:
            render_my_listings_tab(user_info)
    else:
        # Students see Browse and My Listings (for favorites)
        tab1, tab3 = st.tabs(["Browse Listings", "My Listings"])
        
        with tab1:
            render_browse_listings_tab(user_info)
        
        with tab3:
            render_my_listings_tab(user_info)


if __name__ == "__main__":
    main()

#-----END OF FILE-----