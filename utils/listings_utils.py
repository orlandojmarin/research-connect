# TATIANA
# listings_utils.py

import streamlit as st
from utils.auth_utils import db

def save_listing_to_firebase(listing_data):
    """
    Save a new listing to Firebase Realtime Database.
    Returns the unique listing ID.
    """
    try:
        listing_ref = db.child("listings").push(listing_data)
        return listing_ref["name"]  # Returns the generated key
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
        db.child("listings").child(listing_id).update(updated_data)
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to update listing {listing_id}: {e}")
    
def get_all_listings_from_firebase():
    """
    Retrieve all listings from Firebase Realtime Database.
    Returns a list of listing dictionaries.
    """
    try:
        data = db.child("listings").get().val()
        if not data:
            return []

        listings = []
        for listing_id, listing_data in data.items():
            listing_data["listing_id"] = listing_id
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


def delete_listing_from_firebase(listing_id):
    """
    Delete a listing from Firebase Realtime Database by its unique listing ID.
    """
    try:
        db.child("listings").child(listing_id).remove()
        return True
    except Exception as e:
        raise RuntimeError(f"Failed to delete listing {listing_id}: {e}")


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