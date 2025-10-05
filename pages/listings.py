# TATIANA
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py

import streamlit as st
from utils.listings_utils import get_listings_data, filter_listings

def configure_page():
    st.set_page_config(
        page_title="Research Opportunities 🔍",
        page_icon="🔍",
        layout="wide"
    )

def render_sidebar_filters():
    st.sidebar.title("Filters")

    with st.sidebar.expander("Hours per Week", expanded=False):
        hours_filter = st.radio(
            "",
            options=["All", "0 to 5", "6 to 10", "10+"],
            index=0
        )

    with st.sidebar.expander("Compensation Type", expanded=False):
        compensation_filter = st.radio(
            "",
            options=["All", "Paid", "Unpaid"],
            index=0
        )

    with st.sidebar.expander("Faculty", expanded=False):
        faculty_filter = st.radio(
            "",
            options=["All", "Imad Antonios", "Lisa Lancor", "Md Shafaeat Hossain"],
            index=0
        )

    return hours_filter, compensation_filter, faculty_filter


def render_listings(listings):
    for listing in listings:
        with st.container(border=True):
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

    # TEMPORARY: force faculty role so all tabs show
    if "role" not in st.session_state:
        st.session_state["role"] = "FACULTY"

    st.title("Research Opportunities 🔍")

    st.logo("images/scsu_logo.jpg", size="large")

    # Example of role (mock for now)
    # In future, this will come from session state: st.session_state["role"]
    user_role = st.session_state.get("role", "STUDENT")  # default to STUDENT for now

    # Role-based tab logic
    if user_role == "FACULTY":
        tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "My Listings"])
    else:
        tab1, = st.tabs(["Browse Listings"])

    # --- Tab 1: Browse Listings (current functionality) ---
    with tab1:
        hours_filter, compensation_filter, faculty_filter = render_sidebar_filters()
        listings = get_listings_data()
        filtered_listings = filter_listings(listings, hours_filter, compensation_filter, faculty_filter)

        if filtered_listings:
            render_listings(filtered_listings)
        else:
            st.info("No listings match your filters.")

    # --- Tab 2: Create Listing ---
    if user_role == "FACULTY":
        with tab2:
            st.header("Create a New Research Listing")
            st.info("Form for creating new research listings will go here.")

        # --- Tab 3: My Listings ---
        with tab3:
            st.header("My Listings")
            st.info("Faculty’s personal listings will appear here.")


if __name__ == "__main__":
    main()