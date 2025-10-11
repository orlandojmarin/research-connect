# TATIANA

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

if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("home.py")
    st.stop()

# NEW — grab user info for this page
user = st.session_state.user              # 
email = user["email"]                     # 
uid   = user["uid"]                       # 
role  = user.get("role", "student")       # 


def configure_page():
    st.set_page_config(
        page_title="Research Opportunities 🔍",
        page_icon="🔍",
        layout="wide"
    )
with st.sidebar:
    st.success(f"Logged in as {email}")               # changed to use email var
    st.caption(f"Role: {role}")
    if st.button("Log Out"):
        st.session_state.user = None
        st.session_state.page = "landing"
        st.rerun()

def render_sidebar_filters():
    st.sidebar.title("Filters")
    with st.sidebar.expander("Hours per Week", expanded=False):
        hours_filter = st.radio("", ["All", "0 to 5", "6 to 10", "10+"], index=0)
    with st.sidebar.expander("Compensation Type", expanded=False):
        compensation_filter = st.radio("", ["All", "Paid", "Unpaid"], index=0)
    with st.sidebar.expander("Faculty", expanded=False):
        faculty_filter = st.radio("", options=["All"] + FACULTY_NAMES, index=0)
    return hours_filter, compensation_filter, faculty_filter

def render_listings(listings):
    for listing in listings:
        with st.container():
            st.subheader(listing["title"])
            st.write(f"**Principal Investigator:** {listing['pi']}")
            st.write(f"**Additional Investigators/Team Members:** {listing['team']}")
            st.write(f"**Department/Lab:** {listing['department']}")
            st.write(f"**Skills Required:** {listing['skills']}")
            st.write(f"**Number of Openings:** {listing['openings']}")
            st.write(f"**Start Date:** {listing['start_date']}")
            st.write(f"**Duration:** {listing['duration']}")
            st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
            st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
            st.write(f"**Summary/Description:** {listing['summary']}")
            st.write(f"**Date Posted:** {listing['date_posted']}")

def main():
    configure_page()
    if "role" not in st.session_state:
        st.session_state["role"] = "FACULTY"

    st.title("Research Opportunities 🔍")
    st.logo("images/scsu_logo.jpg", size="large")
    user_role = st.session_state.get("role", "STUDENT")

    if user_role == "FACULTY":
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
    if user_role == "FACULTY":
        with tab2:
            st.header("Create a New Research Listing")
            st.info("Fill out the form below and submit.")

            # Use a container for a form-like layout
            with st.container():
                title = st.text_input("Project Title", value="")
                # pi = st.text_input("Principal Investigator", value="")
                pi = st.selectbox("Principal Investigator", options=[""] + FACULTY_NAMES)  # "" allows no default selection

                team = st.text_input("Additional Investigators/Team Members", value="")
                department = st.text_input("Department/Lab", value="")
                skills = st.text_area("Skills Required", value="")
                openings = st.number_input("Number of Openings", min_value=1, max_value=10, value=1, step=1)
                start_date = st.text_input("Start Date", value="")
                duration = st.text_input("Duration", value="")

                # Compensation type and dynamic Hourly Pay Rate
                compensation_type = st.radio("Compensation Type", ["Paid", "Unpaid"], index=None, key="comp_type")
                if compensation_type == "Paid":
                    pay_rate = st.number_input(
                        "Hourly Pay Rate ($)",
                        min_value=0.0,
                        step=0.01,
                        format="%.2f"
                    )

                weekly_hours = st.number_input("Number of Hours per Week", min_value=1, value=1, step=1)
                summary = st.text_area("Summary/Description", value="")
                date_posted = st.date_input("Date Posted")

                submitted = st.button("Submit Listing")
                if submitted:
                    st.success(f"Listing '{title}' successfully created!")

    # My Listings
        with tab3:
            st.header("My Listings")
            st.info("Faculty’s personal listings will appear here.")

if __name__ == "__main__":
    main()