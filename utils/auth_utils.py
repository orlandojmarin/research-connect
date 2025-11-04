# import firebase_admin
# from firebase_admin import credentials, db as admin_db
# from requests.exceptions import HTTPError
# import requests
# import json
# import unicodedata
# import re
# import streamlit as st
# import datetime

# # Started by Sana 
# # Updated by Orlando to protect credentials and add email verification functionality
# # Updated for Python 3.13 compatibility

# # ============================ VALIDATE ENVIRONMENT VARIABLES ============================
# required_env_vars = [
#     "FIREBASE_API_KEY", "FIREBASE_AUTH_DOMAIN", "FIREBASE_PROJECT_ID",
#     "FIREBASE_STORAGE_BUCKET", "FIREBASE_MESSAGING_SENDER_ID",
#     "FIREBASE_APP_ID", "FIREBASE_MEASUREMENT_ID", "FIREBASE_DATABASE_URL"
# ]

# missing_vars = [var for var in required_env_vars if var not in st.secrets]
# if missing_vars:
#     raise EnvironmentError(
#         f"⚠️  Missing required Firebase secrets: {', '.join(missing_vars)}\n"
#         f"Please add these variables to Streamlit secrets.\n"
#     )

# # ============================ SETTINGS ============================
# ALLOWED_DOMAINS = {"southernct.edu"}

# # ============================ FIREBASE INITIALIZATION ============================
# # Initialize Firebase Admin SDK
# if not firebase_admin._apps:
#     try:
#         # Try to use service account credentials if available
#         cred = credentials.Certificate(dict(st.secrets["gcp_service_account"]))
#         firebase_admin.initialize_app(cred, {
#             'databaseURL': st.secrets["FIREBASE_DATABASE_URL"]
#         })
#     except Exception as e:
#         # Fallback to default credentials (shouldn't happen in production)
#         print(f"Warning: Could not initialize with service account: {e}")
#         firebase_admin.initialize_app(options={
#             'databaseURL': st.secrets["FIREBASE_DATABASE_URL"]
#         })

# # Get database reference
# db = admin_db.reference()

# # Store Firebase config for REST API calls
# firebaseConfig = {
#     "apiKey": st.secrets["FIREBASE_API_KEY"],
#     "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
#     "projectId": st.secrets["FIREBASE_PROJECT_ID"],
#     "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
#     "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
#     "appId": st.secrets["FIREBASE_APP_ID"],
#     "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"],
#     "databaseURL": st.secrets["FIREBASE_DATABASE_URL"],
# }

# # ============================ HELPERS ============================
# def sanitize_email(raw: str) -> str:
#     """Normalize email: remove whitespace, control chars, and lowercase it."""
#     if not raw:
#         return ""
#     txt = unicodedata.normalize("NFKC", raw)
#     txt = "".join(ch for ch in txt if not unicodedata.category(ch).startswith("C"))
#     txt = txt.replace(" ", "")
#     return txt.strip().lower()

# def is_allowed_sc_su_email(raw: str) -> bool:
#     """Check if the email is valid and belongs to an allowed SCSU domain."""
#     e = sanitize_email(raw)
#     if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e):
#         return False
#     domain = e.split("@", 1)[1].strip().strip(".")
#     return domain in ALLOWED_DOMAINS

# def strong_password(pw: str):
#     """Check if a password is strong (>=8 chars, includes letters and numbers). Returns (bool, msg)."""
#     if not pw or len(pw) < 8:
#         return False, "Password must be at least 8 characters."
#     if not any(c.isalpha() for c in pw):
#         return False, "Password must include a letter."
#     if not any(c.isdigit() for c in pw):
#         return False, "Password must include a number."
#     return True, ""

# def friendly_firebase_error(err: Exception) -> str:
#     """Convert Firebase REST API errors into user-friendly messages."""
#     default_msg = "Couldn't complete that. Please try again."
    
#     # Try to extract error information from HTTPError
#     if isinstance(err, HTTPError) and err.response is not None:
#         try:
#             # Try to parse JSON response
#             data = err.response.json()
#         except Exception:
#             try:
#                 data = json.loads(err.response.text)
#             except Exception:
#                 data = None
        
#         if data:
#             # Get error message from Firebase response
#             error_info = data.get("error", {})
#             if isinstance(error_info, dict):
#                 code = error_info.get("message", "")
#             else:
#                 code = str(error_info)
            
#             # Map Firebase error codes to user-friendly messages with SPECIFIC details
#             mapping = {
#                 "INVALID_EMAIL": "That email address doesn't look valid. Please check for typos.",
#                 "EMAIL_NOT_FOUND": "No account exists with this email address. Please create an account first or check for typos.",
#                 "INVALID_PASSWORD": "The password you entered is incorrect. Please try again.",
#                 "WRONG_PASSWORD": "The password you entered is incorrect. Please try again.",
#                 "USER_DISABLED": "This account has been disabled by an administrator. Please contact support.",
#                 "WEAK_PASSWORD": "Password is too weak. Use at least 8 characters with letters and numbers.",
#                 "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many failed login attempts. Please wait a few minutes and try again.",
#                 "EMAIL_EXISTS": "An account with this email already exists. Please log in instead.",
#                 "OPERATION_NOT_ALLOWED": "Email/password authentication is currently disabled.",
#                 "MISSING_PASSWORD": "Please enter a password.",
#                 "MISSING_EMAIL": "Please enter an email address.",
#             }
            
#             # Check for exact matches first
#             for key, nice in mapping.items():
#                 if key in code:
#                     return nice
            
#             # Special handling for INVALID_LOGIN_CREDENTIALS - check context
#             if "INVALID_LOGIN_CREDENTIALS" in code:
#                 # This is Firebase's generic error - we can't tell which is wrong
#                 return "The email or password you entered is incorrect. Please check both and try again."
            
#             # If no exact match, return a cleaned up version of the error code
#             if code:
#                 return code.replace("_", " ").capitalize()
    
#     # Check if it's a general exception with a message
#     error_msg = str(err)
#     if "EMAIL_NOT_FOUND" in error_msg:
#         return "No account exists with this email address. Please create an account first or check for typos."
#     if "INVALID_PASSWORD" in error_msg or "WRONG_PASSWORD" in error_msg:
#         return "The password you entered is incorrect. Please try again."
#     if "INVALID_LOGIN_CREDENTIALS" in error_msg:
#         return "The email or password you entered is incorrect. Please check both and try again."
    
#     return default_msg

# # ============================ EMAIL VERIFICATION ============================

# def get_continue_url():
#     """
#     Get the continue URL for email verification redirects.
#     Uses Streamlit secrets.
#     """
#     return st.secrets.get('APP_URL', 'http://localhost:8501')

# def send_verification_email(id_token: str):
#     """
#     Send email verification to the user with custom redirect URL.
    
#     Args:
#         id_token: Firebase ID token from sign-in or account creation
    
#     Returns:
#         bool: True if successful, False otherwise
#     """
#     try:
#         api_key = firebaseConfig["apiKey"]
#         url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        
#         # Get the app URL for redirect after verification
#         continue_url = get_continue_url()
        
#         payload = {
#             "requestType": "VERIFY_EMAIL",
#             "idToken": id_token,
#             "continueUrl": continue_url  # Redirect back to our app
#         }
        
#         response = requests.post(url, json=payload, timeout=10)
#         response.raise_for_status()
#         return True
        
#     except Exception as e:
#         print(f"Error sending verification email: {e}")
#         return False

# def check_email_verified(id_token: str) -> bool:
#     """
#     Check if user's email is verified using REST API.
    
#     Args:
#         id_token: Firebase ID token
    
#     Returns:
#         bool: True if email is verified, False otherwise
#     """
#     try:
#         api_key = firebaseConfig["apiKey"]
#         url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
        
#         payload = {"idToken": id_token}
#         response = requests.post(url, json=payload, timeout=10)
#         response.raise_for_status()
        
#         data = response.json()
#         users = data.get("users", [])
        
#         if users:
#             return users[0].get("emailVerified", False)
        
#         return False
        
#     except Exception as e:
#         print(f"Error checking email verification: {e}")
#         return False

# def resend_verification_email(email: str, password: str):
#     """
#     Resend verification email for a user.
    
#     Args:
#         email: User's email
#         password: User's password (needed to get fresh token)
    
#     Returns:
#         tuple: (success: bool, message: str)
#     """
#     try:
#         # Sign in to get a fresh token using REST API
#         api_key = firebaseConfig["apiKey"]
#         url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        
#         payload = {
#             "email": email,
#             "password": password,
#             "returnSecureToken": True
#         }
        
#         response = requests.post(url, json=payload, timeout=10)
#         response.raise_for_status()
        
#         data = response.json()
#         id_token = data["idToken"]
        
#         # Send verification email
#         if send_verification_email(id_token):
#             return True, "Verification email sent! Please check your inbox and spam folder."
#         else:
#             return False, "Failed to send verification email. Please try again later."
            
#     except Exception as e:
#         return False, friendly_firebase_error(e)

# def handle_verify_email_action(oob_code: str):
#     """
#     Handle email verification action when user clicks link in email.
#     This actually applies the verification to the user's account.
    
#     Args:
#         oob_code: The action code from the verification email URL
    
#     Returns:
#         tuple: (success: bool, message: str, email: str or None)
#     """
#     try:
#         api_key = firebaseConfig["apiKey"]
#         url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
        
#         payload = {
#             "oobCode": oob_code
#         }
        
#         response = requests.post(url, json=payload, timeout=10)
#         response.raise_for_status()
        
#         # Get the response data
#         data = response.json()
#         email = data.get("email", "")
        
#         return True, "Email verified successfully! You can now log in.", email
        
#     except HTTPError as e:
#         if e.response is not None:
#             try:
#                 error_data = e.response.json()
#                 error_message = error_data.get("error", {}).get("message", "")
                
#                 if "INVALID_OOB_CODE" in error_message:
#                     return False, "This verification link is invalid or has already been used.", None
#                 elif "EXPIRED_OOB_CODE" in error_message:
#                     return False, "This verification link has expired. Please request a new one.", None
#                 else:
#                     return False, "Unable to verify email. Please try again or request a new verification email.", None
#             except:
#                 pass
        
#         return False, "Unable to verify email. Please try again or request a new verification email.", None
    
#     except Exception as e:
#         print(f"Error handling email verification: {e}")
#         return False, "An error occurred while verifying your email. Please try again.", None

# # ============================ AUTH OPERATIONS ============================

# def create_account(email: str, password: str, first_name: str, last_name: str):
#     """
#     Create a new Firebase user, send verification email, and store their profile.
    
#     Returns:
#         tuple: (uid: str, id_token: str)
#     """
#     # Create user account using REST API
#     api_key = firebaseConfig["apiKey"]
#     url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    
#     payload = {
#         "email": email,
#         "password": password,
#         "returnSecureToken": True
#     }
    
#     response = requests.post(url, json=payload, timeout=10)
#     response.raise_for_status()
    
#     data = response.json()
#     uid = data["localId"]
#     id_token = data["idToken"]

#     # Determine role based on email
#     admin_emails = (
#         "marino1@southernct.edu",
#         "engt1@southernct.edu",
#         "muneerb1@southernct.edu",
#         "hossainm3@southernct.edu"
#     )

#     faculty_emails = (
#         "abdelraoufa1@southernct.edu",
#         "alseesis1@southernct.edu",
#         "antoniosi1@southernct.edu",
#         "elahia1@southernct.edu",
#         "islamm2@southernct.edu",
#         "kimc1@southernct.edu",
#         "lancorl1@southernct.edu",
#         "podnarh1@southernct.edu",
#         "seyedt1@southernct.edu",
#         "shetaa1@southernct.edu",
#         "upretya1@southernct.edu",
#         "wuh2@southernct.edu",
#         "yuw1@southernct.edu",
#         "pangy1@southernct.edu",
#         "lockwoodh1@southernct.edu",
#         "facultytest@southernct.edu"
#     )

#     # Assign role based on email
#     if email.lower() in admin_emails:
#         role = "admin"
#     elif email.lower() in faculty_emails:
#         role = "faculty"
#     else:
#         role = "student"

#     # Save basic profile in DB using Firebase Admin SDK syntax
#     user_ref = db.child("users").child(uid)
#     user_ref.set({
#         "email": email,
#         "name": f"{first_name} {last_name}".strip(),
#         "role": role,
#         "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
#         "email_verified": False  # Track verification status
#     })

#     # Send verification email
#     send_verification_email(id_token)

#     return uid, id_token

# def sign_in(email: str, password: str):
#     """
#     Sign in a Firebase user and return (uid, id_token, email_verified).
    
#     Returns:
#         tuple: (uid: str, id_token: str, email_verified: bool)
#     """
#     # Sign in using REST API
#     api_key = firebaseConfig["apiKey"]
#     url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
#     payload = {
#         "email": email,
#         "password": password,
#         "returnSecureToken": True
#     }
    
#     response = requests.post(url, json=payload, timeout=10)
#     response.raise_for_status()
    
#     data = response.json()
#     id_token = data["idToken"]
#     uid = data["localId"]
    
#     # IMPORTANT: Get fresh account info to check current verification status
#     # The sign-in response might have stale emailVerified status
#     lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
#     lookup_payload = {"idToken": id_token}
#     lookup_response = requests.post(lookup_url, json=lookup_payload, timeout=10)
#     lookup_response.raise_for_status()
    
#     lookup_data = lookup_response.json()
#     users = lookup_data.get("users", [])
#     email_verified = users[0].get("emailVerified", False) if users else False
    
#     # Update verification status in database using Firebase Admin SDK syntax
#     if email_verified:
#         user_ref = db.child("users").child(uid)
#         user_ref.update({"email_verified": True})
    
#     return uid, id_token, email_verified

# def go(page: str):
#     """Set the Streamlit session state page to navigate between app pages."""
#     st.session_state.page = page

# def logout():
#     """Log out the current user by clearing session state."""
#     st.session_state.user = None
#     st.session_state.page = "landing"

# def delete_self_account(id_token: str):
#     """Delete the currently authenticated Firebase user using their ID token."""
#     # Use REST API to delete account
#     api_key = firebaseConfig["apiKey"]
#     url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}"
#     r = requests.post(url, json={"idToken": id_token}, timeout=10)
#     r.raise_for_status()

# #-----END OF FILE-----

import firebase_admin
from firebase_admin import credentials, db as admin_db, auth as admin_auth
from requests.exceptions import HTTPError
import requests
import json
import unicodedata
import re
import streamlit as st
import datetime

# ============================ VALIDATE ENVIRONMENT VARIABLES ============================
required_env_vars = [
    "FIREBASE_API_KEY", "FIREBASE_AUTH_DOMAIN", "FIREBASE_PROJECT_ID",
    "FIREBASE_STORAGE_BUCKET", "FIREBASE_MESSAGING_SENDER_ID",
    "FIREBASE_APP_ID", "FIREBASE_MEASUREMENT_ID", "FIREBASE_DATABASE_URL"
]

missing_vars = [var for var in required_env_vars if var not in st.secrets]
if missing_vars:
    raise EnvironmentError(
        f"⚠️  Missing required Firebase secrets: {', '.join(missing_vars)}\n"
        f"Please add these variables to Streamlit secrets.\n"
    )

# ============================ SETTINGS ============================
ALLOWED_DOMAINS = {"southernct.edu"}

# ============================ FIREBASE INITIALIZATION ============================
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(dict(st.secrets["gcp_service_account"]))
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["FIREBASE_DATABASE_URL"]
        })
    except Exception as e:
        print(f"Warning: Could not initialize with service account: {e}")
        firebase_admin.initialize_app(options={
            'databaseURL': st.secrets["FIREBASE_DATABASE_URL"]
        })

# Get database reference
db = admin_db.reference()

# Store Firebase config for REST API calls
firebaseConfig = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": st.secrets["FIREBASE_STORAGE_BUCKET"],
    "messagingSenderId": st.secrets["FIREBASE_MESSAGING_SENDER_ID"],
    "appId": st.secrets["FIREBASE_APP_ID"],
    "measurementId": st.secrets["FIREBASE_MEASUREMENT_ID"],
    "databaseURL": st.secrets["FIREBASE_DATABASE_URL"],
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
    
    if isinstance(err, HTTPError) and err.response is not None:
        try:
            data = err.response.json()
        except Exception:
            try:
                data = json.loads(err.response.text)
            except Exception:
                data = None
        
        if data:
            error_info = data.get("error", {})
            if isinstance(error_info, dict):
                code = error_info.get("message", "")
            else:
                code = str(error_info)
            
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
            
            for key, nice in mapping.items():
                if key in code:
                    return nice
            
            if "INVALID_LOGIN_CREDENTIALS" in code:
                return "The email or password you entered is incorrect. Please check both and try again."
            
            if code:
                return code.replace("_", " ").capitalize()
    
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
    Uses APP_URL from secrets with fallback to localhost.
    """
    app_url = st.secrets.get('APP_URL', 'http://localhost:8501')
    
    # Remove trailing slash if present for consistency
    return app_url.rstrip('/')

def send_verification_email(id_token: str):
    """Send email verification to the user with custom redirect URL."""
    try:
        api_key = firebaseConfig["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        
        continue_url = get_continue_url()
        
        payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token,
            "continueUrl": continue_url
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
        
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False

def check_email_verified_via_admin(uid: str) -> bool:
    """
    Check if user's email is verified using Firebase Admin SDK.
    This is the authoritative source for verification status.
    """
    try:
        user = admin_auth.get_user(uid)
        return user.email_verified
    except Exception as e:
        print(f"Error checking email verification via Admin SDK: {e}")
        return False

def check_email_verified(id_token: str) -> bool:
    """Check if user's email is verified using REST API."""
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
    """Resend verification email for a user."""
    try:
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
        
        if send_verification_email(id_token):
            return True, "Verification email sent! Please check your inbox and spam folder."
        else:
            return False, "Failed to send verification email. Please try again later."
            
    except Exception as e:
        return False, friendly_firebase_error(e)

def handle_verify_email_action(oob_code: str):
    """Handle email verification action when user clicks link in email."""
    try:
        api_key = firebaseConfig["apiKey"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={api_key}"
        
        payload = {
            "oobCode": oob_code
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        email = data.get("email", "")
        
        # CRITICAL: Get the localId (uid) from the response to update database
        uid = data.get("localId")
        
        # Update the database to reflect verified status
        if uid:
            try:
                user_ref = db.child("users").child(uid)
                user_ref.update({"email_verified": True})
            except Exception as db_error:
                print(f"Warning: Could not update database verification status: {db_error}")
        
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

# ============================ AUTH OPERATIONS ============================

def create_account(email: str, password: str, first_name: str, last_name: str):
    """Create a new Firebase user, send verification email, and store their profile."""
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

    if email.lower() in admin_emails:
        role = "admin"
    elif email.lower() in faculty_emails:
        role = "faculty"
    else:
        role = "student"

    # Save basic profile in DB
    user_ref = db.child("users").child(uid)
    user_ref.set({
        "email": email,
        "name": f"{first_name} {last_name}".strip(),
        "role": role,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "email_verified": False  # Important: Start as False
    })

    # Send verification email
    send_verification_email(id_token)

    return uid, id_token

# def sign_in(email: str, password: str):
#     """
#     Sign in a Firebase user and return (uid, id_token, email_verified).
#     CRITICAL: This now properly checks verification status using Admin SDK.
#     """
#     # Sign in using REST API
#     api_key = firebaseConfig["apiKey"]
#     url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
#     payload = {
#         "email": email,
#         "password": password,
#         "returnSecureToken": True
#     }
    
#     response = requests.post(url, json=payload, timeout=10)
#     response.raise_for_status()
    
#     data = response.json()
#     id_token = data["idToken"]
#     uid = data["localId"]
    
#     # CRITICAL FIX: Use Admin SDK to get authoritative verification status
#     # This is more reliable than the REST API response
#     email_verified = check_email_verified_via_admin(uid)
    
#     # Update verification status in database to keep it in sync
#     user_ref = db.child("users").child(uid)
#     user_ref.update({"email_verified": email_verified})
    
#     return uid, id_token, email_verified

def sign_in(email: str, password: str):
    """
    Sign in a Firebase user and return (uid, id_token, email_verified).
    CRITICAL: Forces a fresh token refresh to get latest verification status.
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
    
    # CRITICAL FIX: Force a token refresh to get the LATEST verification status
    # The initial sign-in token might have stale emailVerified data
    refresh_url = f"https://securetoken.googleapis.com/v1/token?key={api_key}"
    refresh_payload = {
        "grant_type": "refresh_token",
        "refresh_token": data["refreshToken"]
    }
    
    try:
        refresh_response = requests.post(refresh_url, json=refresh_payload, timeout=10)
        refresh_response.raise_for_status()
        refresh_data = refresh_response.json()
        
        # Get fresh ID token
        fresh_id_token = refresh_data["id_token"]
        
        # Now check verification status with the fresh token
        lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
        lookup_payload = {"idToken": fresh_id_token}
        lookup_response = requests.post(lookup_url, json=lookup_payload, timeout=10)
        lookup_response.raise_for_status()
        
        lookup_data = lookup_response.json()
        users = lookup_data.get("users", [])
        
        if users:
            email_verified = users[0].get("emailVerified", False)
        else:
            # Fallback to Admin SDK if lookup fails
            email_verified = check_email_verified_via_admin(uid)
    
    except Exception as e:
        print(f"Warning: Token refresh failed, using Admin SDK: {e}")
        # Fallback to Admin SDK
        email_verified = check_email_verified_via_admin(uid)
    
    # Update verification status in database to keep it in sync
    user_ref = db.child("users").child(uid)
    user_ref.update({"email_verified": email_verified})
    
    # Return the fresh token (or original if refresh failed)
    return uid, fresh_id_token if 'fresh_id_token' in locals() else id_token, email_verified

def go(page: str):
    """Set the Streamlit session state page to navigate between app pages."""
    st.session_state.page = page

def logout():
    """Log out the current user by clearing session state."""
    st.session_state.user = None
    st.session_state.page = "landing"

def delete_self_account(id_token: str):
    """Delete the currently authenticated Firebase user using their ID token."""
    api_key = firebaseConfig["apiKey"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}"
    r = requests.post(url, json={"idToken": id_token}, timeout=10)
    r.raise_for_status()

#-----END OF FILE-----