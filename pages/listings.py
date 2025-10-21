# TATIANA
# listings.py

import streamlit as st
from utils.listings_utils import get_listings_data, filter_listings

FACULTY_NAMES = [
    "Amal Abd El-Raouf",
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

# Check if user is logged in
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("home.py")
    st.stop()

# Grab user info for this page
user = st.session_state.user
email = user.get("email", "")
uid = user.get("uid", "")
role = user.get("role", "student")

### TEMPORARY: Hard-code role for development ###
if email in ("engt1@southernct.edu", "marino1@southernct.edu", "muneerb1@southernct.edu"):
    role = "ADMIN"

def configure_page():
    st.set_page_config(
        page_title="Research Opportunities 🔍",
        page_icon="🔍",
        layout="wide"
    )


configure_page()

with st.sidebar:
    st.success(f"Logged in as {email}")
    st.caption(f"Role: {role}")
    if st.button("Log Out"):
        st.session_state.user = None
        st.session_state.page = "landing"
        st.rerun()


def render_sidebar_filters():
    st.sidebar.title("Filters")
    with st.sidebar.expander("Hours per Week", expanded=False):
        hours_filter = st.radio("", ["All", "0 to 5", "6 to 10", "10+"], index=0, key="hours_filter")
    with st.sidebar.expander("Compensation Type", expanded=False):
        compensation_filter = st.radio("", ["All", "Paid", "Unpaid"], index=0, key="comp_filter")
    with st.sidebar.expander("Faculty", expanded=False):
        faculty_filter = st.radio("", options=["All"] + FACULTY_NAMES, index=0, key="faculty_filter")
    return hours_filter, compensation_filter, faculty_filter


def render_listings(listings):
    # Create centered column layout
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        for listing in listings:
            with st.container(border=True):
                st.subheader(listing["title"])
                st.write(f"**Principal Investigator:** {listing['pi']}")
                st.write(f"**Additional Collaborators:** {listing['team']}")
                st.write(f"**Department/Lab:** {listing['department']}")
                st.write(f"**Number of Openings:** {listing['openings']}")
                st.write(f"**Start Date:** {listing['start_date']}")
                st.write(f"**Duration:** {listing['duration']}")
                st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
                st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
                st.write(f"**Skills Required:** {listing['skills']}")
                st.write(f"**Summary/Description:** {listing['summary']}")
                st.write(f"**Date Posted:** {listing['date_posted']}")
                st.write("")  # Add spacing between listings


def main():
    st.title("Research Opportunities 🔍")
    st.logo("images/scsu_logo.jpg", size="large")

    if role in ("FACULTY", "ADMIN"):
        tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "My Listings"])
    else:
        tab1, = st.tabs(["Browse Listings"])

    # Browse Listings
    with tab1:
        hours_filter, compensation_filter, faculty_filter = render_sidebar_filters()
        listings = get_listings_data()
        filtered_listings = filter_listings(listings, hours_filter, compensation_filter, faculty_filter)
        if filtered_listings:
            render_listings(filtered_listings)
        else:
            st.info("No listings match your filters.")

    # Create Listing
    if role in ("FACULTY", "ADMIN"):
        with tab2:
            st.header("Create a New Research Listing")
            st.info("Fill out the form below and submit.")

            # Create centered column layout
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col2:
                # Use a container for a form-like layout
                with st.container(border=True):
                    title = st.text_input("Project Title", value="")
                    pi = st.selectbox("Principal Investigator", options=[""] + FACULTY_NAMES)
                    team = st.text_input("Additional Investigators/Team Members", value="")
                    department = st.text_input("Department/Lab", value="")
                    openings = st.number_input("Number of Openings", min_value=1, max_value=10, value=1, step=1)
                    start_date = st.date_input("Start Date")
                    st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
                    duration = st.text_input("Duration", value="")
                    weekly_hours = st.number_input("Number of Hours per Week", min_value=1, value=1, step=1)

                    # Compensation type and dynamic Hourly Pay Rate
                    compensation_type = st.radio("Compensation Type", ["Paid", "Unpaid"], index=None, key="comp_type")
                    if compensation_type == "Paid":
                        pay_rate = st.number_input(
                            "Hourly Pay Rate ($)",
                            min_value=0.0,
                            step=0.01,
                            format="%.2f"
                        )

                    st.write("Skills Required (Select all that apply.)")
                    skills = st.multiselect(
                        "Select skills",
                        options=SKILLS_OPTIONS,
                        default=None,
                        label_visibility="collapsed"
                    )

                    summary = st.text_area("Summary/Description", value="")
                    date_posted = st.date_input("Date Posted")
                    st.caption(f"Will display as: {date_posted.strftime('%B %d, %Y')}")

                    submitted = st.button("Submit Listing")
                    if submitted:
                        # Format dates as "Month Day, Year"
                        start_date_formatted = start_date.strftime("%B %d, %Y")
                        date_posted_formatted = date_posted.strftime("%B %d, %Y")
                        
                        if skills:
                            skills_str = ", ".join(skills)
                            st.success(f"Listing '{title}' successfully created!")
                            st.info(f"Start Date: {start_date_formatted} | Date Posted: {date_posted_formatted}")
                        else:
                            st.success(f"Listing '{title}' successfully created!")
                            st.info(f"Start Date: {start_date_formatted} | Date Posted: {date_posted_formatted}")

        # My Listings
        with tab3:
            st.header("My Listings")
            st.info("Faculty's personal listings will appear here.")


if __name__ == "__main__":
    main()