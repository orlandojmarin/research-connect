# TATIANA
# listings.py
# refactored. render sidebar filters, render edit form, render listings functions moved to listings_utils.py.

import streamlit as st
from datetime import datetime
from utils.listings_utils import (
    filter_listings,
    save_listing_to_firebase,
    get_all_listings_from_firebase,
    get_user_listings_from_firebase,
    delete_listing_from_firebase,
    update_listing_in_firebase,
    toggle_favorite_listing,
    get_user_favorite_listings,
    get_active_faculty_names,
    render_sidebar_filters,
    render_edit_form,
    render_listings,
    SKILLS_OPTIONS
)
from utils.profile_utils import get_user_profile
from utils.general_utils import (
    auth_gate, get_current_user, configure_page,
    render_scsu_logo, render_sidebar_auth
)

FACULTY_NAMES = [
    "Amal Abd El-Raouf",
    "Sahar Al Seesi",
    "Imad Antonios",
    "Ataollah Elahi",
    "Mohammad Islam",
    "Chang Suk Kim",
    "Lisa Lancor",
    "Hrvoje Podnar",
    "Taraneh Seyed",
    "Alaa Sheta",
    "Aashma Uprety",
    "Hao Wu",
    "Winnie Yu",
    "Yulei Pang",
    "Heidi Lockwood",
    "Tatiana Eng",
    "Orlando Marin",
    "Sana Muneer"
]

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

def main():
    """Main entry point for the Research Opportunities page."""
    st.title("Research Opportunities 🔍")

    # Show tabs based on role
    if user_info['role'] in ("faculty", "admin"):
        tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "My Listings"])
    else:
        # Students see Browse and My Listings (for favorites)
        tab1, tab3 = st.tabs(["Browse Listings", "My Listings"])
        tab2 = None  # No create tab for students

    # Browse Listings
    with tab1:
        # Get all listings first
        all_listings = get_all_listings_from_firebase()
        
        # Render filters in sidebar (pass all listings for faculty extraction)
        hours_filter, compensation_filter, faculty_filter = render_sidebar_filters(all_listings)
        
        # Filter and reverse for display
        filtered_listings = filter_listings(all_listings, hours_filter, compensation_filter, faculty_filter)
        filtered_listings = filtered_listings[::-1]  # Reverse to show newest first
        
        # Show admin edit/delete capability notice
        if user_info['role'] == "admin":
            st.info("👑 **Admin View:** You can edit or delete any listing from this tab.")
        
        if filtered_listings:
            # Students see favorite button, admins see edit/delete
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

    # Create Listing (faculty/admin only)
    if user_info['role'] in ("faculty", "admin") and tab2 is not None:
        with tab2:
            st.header("Create a New Research Listing")

            if "form_counter" not in st.session_state:
                st.session_state.form_counter = 0

            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                if st.session_state.get("listing_created", False):
                    st.success(f"Listing '{st.session_state.listing_title}' successfully created!")
                    st.session_state.listing_created = False

                with st.container(border=True):
                    form_key = st.session_state.form_counter
                    title = st.text_input("Project Title *", value="", placeholder="ex. Biometric Authentication in Smartphones", key=f"title_input_{form_key}")
                    team = st.text_input("Additional Collaborators", value="", placeholder="ex. Grace Hopper, John von Neumann", key=f"team_input_{form_key}")
                    department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=0, key=f"dept_input_{form_key}")
                    openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=1, step=1, key=f"openings_input_{form_key}")
                    start_date = st.date_input("Start Date *", value=datetime.now().date(), key=f"start_date_input_{form_key}")
                    if start_date:
                        st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
                    else:
                        st.caption("Please select a start date")
                    duration = st.selectbox("Duration *", options=["1 semester", "2 semesters", "More than 2 semesters"], index=0, key=f"duration_input_{form_key}")
                    weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=1, step=1, key=f"hours_input_{form_key}")

                    compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=None, key=f"comp_type_{form_key}")
                    
                    # Always show pay rate field, but disable when Unpaid is selected or nothing is selected
                    pay_rate = st.number_input(
                        "Hourly Pay Rate ($) *",
                        min_value=16.35,
                        value=16.35,
                        step=0.01,
                        format="%.2f",
                        disabled=(compensation_type != "Paid"),
                        key=f"pay_rate_input_{form_key}"
                    )

                    st.write("Skills Required *")
                    skills = st.multiselect(
                        "Select skills",
                        options=SKILLS_OPTIONS,
                        default=None,
                        placeholder="Select all that apply",
                        label_visibility="collapsed",
                        key=f"skills_input_{form_key}"
                    )

                    website_urls = st.text_input("Website URL(s)", value="", placeholder="ex. https://example.com", key=f"website_input_{form_key}")
                    summary = st.text_area("Summary/Description *", value="", key=f"summary_input_{form_key}")
                    
                    st.write("Preferred Method of Communication *")
                    communication = st.multiselect(
                        "Select communication methods",
                        options=["Email", "Teams"],
                        default=None,
                        placeholder="Select all that apply",
                        label_visibility="collapsed",
                        key=f"comm_input_{form_key}"
                    )

                    submitted = st.button("Post Listing")
                    if submitted:
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
                        if compensation_type == "Paid" and (pay_rate is None or pay_rate < 16.35):
                            errors.append("Hourly Pay Rate (must be at least $16.35)")
                        if not skills:
                            errors.append("Skills Required")
                        if not summary.strip():
                            errors.append("Summary/Description")
                        if not communication:
                            errors.append("Preferred Method of Communication")

                        if errors:
                            st.error(f"Please fill out the following required fields: {', '.join(errors)}")
                        else:
                            date_posted_formatted = datetime.now().strftime("%B %d, %Y")
                            profile_data = get_user_profile(user_info['uid'])
                            posted_by = profile_data.get('name', 'Unknown') if profile_data else 'Unknown'
                            start_date_formatted = start_date.strftime("%B %d, %Y")
                            skills_str = ", ".join(skills)
                            communication_str = ", ".join(communication)

                            new_listing = {
                                "title": title,
                                "pi": posted_by,
                                "team": team if team else "n/a",
                                "department": department,
                                "skills": skills_str,
                                "openings": openings,
                                "start_date": start_date_formatted,
                                "duration": duration,
                                "pay_rate": pay_rate if compensation_type == "Paid" else 0,
                                "weekly_hours": weekly_hours,
                                "summary": summary,
                                "date_posted": date_posted_formatted,
                                "compensation_type": compensation_type.lower(),
                                "website_urls": website_urls if website_urls else "n/a",
                                "communication": communication_str,
                                "posted_by_uid": user_info['uid']
                            }

                            try:
                                listing_id = save_listing_to_firebase(new_listing)
                                st.session_state.listing_created = True
                                st.session_state.listing_title = title
                                st.session_state.listing_posted_by = posted_by
                                st.session_state.listing_date = date_posted_formatted
                                st.session_state.form_counter += 1
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to create listing: {e}")

    # My Listings (all users)
    with tab3:
        if user_info['role'] == "student":
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
        
        else:  # Faculty and admin see their created listings
            st.header("My Listings")
            
            # Both admins and faculty see only their own listings here
            my_listings = get_user_listings_from_firebase(user_info['uid'])
            
            if my_listings:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    for idx, listing in enumerate(my_listings[::-1]):
                        listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
                        container_key = f"my_listing_container_{listing_id}"
                        
                        # Check if this listing is being edited
                        is_editing = (st.session_state.get("editing_listing") == listing_id and 
                                     st.session_state.get("editing_tab") == "my")

                        with st.container(key=container_key, border=True):
                            if is_editing:
                                render_edit_form(listing, listing_id, "my")
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
                                if "delete_confirm_my" not in st.session_state:
                                    st.session_state.delete_confirm_my = {}

                                # Check if delete confirmation is active for this listing
                                if st.session_state.delete_confirm_my.get(listing_id):
                                    # Show full-width delete confirmation
                                    st.warning(f"Are you sure you want to delete **{listing['title']}**?")
                                    col_yes, col_no = st.columns([1, 1])
                                    with col_yes:
                                        if st.button("🗑️ Confirm Delete", key=f"confirm_my_{listing_id}", use_container_width=True):
                                            try:
                                                delete_listing_from_firebase(listing.get("listing_id"))
                                                st.success(f"'{listing['title']}' has been deleted.")
                                                st.session_state.delete_confirm_my[listing_id] = False
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Failed to delete listing: {e}")
                                    with col_no:
                                        if st.button("❌ Cancel", key=f"cancel_my_{listing_id}", use_container_width=True):
                                            st.session_state.delete_confirm_my[listing_id] = False
                                            st.rerun()
                                else:
                                    # Action buttons row - keeping original narrow width
                                    button_cols = st.columns([1, 1, 4])
                                    
                                    # Edit button
                                    with button_cols[0]:
                                        if st.button("✏️ Edit", key=f"edit_my_{listing_id}", use_container_width=True):
                                            st.session_state.editing_listing = listing_id
                                            st.session_state.editing_tab = "my"
                                            st.rerun()

                                    # Delete button
                                    with button_cols[1]:
                                        if st.button("🗑️ Delete", key=f"delete_my_{listing_id}", use_container_width=True):
                                            st.session_state.delete_confirm_my[listing_id] = True
                                            st.rerun()
            else:
                st.info("You haven't created any listings yet.")

if __name__ == "__main__":
    main()