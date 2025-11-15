# auth_utils.py
# Started by Sana
# Updated by Orlando to add email verification functionality

import firebase_admin
from firebase_admin import credentials, db as admin_db
from requests.exceptions import HTTPError
import requests
import json
import unicodedata
import re
import streamlit as st
import datetime
import os

# ============================ CONFIG HELPER ============================
def get_config(key, default=None):
    """
    Get config from environment variables (Cloud Run) or st.secrets (local).
    
    Args:
        key: Configuration key to retrieve
        default: Default value if key not found
    
    Returns:
        Configuration value or default
    """
    # Try environment variable first (for Cloud Run)
    env_value = os.environ.get(key)
    if env_value:
        return env_value
    
    # Fall back to st.secrets (for local development)
    try:
        return st.secrets[key]
    except:
        return default

# ============================ VALIDATE ENVIRONMENT VARIABLES ============================
required_env_vars = [
    "FIREBASE_API_KEY", "FIREBASE_AUTH_DOMAIN", "FIREBASE_PROJECT_ID",
    "FIREBASE_STORAGE_BUCKET", "FIREBASE_MESSAGING_SENDER_ID",
    "FIREBASE_APP_ID", "FIREBASE_MEASUREMENT_ID", "FIREBASE_DATABASE_URL"
]

missing_vars = [var for var in required_env_vars if get_config(var) is None]
if missing_vars:
    raise EnvironmentError(
        f"⚠️  Missing required Firebase configuration: {', '.join(missing_vars)}\n"
        f"Please add these as environment variables or in Streamlit secrets.\n"
    )

# ============================ SETTINGS ============================
ALLOWED_DOMAINS = {"southernct.edu"}

# ============================ FIREBASE INITIALIZATION ============================
# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        # Try to get service account from environment variable first (Cloud Run)
        service_account_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
        
        if service_account_json:
            # Cloud Run: parse JSON string from environment variable
            service_account_dict = json.loads(service_account_json)
            cred = credentials.Certificate(service_account_dict)
        else:
            # Local: use secrets.toml
            try:
                cred = credentials.Certificate(dict(st.secrets["gcp_service_account"]))
            except:
                # Fallback: try default credentials
                print("Warning: Using default credentials for Firebase Admin SDK")
                firebase_admin.initialize_app(options={
                    'databaseURL': get_config("FIREBASE_DATABASE_URL")
                })
                cred = None
        
        if cred:
            firebase_admin.initialize_app(cred, {
                'databaseURL': get_config("FIREBASE_DATABASE_URL")
            })
    except Exception as e:
        print(f"Warning: Could not initialize with service account: {e}")
        # Last resort fallback
        firebase_admin.initialize_app(options={
            'databaseURL': get_config("FIREBASE_DATABASE_URL")
        })

# Get database reference
db = admin_db.reference()

# Store Firebase config for REST API calls
firebaseConfig = {
    "apiKey": get_config("FIREBASE_API_KEY"),
    "authDomain": get_config("FIREBASE_AUTH_DOMAIN"),
    "projectId": get_config("FIREBASE_PROJECT_ID"),
    "storageBucket": get_config("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": get_config("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": get_config("FIREBASE_APP_ID"),
    "measurementId": get_config("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": get_config("FIREBASE_DATABASE_URL"),
}

# ============================ HELPERS ============================
def sanitize_email(raw: str) -> str:
    """Normalize email: remove whitespace, control chars, and lowercase it."""
    if not raw:
        return ""
    txt = unicodedata.normalize("NFKC", raw)
    txt = "".join(ch for ch in txt if not unicodedata.category(ch).startswith("C"))
    txt = txt.replace(" ", "")
    return txt.strip().lower()

def is_allowed_sc_su_email(raw: str) -> bool:
    """Check if the email is valid and belongs to an allowed SCSU domain."""
    e = sanitize_email(raw)
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e):
        return False
    domain = e.split("@", 1)[1].strip().strip(".")
    return domain in ALLOWED_DOMAINS

def strong_password(pw: str):
    """Check if a password is strong (>=8 chars, includes letters and numbers). Returns (bool, msg)."""
    if not pw or len(pw) < 8:
        return False, "Password must be at least 8 characters."
    if not any(c.isalpha() for c in pw):
        return False, "Password must include a letter."
    if not any(c.isdigit() for c in pw):
        return False, "Password must include a number."
    return True, ""

def friendly_firebase_error(err: Exception) -> str:
    """Convert Firebase REST API errors into user-friendly messages."""
    default_msg = "Couldn't complete that. Please try again."
    
    # Try to extract error information from HTTPError
    if isinstance(err, HTTPError) and err.response is not None:
        try:
            # Try to parse JSON response
            data = err.response.json()
        except Exception:
            try:
                data = json.loads(err.response.text)
            except Exception:
                data = None
        
        if data:
            # Get error message from Firebase response
            error_info = data.get("error", {})
            if isinstance(error_info, dict):
                code = error_info.get("message", "")
            else:
                code = str(error_info)
            
            # Map Firebase error codes to user-friendly messages with SPECIFIC details
            mapping = {
                "INVALID_EMAIL": "That email address doesn't look valid. Please check for typos.",
                "EMAIL_NOT_FOUND": "No account exists with this email address. Please create an account first or check for typos.",
                "INVALID_PASSWORD": "The password you entered is incorrect. Please try again.",
                "WRONG_PASSWORD": "The password you entered is incorrect. Please try again.",
                "USER_DISABLED": "This account has been disabled by an administrator. Please contact support.",
                "WEAK_PASSWORD": "Password is too weak. Use at least 8 characters with letters and numbers.",
                "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed login attempts. Please wait a few minutes and try again.",
                "EMAIL_EXISTS": "An account with this email already exists. Please log in instead.",
                "OPERATION_NOT_ALLOWED": "Email/password authentication is currently disabled.",
                "MISSING_PASSWORD": "Please enter a password.",
                "MISSING_EMAIL": "Please enter an email address.",
            }
            
            # Check for exact matches first
            for key, nice in mapping.items():
                if key in code:
                    return nice
            
            # Special handling for INVALID_LOGIN_CREDENTIALS - check context
            if "INVALID_LOGIN_CREDENTIALS" in code:
                # This is Firebase's generic error - we can't tell which is wrong
                return "The email or password you entered is incorrect. Please check both and try again."
            
            # If no exact match, return a cleaned up version of the error code
            if code:
                return code.replace("_", " ").capitalize()
    
    # Check if it's a general exception with a message
    error_msg = str(err)
    if "EMAIL_NOT_FOUND" in error_msg:
        return "No account exists with this email address. Please create an account first or check for typos."
    if "INVALID_PASSWORD" in error_msg or "WRONG_PASSWORD" in error_msg:
        return "The password you entered is incorrect. Please try again."
    if "INVALID_LOGIN_CREDENTIALS" in error_msg:
        return "The email or password you entered is incorrect. Please check both and try again."
    
    return default_msg

# ============================ EMAIL VERIFICATION ============================

def get_continue_url():
    """
    Get the continue URL for email verification redirects.
    Uses environment variables or Streamlit secrets.
    """
    return get_config('APP_URL', 'http://localhost:8501')

def send_verification_email(id_token: str):
    """
    Send email verification to the user with custom redirect URL.
    
    Args:
        id_token: Firebase ID token from sign-in or account creation
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        api_key = firebaseConfig["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        
        # Get the app URL for redirect after verification
        continue_url = get_continue_url()
        
        payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token,
            "continueUrl": continue_url  # Redirect back to our app
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False

def check_email_verified(id_token: str) -> bool:
    """
    Check if user's email is verified using REST API.
    
    Args:
        id_token: Firebase ID token
    
    Returns:
        bool: True if email is verified, False otherwise
    """
    try:
        api_key = firebaseConfig["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
        
        payload = {"idToken": id_token}
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        users = data.get("users", [])
        
        if users:
            return users[0].get("emailVerified", False)
        
        return False
        
    except Exception as e:
        print(f"Error checking email verification: {e}")
        return False

def resend_verification_email(email: str, password: str):
    """
    Resend verification email for a user.
    
    Args:
        email: User's email
        password: User's password (needed to get fresh token)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Sign in to get a fresh token using REST API
        api_key = firebaseConfig["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        id_token = data["idToken"]
        
        # Send verification email
        if send_verification_email(id_token):
            return True, "Verification email sent! Please check your inbox and spam folder."
        else:
            return False, "Failed to send verification email. Please try again later."
            
    except Exception as e:
        return False, friendly_firebase_error(e)

def handle_verify_email_action(oob_code: str):
    """
    Handle email verification action when user clicks link in email.
    This actually applies the verification to the user's account.
    
    Args:
        oob_code: The action code from the verification email URL
    
    Returns:
        tuple: (success: bool, message: str, email: str or None)
    """
    try:
        api_key = firebaseConfig["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
        
        payload = {
            "oobCode": oob_code
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        # Get the response data
        data = response.json()
        email = data.get("email", "")
        
        return True, "Email verified successfully! You can now log in.", email
        
    except HTTPError as e:
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get("error", {}).get("message", "")
                
                if "INVALID_OOB_CODE" in error_message:
                    return False, "This verification link is invalid or has already been used.", None
                elif "EXPIRED_OOB_CODE" in error_message:
                    return False, "This verification link has expired. Please request a new one.", None
                else:
                    return False, "Unable to verify email. Please try again or request a new verification email.", None
            except:
                pass
        
        return False, "Unable to verify email. Please try again or request a new verification email.", None
    
    except Exception as e:
        print(f"Error handling email verification: {e}")
        return False, "An error occurred while verifying your email. Please try again.", None

# ============================ PASSWORD RESET ============================

def send_password_reset_email(email: str):
    """
    Send password reset email to user.
    
    Args:
        email: User's email address
    
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        api_key = firebaseConfig["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        return True, "Password reset email sent! Please check your inbox."
        
    except HTTPError as e:
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get("error", {}).get("message", "")
                
                if "EMAIL_NOT_FOUND" in error_message:
                    return False, "No account exists with this email address."
                else:
                    return False, friendly_firebase_error(e)
            except:
                pass
        
        return False, friendly_firebase_error(e)
    
    except Exception as e:
        return False, f"Failed to send password reset email: {str(e)}"

def handle_password_reset_action(oob_code: str, new_password: str, current_password_check: str = None):
    """
    Complete password reset using the code from reset email.
    
    Args:
        oob_code: The action code from the password reset email URL
        new_password: The new password to set
        current_password_check: Optional current password to verify it's different
    
    Returns:
        tuple: (success: bool, message: str, email: str or None)
    """
    try:
        # Validate new password strength
        is_strong, msg = strong_password(new_password)
        if not is_strong:
            return False, msg, None
        
        # First, verify the code and get the email (without resetting yet)
        api_key = firebaseConfig["apiKey"]
        
        # Verify the reset code is valid and get user email
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={api_key}"
        
        # First call without newPassword to verify code and get email
        verify_payload = {
            "oobCode": oob_code
        }
        
        verify_response = requests.post(verify_url, json=verify_payload, timeout=10)
        
        # If code is valid, we get the email back
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            email = verify_data.get("email", "")
            
            # Now try to sign in with the new password to check if it's the same as current
            if email:
                signin_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
                signin_payload = {
                    "email": email,
                    "password": new_password,
                    "returnSecureToken": True
                }
                
                # Try signing in with the new password
                try:
                    signin_response = requests.post(signin_url, json=signin_payload, timeout=10)
                    
                    # If sign-in succeeds, the new password is the same as current password
                    if signin_response.status_code == 200:
                        return False, "Your new password cannot be the same as your current password. Please choose a different password.", email
                except:
                    # Sign-in failed, which means password is different - this is what we want
                    pass
            
            # Password is different, proceed with reset
            reset_payload = {
                "oobCode": oob_code,
                "newPassword": new_password
            }
            
            reset_response = requests.post(verify_url, json=reset_payload, timeout=10)
            reset_response.raise_for_status()
            
            return True, "Password reset successfully! You can now log in with your new password.", email
        else:
            # Handle verification errors
            verify_response.raise_for_status()
        
    except HTTPError as e:
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get("error", {}).get("message", "")
                
                if "INVALID_OOB_CODE" in error_message:
                    return False, "This password reset link is invalid or has already been used.", None
                elif "EXPIRED_OOB_CODE" in error_message:
                    return False, "This password reset link has expired. Please request a new one.", None
                else:
                    return False, "Unable to reset password. Please try again or request a new reset link.", None
            except:
                pass
        
        return False, "Unable to reset password. Please try again or request a new reset link.", None
    
    except Exception as e:
        print(f"Error handling password reset: {e}")
        return False, "An error occurred while resetting your password. Please try again.", None

def change_password(email: str, current_password: str, new_password: str):
    """
    Change user's password after verifying current password.
    
    Args:
        email: User's email
        current_password: Current password for verification
        new_password: New password to set
    
    Returns:
        tuple: (success: bool, message: str, new_token: str or None)
    """
    try:
        # First, verify current password by signing in
        api_key = firebaseConfig["apiKey"]
        signin_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        
        signin_payload = {
            "email": email,
            "password": current_password,
            "returnSecureToken": True
        }
        
        signin_response = requests.post(signin_url, json=signin_payload, timeout=10)
        signin_response.raise_for_status()
        
        signin_data = signin_response.json()
        id_token = signin_data["idToken"]
        
        # Validate new password strength
        is_strong, msg = strong_password(new_password)
        if not is_strong:
            return False, msg, None
        
        # Update password using the verified token
        update_url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
        
        update_payload = {
            "idToken": id_token,
            "password": new_password,
            "returnSecureToken": True
        }
        
        update_response = requests.post(update_url, json=update_payload, timeout=10)
        update_response.raise_for_status()
        
        update_data = update_response.json()
        new_token = update_data["idToken"]
        
        return True, "Password changed successfully!", new_token
        
    except HTTPError as e:
        if e.response is not None:
            try:
                error_data = e.response.json()
                error_message = error_data.get("error", {}).get("message", "")
                
                if "INVALID_PASSWORD" in error_message or "WRONG_PASSWORD" in error_message or "INVALID_LOGIN_CREDENTIALS" in error_message:
                    return False, "Current password is incorrect. Please try again.", None
                else:
                    return False, friendly_firebase_error(e), None
            except:
                pass
        
        return False, friendly_firebase_error(e), None
    
    except Exception as e:
        return False, f"Failed to change password: {str(e)}", None

# ============================ AUTH OPERATIONS ============================

def create_account(email: str, password: str, first_name: str, last_name: str):
    """
    Create a new Firebase user, send verification email, and store their profile.
    
    Returns:
        tuple: (uid: str, id_token: str)
    """
    # Create user account using REST API
    api_key = firebaseConfig["apiKey"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    uid = data["localId"]
    id_token = data["idToken"]

    # Determine role based on email
    admin_emails = (
        "marino1@southernct.edu",
        "engt1@southernct.edu",
        "muneerb1@southernct.edu",
        "hossainm3@southernct.edu"
    )

    faculty_emails = (
        "abdelraoufa1@southernct.edu",
        "alseesis1@southernct.edu",
        "antoniosi1@southernct.edu",
        "elahia1@southernct.edu",
        "islamm2@southernct.edu",
        "kimc1@southernct.edu",
        "lancorl1@southernct.edu",
        "podnarh1@southernct.edu",
        "seyedt1@southernct.edu",
        "shetaa1@southernct.edu",
        "upretya1@southernct.edu",
        "wuh2@southernct.edu",
        "yuw1@southernct.edu",
        "pangy1@southernct.edu",
        "lockwoodh1@southernct.edu",
        "facultytest@southernct.edu"
    )

    # Assign role based on email
    if email.lower() in admin_emails:
        role = "admin"
    elif email.lower() in faculty_emails:
        role = "faculty"
    else:
        role = "student"

    # Save basic profile in DB using Firebase Admin SDK syntax
    user_ref = db.child("users").child(uid)
    user_ref.set({
        "email": email,
        "name": f"{first_name} {last_name}".strip(),
        "role": role,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email_verified": False  # Track verification status
    })

    # Send verification email
    send_verification_email(id_token)

    return uid, id_token

def sign_in(email: str, password: str):
    """
    Sign in a Firebase user and return (uid, id_token, email_verified).
    
    Returns:
        tuple: (uid: str, id_token: str, email_verified: bool)
    """
    # Sign in using REST API
    api_key = firebaseConfig["apiKey"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    id_token = data["idToken"]
    uid = data["localId"]
    
    # IMPORTANT: Get fresh account info to check current verification status
    # The sign-in response might have stale emailVerified status
    lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
    lookup_payload = {"idToken": id_token}
    lookup_response = requests.post(lookup_url, json=lookup_payload, timeout=10)
    lookup_response.raise_for_status()
    
    lookup_data = lookup_response.json()
    users = lookup_data.get("users", [])
    email_verified = users[0].get("emailVerified", False) if users else False
    
    # Update verification status in database using Firebase Admin SDK syntax
    if email_verified:
        user_ref = db.child("users").child(uid)
        user_ref.update({"email_verified": True})
    
    return uid, id_token, email_verified

def go(page: str):
    """Set the Streamlit session state page to navigate between app pages."""
    st.session_state.page = page

def logout():
    """Log out the current user by clearing session state."""
    st.session_state.user = None
    st.session_state.page = "landing"

def delete_self_account(id_token: str):
    """Delete the currently authenticated Firebase user using their ID token."""
    # Use REST API to delete account
    api_key = firebaseConfig["apiKey"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}"
    r = requests.post(url, json={"idToken": id_token}, timeout=10)
    r.raise_for_status()

#-----END OF FILE-----