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
            st.write("---")  # divider between listings for clarity

def main():
    configure_page()
    st.title("Research Opportunities 🔍")

    # Sidebar filters
    hours_filter, compensation_filter, faculty_filter = render_sidebar_filters()

    # Load listings and filter
    listings = get_listings_data()
    filtered_listings = filter_listings(listings, hours_filter, compensation_filter, faculty_filter)

    if filtered_listings:
        render_listings(filtered_listings)
    else:
        st.info("No listings match your filters.")

if __name__ == "__main__":
    main()