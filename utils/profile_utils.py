# ORLANDO
# profile_utils.py

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
        user_ref = db.child("users").child(uid)
        data = user_ref.get()  # Firebase Admin SDK syntax - no .val() needed
        return data or None
    except Exception as e:
        print(f"Error fetching user profile: {e}")
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
        user_ref = db.child("users").child(uid)
        user_ref.update(updates)
    except Exception as e:
        raise RuntimeError(f"Failed to update user profile: {e}")

def delete_user_data(uid: str):
    """
    Delete user data from Firebase Realtime Database
    Args:
        uid (str): Firebase user UID
    """
    try:
        user_ref = db.child("users").child(uid)
        user_ref.delete()  # Firebase Admin SDK uses .delete() not .remove()
    except Exception as e:
        raise RuntimeError(f"Failed to remove user data: {e}")

def get_all_users():
    """
    Retrieve all users from Firebase Realtime Database (Admin only)
    Returns:
        list: List of user dictionaries with uid included
    """
    try:
        users_ref = db.child("users")
        data = users_ref.get()  # Firebase Admin SDK returns dict directly
        
        if not data:
            return []
        
        users = []
        for uid, user_data in data.items():
            user_data["uid"] = uid
            users.append(user_data)
        
        return users
    except Exception as e:
        print(f"Error fetching all users: {e}")
        return []

def update_user_role(uid: str, new_role: str):
    """
    Update a user's role in Firebase Realtime Database (Admin only)
    
    Safety Check: Prevents demoting admins if fewer than 2 would remain
    
    Args:
        uid (str): Firebase user UID
        new_role (str): New role to assign (student, faculty, or admin)
    Raises:
        ValueError: If the role is not valid
        RuntimeError: If the update fails or safety check fails
    """
    # Validate role
    valid_roles = ["student", "faculty", "admin"]
    if new_role not in valid_roles:
        raise ValueError(f"Invalid role: {new_role}. Must be one of {valid_roles}")
    
    # Safety check: ensure at least 2 admins remain
    try:
        # Get current user's role
        user_ref = db.child("users").child(uid)
        current_user = user_ref.get()
        current_role = current_user.get('role') if current_user else None
        
        # If demoting an admin, check admin count
        if current_role == "admin" and new_role != "admin":
            admin_count = count_admins()
            if admin_count <= 2:
                raise RuntimeError(
                    f"Cannot demote admin: only {admin_count} admin(s) exist. "
                    "At least 2 admins must remain for safety."
                )
        
        # Proceed with update
        user_ref.update({"role": new_role})
        
    except Exception as e:
        if isinstance(e, RuntimeError):
            raise e
        raise RuntimeError(f"Failed to update user role: {e}")

def count_admins():
    """
    Count the total number of admin users in the database
    
    Returns:
        int: Number of users with role="admin"
    """
    try:
        all_users = get_all_users()
        return sum(1 for user in all_users if user.get('role') == 'admin')
    except Exception as e:
        print(f"Error counting admins: {e}")
        return 0

#----END OF FILE-----
