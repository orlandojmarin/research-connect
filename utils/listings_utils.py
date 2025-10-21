# TATIANA
# listings_utils.py

import streamlit as st
from utils.auth_utils import db

def get_listings_data():
    """
    Returns mock data for research listings.
    """
    return [
        {
            "title": "Biometric Authentication Research",
            "pi": "Md Shafaeat Hossain",
            "team": "n/a",
            "department": "Computer Science",
            "skills": "Python, Artificial Intelligence, Machine Learning, Data Science",
            "openings": 1,
            "start_date": "January 2026",
            "duration": "1 year",
            "pay_rate": 16.35,
            "weekly_hours": 5,
            "summary": "Research focused on developing secure and scalable biometric authentication systems.",
            "date_posted": "September 28, 2025",
            "compensation_type": "paid",
        },
        {
            "title": "FOMO Analytics Project",
            "pi": "Imad Antonios",
            "team": "n/a",
            "department": "Computer Science, Data Science",
            "skills": "Python, Artificial Intelligence, Machine Learning, Data Science",
            "openings": 1,
            "start_date": "January 2026",
            "duration": "1 year",
            "pay_rate": 16.35,
            "weekly_hours": 5,
            "summary": "Analyze social media patterns to understand fear-of-missing-out behavior among users.",
            "date_posted": "September 1, 2025",
            "compensation_type": "paid",
        }
    ]


def save_listing_to_firebase(listing_data):
    """
    Save a new listing to Firebase Realtime Database.
    Returns the unique listing ID.
    """
    try:
        # Generate a unique key for the listing
        listing_ref = db.child("listings").push(listing_data)
        return listing_ref["name"]  # Returns the generated key
    except Exception as e:
        raise RuntimeError(f"Failed to save listing: {e}")


def get_all_listings_from_firebase():
    """
    Retrieve all listings from Firebase Realtime Database.
    Returns a list of listing dictionaries.
    """
    try:
        data = db.child("listings").get().val()
        if not data:
            return []
        
        # Convert Firebase dict to list of listings
        listings = []
        for listing_id, listing_data in data.items():
            listing_data["listing_id"] = listing_id  # Add the ID to each listing
            listings.append(listing_data)
        
        return listings
    except Exception:
        return []


def get_user_listings_from_firebase(uid):
    """
    Retrieve all listings created by a specific user.
    Returns a list of listing dictionaries.
    """
    try:
        all_listings = get_all_listings_from_firebase()
        return [listing for listing in all_listings if listing.get("posted_by_uid") == uid]
    except Exception:
        return []


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