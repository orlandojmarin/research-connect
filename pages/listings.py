# TATIANA
# listings.py

import streamlit as st
from datetime import datetime
from utils.listings_utils import (
    filter_listings,
    save_listing_to_firebase,
    get_all_listings_from_firebase,
    get_user_listings_from_firebase,
    delete_listing_from_firebase
)
from utils.profile_utils import get_user_profile
from utils.general_utils import (
    auth_gate, get_current_user, configure_page,
    render_scsu_logo, render_sidebar_auth
)

FACULTY_NAMES = [
    "Amal Abed El-Raouf",
    "Hao Wu",
    "Imad Antonios",
    "Lisa Lancor",
    "Md Shafaeat Hossain",
    "Mohammad Islam",
    "Sahar Al Seesi",
    "Winnie Yu"
]

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

def render_sidebar_filters():
    """Render sidebar filters for refining research opportunity listings."""
    st.sidebar.title("Filters")
    with st.sidebar.expander("Hours per Week", expanded=False):
        hours_filter = st.radio("", ["All", "0 to 5", "6 to 10", "10+"], index=0, key="hours_filter")
    with st.sidebar.expander("Compensation Type", expanded=False):
        compensation_filter = st.radio("", ["All", "Paid", "Unpaid"], index=0, key="comp_filter")
    with st.sidebar.expander("Faculty", expanded=False):
        faculty_filter = st.radio("", options=["All"] + FACULTY_NAMES, index=0, key="faculty_filter")
    return hours_filter, compensation_filter, faculty_filter

def render_listings(listings):
    """Display a list of research opportunity listings in a structured and readable format."""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        for listing in listings:
            with st.container(border=True):
                st.subheader(listing["title"])
                st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
                st.write(f"**Additional Collaborators:** {listing['team']}")
                st.write(f"**Department/Lab:** {listing['department']}")
                st.write(f"**Number of Openings:** {listing['openings']}")
                st.write(f"**Start Date:** {listing['start_date']}")
                st.write(f"**Duration:** {listing['duration']}")
                st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
                st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
                st.write(f"**Skills Required:** {listing['skills']}")
                if "website_urls" in listing and listing["website_urls"] != "n/a":
                    st.write(f"**Website URL(s):** {listing['website_urls']}")
                st.write(f"**Summary/Description:** {listing['summary']}")
                if "communication" in listing and listing["communication"]:
                    st.write(f"**Preferred Method of Communication:** {listing['communication']}")
                st.write("")

def main():
    """Main entry point for the Research Opportunities page."""
    st.title("Research Opportunities 🔍")

    if user_info['role'] in ("faculty", "admin"):
        tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "My Listings"])
    else:
        tab1, = st.tabs(["Browse Listings"])

    # Browse Listings
    with tab1:
        hours_filter, compensation_filter, faculty_filter = render_sidebar_filters()
        listings = get_all_listings_from_firebase()[::-1]  # Firebase only
        filtered_listings = filter_listings(listings, hours_filter, compensation_filter, faculty_filter)
        if filtered_listings:
            render_listings(filtered_listings)
        else:
            st.info("No listings match your filters.")

    # Create Listing
    if user_info['role'] in ("faculty", "admin"):
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
                    title = st.text_input("Project Title *", value="", placeholder="ex. My Research Project", key=f"title_input_{form_key}")
                    team = st.text_input("Additional Collaborators", value="", placeholder="ex. Orlando Marin, Sana Muneer", key=f"team_input_{form_key}")
                    department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=0, key=f"dept_input_{form_key}")
                    openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=1, step=1, key=f"openings_input_{form_key}")
                    start_date = st.date_input("Start Date *", key=f"start_date_input_{form_key}")
                    st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
                    duration = st.selectbox("Duration *", options=["1 semester", "2 semesters", "More than 2 semesters"], index=0, key=f"duration_input_{form_key}")
                    weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=1, step=1, key=f"hours_input_{form_key}")

                    compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=None, key=f"comp_type_{form_key}")
                    if compensation_type == "Paid":
                        pay_rate = st.number_input(
                            "Hourly Pay Rate ($) *",
                            min_value=0.0,
                            step=0.01,
                            format="%.2f",
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
                        if compensation_type == "Paid" and (not 'pay_rate' in locals() or pay_rate <= 0):
                            errors.append("Hourly Pay Rate")
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

        # My Listings
        with tab3:
            st.header("My Listings")
            my_listings = get_user_listings_from_firebase(user_info['uid'])
            
            if my_listings:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    for idx, listing in enumerate(my_listings[::-1]):
                        listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
                        container_key = f"listing_container_{listing_id}"

                        with st.container(key=container_key, border=True):
                            st.subheader(listing["title"])
                            st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
                            st.write(f"**Additional Collaborators:** {listing['team']}")
                            st.write(f"**Department/Lab:** {listing['department']}")
                            st.write(f"**Number of Openings:** {listing['openings']}")
                            st.write(f"**Start Date:** {listing['start_date']}")
                            st.write(f"**Duration:** {listing['duration']}")
                            st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
                            st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
                            st.write(f"**Skills Required:** {listing['skills']}")
                            if "website_urls" in listing and listing["website_urls"] != "n/a":
                                st.write(f"**Website URL(s):** {listing['website_urls']}")
                            st.write(f"**Summary/Description:** {listing['summary']}")
                            if "communication" in listing and listing["communication"]:
                                st.write(f"**Preferred Method of Communication:** {listing['communication']}")
                            st.write("")

                            # Initialize session state for confirmation if not present
                            if "delete_confirm" not in st.session_state:
                                st.session_state.delete_confirm = {}

                            # If this listing is being confirmed
                            if st.session_state.delete_confirm.get(listing_id):
                                st.warning(f"Are you sure you want to delete **{listing['title']}**?")
                                col_yes, col_no = st.columns([1,1])
                                with col_yes:
                                    if st.button("Confirm Delete", key=f"confirm_{listing_id}"):
                                        try:
                                            delete_listing_from_firebase(listing.get("listing_id"))
                                            st.success(f"'{listing['title']}' has been deleted.")
                                            st.session_state.delete_confirm[listing_id] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Failed to delete listing: {e}")
                                with col_no:
                                    if st.button("Cancel", key=f"cancel_{listing_id}"):
                                        st.session_state.delete_confirm[listing_id] = False
                                        st.rerun()
                            else:
                                if st.button("🗑️ Delete", key=f"delete_{listing_id}"):
                                    st.session_state.delete_confirm[listing_id] = True
                                    st.rerun()
            else:
                st.info("You haven't created any listings yet.")

if __name__ == "__main__":
    main()
