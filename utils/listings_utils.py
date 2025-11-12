# TATIANA
# listings_utils.py

# import streamlit as st
# from utils.auth_utils import db

# def save_listing_to_firebase(listing_data):
#     """
#     Save a new listing to Firebase Realtime Database using Firebase Admin SDK.
#     Returns the unique listing ID.
#     """
#     try:
#         # Firebase Admin SDK uses push() differently
#         listings_ref = db.child("listings")
#         new_listing_ref = listings_ref.push()
#         new_listing_ref.set(listing_data)
        
#         # Get the key/ID of the newly created listing
#         listing_id = new_listing_ref.key
#         return listing_id
#     except Exception as e:
#         raise RuntimeError(f"Failed to save listing: {e}")

# def update_listing_in_firebase(listing_id, updated_data):
#     """
#     Update an existing listing in Firebase Realtime Database.
    
#     Args:
#         listing_id: The unique listing ID
#         updated_data: Dictionary of fields to update
#     """
#     try:
#         listing_ref = db.child("listings").child(listing_id)
#         listing_ref.update(updated_data)
#         return True
#     except Exception as e:
#         raise RuntimeError(f"Failed to update listing {listing_id}: {e}")
    
# def get_all_listings_from_firebase():
#     """
#     Retrieve all listings from Firebase Realtime Database using Firebase Admin SDK.
#     Returns a list of listing dictionaries.
#     """
#     try:
#         listings_ref = db.child("listings")
#         data = listings_ref.get()  # Firebase Admin SDK returns dict directly, no .val() needed
        
#         if not data:
#             return []

#         listings = []
#         for listing_id, listing_data in data.items():
#             listing_data["listing_id"] = listing_id
#             listings.append(listing_data)

#         return listings
#     except Exception as e:
#         print(f"Error fetching listings: {e}")
#         return []


# def get_user_listings_from_firebase(uid):
#     """
#     Retrieve all listings created by a specific user.
#     Returns a list of listing dictionaries.
#     """
#     try:
#         all_listings = get_all_listings_from_firebase()
#         return [listing for listing in all_listings if listing.get("posted_by_uid") == uid]
#     except Exception as e:
#         print(f"Error fetching user listings: {e}")
#         return []


# def delete_listing_from_firebase(listing_id):
#     """
#     Delete a listing from Firebase Realtime Database by its unique listing ID.
#     """
#     try:
#         listing_ref = db.child("listings").child(listing_id)
#         listing_ref.delete()  # Firebase Admin SDK uses .delete() not .remove()
#         return True
#     except Exception as e:
#         raise RuntimeError(f"Failed to delete listing {listing_id}: {e}")


# def filter_listings(listings, hours_filter, compensation_filter, faculty_filter):
#     """
#     Filters listings based on sidebar selections.
#     """
#     filtered = []

#     for listing in listings:
#         # Hours per Week filter
#         hours_ok = False
#         if hours_filter == "All":
#             hours_ok = True
#         elif hours_filter == "0 to 5" and listing["weekly_hours"] <= 5:
#             hours_ok = True
#         elif hours_filter == "6 to 10" and 6 <= listing["weekly_hours"] <= 10:
#             hours_ok = True
#         elif hours_filter == "10+" and listing["weekly_hours"] > 10:
#             hours_ok = True

#         # Compensation filter
#         compensation_ok = (compensation_filter == "All" or listing["compensation_type"] == compensation_filter.lower())

#         # Faculty filter
#         faculty_ok = (faculty_filter == "All" or listing["pi"] == faculty_filter)

#         if hours_ok and compensation_ok and faculty_ok:
#             filtered.append(listing)

#     return filtered


# def toggle_favorite_listing(uid, listing_id):
#     """
#     Toggle a listing as favorite/unfavorite for a user using Firebase Admin SDK.
#     Stores favorites under users/{uid}/favorite_listings/{listing_id}
    
#     Args:
#         uid: User's unique ID
#         listing_id: Listing's unique ID
    
#     Returns:
#         bool: True if favorited, False if unfavorited
#     """
#     try:
#         # Check if already favorited
#         favorite_ref = db.child("users").child(uid).child("favorite_listings").child(listing_id)
#         current_value = favorite_ref.get()
        
#         if current_value:
#             # Already favorited, so remove it
#             favorite_ref.delete()
#             return False
#         else:
#             # Not favorited, so add it
#             favorite_ref.set(True)
#             return True
#     except Exception as e:
#         raise RuntimeError(f"Failed to toggle favorite for listing {listing_id}: {e}")


# def get_user_favorite_listings(uid):
#     """
#     Get all listing IDs that a user has favorited using Firebase Admin SDK.
    
#     Args:
#         uid: User's unique ID
    
#     Returns:
#         list: List of listing IDs that are favorited
#     """
#     try:
#         favorites_ref = db.child("users").child(uid).child("favorite_listings")
#         data = favorites_ref.get()
        
#         if not data:
#             return []
        
#         # Return list of listing IDs
#         return list(data.keys())
#     except Exception as e:
#         print(f"Error fetching favorite listings: {e}")
#         return []

# #-----END OF FILE-----

# modified faculty filter

# TATIANA
# listings_utils.py

import streamlit as st
from utils.auth_utils import db

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

#-----END OF FILE-----