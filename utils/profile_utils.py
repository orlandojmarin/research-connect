"""
Profile utilities for ResearchConnect SCSU
Handles fetching, updating, and deleting user data
"""

from utils.auth_utils import db

def get_user_profile(uid: str):
    """
    Fetch user profile data from Firebase Realtime Database
    Args:
        uid (str): Firebase user UID
    Returns:
        dict | None: User profile data
    """
    try:
        data = db.child("users").child(uid).get().val()
        return data or None
    except Exception:
        return None

def update_user_profile(uid: str, updates: dict):
    """
    Update user profile data in Firebase Realtime Database
    Args:
        uid (str): Firebase user UID
        updates (dict): Dictionary of fields to update (e.g., {"name": "New Name"})
    Raises:
        RuntimeError: If the update fails
    """
    try:
        db.child("users").child(uid).update(updates)
    except Exception as e:
        raise RuntimeError(f"Failed to update user profile: {e}")

def delete_user_data(uid: str):
    """
    Delete user data from Firebase Realtime Database
    Args:
        uid (str): Firebase user UID
    """
    try:
        db.child("users").child(uid).remove()
    except Exception as e:
        raise RuntimeError(f"Failed to remove user data: {e}")
    
#----END OF FILE-----
