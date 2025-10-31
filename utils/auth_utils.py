# SANA 
# Updated by Orlando to hide firebase credentials
import pyrebase
from requests.exceptions import HTTPError
import requests
import json, unicodedata, re
import streamlit as st
import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================ VALIDATE ENVIRONMENT VARIABLES ============================
required_env_vars = [
    "FIREBASE_API_KEY", "FIREBASE_AUTH_DOMAIN", "FIREBASE_PROJECT_ID",
    "FIREBASE_STORAGE_BUCKET", "FIREBASE_MESSAGING_SENDER_ID",
    "FIREBASE_APP_ID", "FIREBASE_MEASUREMENT_ID", "FIREBASE_DATABASE_URL"
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(
        f"⚠️  Missing required Firebase environment variables: {', '.join(missing_vars)}\n"
        f"Please create a .env file and add these variables.\n"
        f"See .env.example for the required format."
    )

# ============================ SETTINGS ============================
ALLOWED_DOMAINS = {"southernct.edu"}

# ============================ FIREBASE ============================
firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL"),
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

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

# ============================ AUTH OPERATIONS ============================

def create_account(email: str, password: str, first_name: str, last_name: str):
    """Create a new Firebase user and store their profile in the database. Returns uid."""
    user = auth.create_user_with_email_and_password(email, password)
    uid = user["localId"]

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

    # Save basic profile in DB
    db.child("users").child(uid).set({
        "email": email,
        "name": f"{first_name} {last_name}".strip(),
        "role": role,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })

    return uid

def sign_in(email: str, password: str):
    """Sign in a Firebase user and return (uid, id_token)."""
    user = auth.sign_in_with_email_and_password(email, password)
    info = auth.get_account_info(user["idToken"])
    uid = info["users"][0]["localId"]
    return uid, user["idToken"]

def go(page: str):
    """Set the Streamlit session state page to navigate between app pages."""
    st.session_state.page = page

def logout():
    """Log out the current user by clearing session state."""
    st.session_state.user = None
    st.session_state.page = "landing"

def delete_self_account(id_token: str):
    """Delete the currently authenticated Firebase user using their ID token."""
    # Try pyrebase helper if present
    try:
        auth.delete_user_account(id_token)  # some pyrebase builds have this
        return
    except Exception:
        pass
    # Fallback to REST
    api_key = firebaseConfig["apiKey"]
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={api_key}"
    r = requests.post(url, json={"idToken": id_token}, timeout=10)
    r.raise_for_status()

#-----END OF FILE-----