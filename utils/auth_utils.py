# SANA
import pyrebase
from requests.exceptions import HTTPError
import requests
import json, unicodedata, re
import streamlit as st
import datetime

# ============================ SETTINGS ============================
ALLOWED_DOMAINS = {"southernct.edu"}

# When email already exists AND the provided password matches,
# we quietly delete the existing account and recreate it so
# "Create Account" always works in demos/tests.
ALLOW_RECREATE_SAME_EMAIL = True

# ============================ FIREBASE ============================
firebaseConfig = {
    "apiKey": "AIzaSyAZVSbKHQpLLnEH7rlPa3CoxAdQiV3aAYk",
    "authDomain": "researchconnect-scsu.firebaseapp.com",
    "projectId": "researchconnect-scsu",
    "storageBucket": "researchconnect-scsu.appspot.com",
    "messagingSenderId": "957316833349",
    "appId": "1:957316833349:web:197e9b2fcafd75e8ca432c",
    "measurementId": "G-YR8GM246SG",
    "databaseURL": "https://researchconnect-scsu-default-rtdb.firebaseio.com/",
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

# ============================ AUTH OPERATIONS ============================

def create_account(email: str, password: str, first_name: str, last_name: str):
    """Create a new Firebase user and store their profile in the database. Returns uid."""
    try:
        user = auth.create_user_with_email_and_password(email, password)
        uid = user["localId"]
    except HTTPError as ce:
        # Handle duplicate account case gracefully
        body = None
        try:
            body = ce.response.json()
        except Exception:
            pass
        code = (body or {}).get("error", {}).get("message", "")
        if "EMAIL_EXISTS" in code and ALLOW_RECREATE_SAME_EMAIL:
            try:
                signed = auth.sign_in_with_email_and_password(email, password)
                uid = signed["localId"]
            except Exception:
                raise ce
        else:
            raise ce

    # Save basic profile in DB
    db.child("users").child(uid).set({
        "email": email,
        "name": f"{first_name} {last_name}".strip(),
        "role": "student",
        "created_at": datetime.datetime.utcnow().isoformat() + "Z",
    })

    return uid

def sign_in(email: str, password: str):
    """Sign in a Firebase user and return (uid, id_token)."""
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        info = auth.get_account_info(user["idToken"])
        uid = info["users"][0]["localId"]
        return uid, user["idToken"]
    except HTTPError as e:
        # Re-raise with the original error so friendly_firebase_error can parse it
        raise e
    except Exception as e:
        # For non-HTTP errors, wrap them in a more informative message
        raise Exception(f"Login failed: {str(e)}")

def go(page: str):
    """Set the Streamlit session state page to navigate between app pages."""
    st.session_state.page = page

def logout():
    """Log out the current user by clearing session state."""
    st.session_state.user = None
    st.session_state.page = "landing"

#-----END OF FILE-----