# TATIANA
# listings_utils.py

import streamlit as st
from datetime import datetime
from utils.auth_utils import db
from utils.profile_utils import get_user_profile

SKILLS_OPTIONS = [
    "Python",
    "Java",
    "C++",
    "SQL",
    "Web Development (HTML, CSS, JavaScript)",
    "Data Science",
    "Artificial Intelligence/Machine Learning",
    "Data Visualization",
    "Software Development",
    "Cloud Computing (AWS, Azure, GCP)",
    "Database Design and Management",
    "Research Methods / Experimental Design"
]

def save_listing_to_firebase(listing_data):
    """
    Save a new listing to Firebase Realtime Database using Firebase Admin SDK.
    Returns the unique listing ID.
    """
    try:
        # Firebase Admin SDK uses push() differently
        listings_ref = db.child("listings")
        new_listing_ref = listings_ref.push()
        new_listing_ref.set(listing_data)
        
        # Get the key/ID of the newly created listing
        listing_id = new_listing_ref.key
        return listing_id
    except Exception as e:
        raise RuntimeError(f"Failed to save listing: {e}")

def update_listing_in_firebase(listing_id, updated_data):
    """
    Update an existing listing in Firebase Realtime Database.
    
    Args:
        listing_id: The unique listing ID
        updated_data: Dictionary of fields to update
    """
    try:
        listing_ref = db.child("listings").child(listing_id)
        listing_ref.update(updated_data)
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to update listing {listing_id}: {e}")
    
def get_all_listings_from_firebase():
    """
    Retrieve all listings from Firebase Realtime Database using Firebase Admin SDK.
    Returns a list of listing dictionaries.
    """
    try:
        listings_ref = db.child("listings")
        data = listings_ref.get()  # Firebase Admin SDK returns dict directly, no .val() needed
        
        if not data:
            return []

        listings = []
        for listing_id, listing_data in data.items():
            listing_data["listing_id"] = listing_id
            listings.append(listing_data)

        return listings
    except Exception as e:
        print(f"Error fetching listings: {e}")
        return []


def get_user_listings_from_firebase(uid):
    """
    Retrieve all listings created by a specific user.
    Returns a list of listing dictionaries.
    """
    try:
        all_listings = get_all_listings_from_firebase()
        return [listing for listing in all_listings if listing.get("posted_by_uid") == uid]
    except Exception as e:
        print(f"Error fetching user listings: {e}")
        return []


def delete_listing_from_firebase(listing_id):
    """
    Delete a listing from Firebase Realtime Database by its unique listing ID.
    """
    try:
        listing_ref = db.child("listings").child(listing_id)
        listing_ref.delete()  # Firebase Admin SDK uses .delete() not .remove()
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to delete listing {listing_id}: {e}")


def get_active_faculty_names(listings):
    """
    Extract unique faculty names (pi field) from a list of listings.
    Returns a sorted list of faculty names who have active listings.
    
    Args:
        listings: List of listing dictionaries
    
    Returns:
        list: Sorted list of unique faculty names
    """
    faculty_names = set()
    for listing in listings:
        pi = listing.get("pi")
        if pi and pi != "Unknown":
            faculty_names.add(pi)
    
    return sorted(list(faculty_names))


def filter_listings(listings, hours_filter, compensation_filter, faculty_filter):
    """
    Filters listings based on sidebar selections.
    """
    filtered = []

    for listing in listings:
        # Hours per Week filter
        hours_ok = False
        if hours_filter == "All":
            hours_ok = True
        elif hours_filter == "0 to 5" and listing["weekly_hours"] <= 5:
            hours_ok = True
        elif hours_filter == "6 to 10" and 6 <= listing["weekly_hours"] <= 10:
            hours_ok = True
        elif hours_filter == "10+" and listing["weekly_hours"] > 10:
            hours_ok = True

        # Compensation filter
        compensation_ok = (compensation_filter == "All" or listing["compensation_type"] == compensation_filter.lower())

        # Faculty filter
        faculty_ok = (faculty_filter == "All" or listing["pi"] == faculty_filter)

        if hours_ok and compensation_ok and faculty_ok:
            filtered.append(listing)

    return filtered


def toggle_favorite_listing(uid, listing_id):
    """
    Toggle a listing as favorite/unfavorite for a user using Firebase Admin SDK.
    Stores favorites under users/{uid}/favorite_listings/{listing_id}
    
    Args:
        uid: User's unique ID
        listing_id: Listing's unique ID
    
    Returns:
        bool: True if favorited, False if unfavorited
    """
    try:
        # Check if already favorited
        favorite_ref = db.child("users").child(uid).child("favorite_listings").child(listing_id)
        current_value = favorite_ref.get()
        
        if current_value:
            # Already favorited, so remove it
            favorite_ref.delete()
            return False
        else:
            # Not favorited, so add it
            favorite_ref.set(True)
            return True
    except Exception as e:
        raise RuntimeError(f"Failed to toggle favorite for listing {listing_id}: {e}")


def get_user_favorite_listings(uid):
    """
    Get all listing IDs that a user has favorited using Firebase Admin SDK.
    
    Args:
        uid: User's unique ID
    
    Returns:
        list: List of listing IDs that are favorited
    """
    try:
        favorites_ref = db.child("users").child(uid).child("favorite_listings")
        data = favorites_ref.get()
        
        if not data:
            return []
        
        # Return list of listing IDs
        return list(data.keys())
    except Exception as e:
        print(f"Error fetching favorite listings: {e}")
        return []


def render_sidebar_filters(all_listings):
    """Render sidebar filters for refining research opportunity listings.
    
    Args:
        all_listings: List of all listings to extract active faculty from
    """
    st.sidebar.title("Filters")
    with st.sidebar.expander("Hours per Week", expanded=True):
        hours_filter = st.radio("", ["All", "0 to 5", "6 to 10", "10+"], index=0, key="hours_filter")
    with st.sidebar.expander("Compensation Type", expanded=True):
        compensation_filter = st.radio("", ["All", "Paid", "Unpaid"], index=0, key="comp_filter")
    with st.sidebar.expander("Faculty", expanded=True):
        # Get only faculty who have active listings
        active_faculty = get_active_faculty_names(all_listings)
        faculty_filter = st.radio("", options=["All"] + active_faculty, index=0, key="faculty_filter")
    return hours_filter, compensation_filter, faculty_filter

def render_edit_form(listing, listing_id, form_key_prefix):
    """Render the edit form for a listing.
    
    Args:
        listing: The listing data dictionary
        listing_id: The unique listing ID
        form_key_prefix: Prefix for form keys to ensure uniqueness
    """
    st.subheader(f"Editing: {listing['title']}")
    
    with st.form(key=f"edit_form_{form_key_prefix}_{listing_id}"):
        title = st.text_input("Project Title *", value=listing['title'], key=f"edit_title_{form_key_prefix}_{listing_id}")
        team = st.text_input("Additional Collaborators", value=listing.get('team', 'n/a') if listing.get('team') != 'n/a' else "", key=f"edit_team_{form_key_prefix}_{listing_id}")
        
        dept_index = 0 if listing['department'] == "Computer Science" else 1
        department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=dept_index, key=f"edit_dept_{form_key_prefix}_{listing_id}")
        
        openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=listing['openings'], step=1, key=f"edit_openings_{form_key_prefix}_{listing_id}")
        
        # Parse start date - if empty or invalid, default to today
        try:
            start_date_obj = datetime.strptime(listing['start_date'], "%B %d, %Y")
        except:
            start_date_obj = datetime.now()
        
        start_date = st.date_input("Start Date *", value=start_date_obj, key=f"edit_start_date_{form_key_prefix}_{listing_id}")
        
        # If start_date is None (user cleared it), use today's date
        if start_date is None:
            start_date = datetime.now().date()
        
        st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
        
        duration_options = ["1 semester", "2 semesters", "More than 2 semesters"]
        duration_index = duration_options.index(listing['duration']) if listing['duration'] in duration_options else 0
        duration = st.selectbox("Duration *", options=duration_options, index=duration_index, key=f"edit_duration_{form_key_prefix}_{listing_id}")
        
        weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=listing['weekly_hours'], step=1, key=f"edit_hours_{form_key_prefix}_{listing_id}")
        
        comp_index = 0 if listing['compensation_type'] == "paid" else 1
        compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=comp_index, key=f"edit_comp_type_{form_key_prefix}_{listing_id}")
        
        # Pay rate field is always optional (no asterisk)
        pay_rate = st.number_input(
            "Hourly Pay Rate ($)",
            min_value=16.35,
            value=max(16.35, float(listing.get('pay_rate', 16.35))),
            step=0.01,
            format="%.2f",
            key=f"edit_pay_rate_{form_key_prefix}_{listing_id}"
        )
        st.caption("Note: Pay rate will be displayed as N/A when compensation type is unpaid.")
        
        st.write("Skills Required *")
        current_skills = [s.strip() for s in listing['skills'].split(',')] if listing['skills'] else []
        skills = st.multiselect(
            "Select skills",
            options=SKILLS_OPTIONS,
            default=[s for s in current_skills if s in SKILLS_OPTIONS],
            placeholder="Select all that apply",
            label_visibility="collapsed",
            key=f"edit_skills_{form_key_prefix}_{listing_id}"
        )
        
        website_urls = st.text_input("Website URL(s)", value=listing.get('website_urls', '') if listing.get('website_urls') != 'n/a' else "", key=f"edit_website_{form_key_prefix}_{listing_id}")
        summary = st.text_area("Summary/Description *", value=listing['summary'], key=f"edit_summary_{form_key_prefix}_{listing_id}")
        
        st.write("Preferred Method of Communication *")
        current_comm = [c.strip() for c in listing.get('communication', '').split(',')] if listing.get('communication') else []
        communication = st.multiselect(
            "Select communication methods",
            options=["Email", "Teams"],
            default=[c for c in current_comm if c in ["Email", "Teams"]],
            placeholder="Select all that apply",
            label_visibility="collapsed",
            key=f"edit_comm_{form_key_prefix}_{listing_id}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel_button:
            st.session_state.editing_listing = None
            st.rerun()
        
        if save_button:
            errors = []
            if not title.strip():
                errors.append("Project Title")
            if not department:
                errors.append("Department/Lab")
            if openings < 1:
                errors.append("Number of Openings")
            if not start_date:
                errors.append("Start Date")
            if not duration:
                errors.append("Duration")
            if weekly_hours < 1:
                errors.append("Number of Hours per Week")
            if not compensation_type:
                errors.append("Compensation Type")
            # Pay rate is now always optional - no validation needed
            if not skills:
                errors.append("Skills Required")
            if not summary.strip():
                errors.append("Summary/Description")
            if not communication:
                errors.append("Preferred Method of Communication")
            
            if errors:
                st.error(f"Please fill out the following required fields: {', '.join(errors)}")
            else:
                start_date_formatted = start_date.strftime("%B %d, %Y")
                skills_str = ", ".join(skills)
                communication_str = ", ".join(communication)
                
                updated_listing = {
                    "title": title,
                    "team": team if team else "n/a",
                    "department": department,
                    "skills": skills_str,
                    "openings": openings,
                    "start_date": start_date_formatted,
                    "duration": duration,
                    "pay_rate": pay_rate if compensation_type == "Paid" else 0,
                    "weekly_hours": weekly_hours,
                    "summary": summary,
                    "compensation_type": compensation_type.lower(),
                    "website_urls": website_urls if website_urls else "n/a",
                    "communication": communication_str,
                }
                
                try:
                    update_listing_in_firebase(listing_id, updated_listing)
                    st.success(f"✅ Listing '{title}' has been updated successfully!")
                    st.session_state.editing_listing = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update listing: {e}")

def render_listings(listings, show_edit=False, show_delete=False, show_favorite=False, user_info=None, tab_prefix="browse"):
    """Display a list of research opportunity listings in a structured and readable format.
    
    Args:
        listings: List of listing dictionaries to display
        show_edit: Whether to show edit buttons
        show_delete: Whether to show delete buttons (admin only in Browse tab)
        show_favorite: Whether to show favorite/star button
        user_info: Current user information for permission checks
        tab_prefix: Prefix for session state keys to avoid conflicts between tabs
    """
    # Get user's favorited listings if showing favorites
    favorited_listing_ids = set()
    if show_favorite and user_info:
        favorited_listing_ids = set(get_user_favorite_listings(user_info['uid']))
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        for idx, listing in enumerate(listings):
            listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
            container_key = f"{tab_prefix}_listing_container_{listing_id}_{idx}"
            
            # Check if this listing is being edited
            is_editing = (st.session_state.get("editing_listing") == listing_id and 
                         st.session_state.get("editing_tab") == tab_prefix)
            
            with st.container(key=container_key, border=True):
                if is_editing:
                    render_edit_form(listing, listing_id, tab_prefix)
                else:
                    # Header row with title and favorite button
                    if show_favorite:
                        header_cols = st.columns([5, 1])
                        with header_cols[0]:
                            st.subheader(listing["title"])
                        with header_cols[1]:
                            is_favorited = listing_id in favorited_listing_ids
                            star_icon = "⭐" if is_favorited else "☆"
                            star_label = "Unfavorite" if is_favorited else "Favorite"
                            if st.button(star_icon, key=f"fav_{tab_prefix}_{listing_id}_{idx}", help=star_label, use_container_width=True):
                                try:
                                    toggle_favorite_listing(user_info['uid'], listing_id)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to update favorite: {e}")
                    else:
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
                        st.write(f"**Website URL(s):** {listing['website_urls']}")
                    st.write(f"**Summary/Description:** {listing['summary']}")
                    if "communication" in listing and listing["communication"]:
                        st.write(f"**Preferred Method of Communication:** {listing['communication']}")
                    st.write("")
                    
                    # Initialize session state for confirmation if not present
                    delete_confirm_key = f"delete_confirm_{tab_prefix}"
                    if delete_confirm_key not in st.session_state:
                        st.session_state[delete_confirm_key] = {}
                    
                    # Check if delete confirmation is active for this listing
                    if st.session_state[delete_confirm_key].get(listing_id):
                        # Show full-width delete confirmation
                        st.warning(f"Are you sure you want to delete **{listing['title']}**?")
                        col_yes, col_no = st.columns([1, 1])
                        with col_yes:
                            if st.button("🗑️ Confirm Delete", key=f"confirm_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
                                try:
                                    delete_listing_from_firebase(listing.get("listing_id"))
                                    st.success(f"'{listing['title']}' has been deleted.")
                                    st.session_state[delete_confirm_key][listing_id] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete listing: {e}")
                        with col_no:
                            if st.button("❌ Cancel", key=f"cancel_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
                                st.session_state[delete_confirm_key][listing_id] = False
                                st.rerun()
                    else:
                        # Action buttons row - keeping original narrow width
                        button_cols = st.columns([1, 1, 4])
                        
                        # Edit button
                        if show_edit:
                            with button_cols[0]:
                                if st.button("✏️ Edit", key=f"edit_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
                                    st.session_state.editing_listing = listing_id
                                    st.session_state.editing_tab = tab_prefix
                                    st.rerun()
                        
                        # Delete button
                        if show_delete:
                            with button_cols[1]:
                                if st.button("🗑️ Delete", key=f"delete_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
                                    st.session_state[delete_confirm_key][listing_id] = True
                                    st.rerun()

#-----END OF FILE-----