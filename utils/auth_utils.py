#Sana
import pyrebase
from requests.exceptions import HTTPError
import requests
import json, unicodedata, re

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
    """Normalize, strip whitespace, remove zero-width/control chars."""
    if not raw:
        return ""
    txt = unicodedata.normalize("NFKC", raw)
    txt = "".join(ch for ch in txt if not unicodedata.category(ch).startswith("C"))
    txt = txt.replace(" ", "")
    return txt.strip().lower()

def is_allowed_sc_su_email(raw: str) -> bool:
    e = sanitize_email(raw)
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e):
        return False
    domain = e.split("@", 1)[1].strip().strip(".")
    return domain in ALLOWED_DOMAINS

def strong_password(pw: str):
    # Simple rule: >= 8 chars, includes a letter and a number
    if not pw or len(pw) < 8:
        return False, "Password must be at least 8 characters."
    if not any(c.isalpha() for c in pw):
        return False, "Password must include a letter."
    if not any(c.isdigit() for c in pw):
        return False, "Password must include a number."
    return True, ""

def friendly_firebase_error(err: Exception) -> str:
    """Turn Firebase REST error codes into friendly messages."""
    default_msg = "Couldn’t complete that. Please try again."
    if isinstance(err, HTTPError) and err.response is not None:
        try:
            data = err.response.json()
        except Exception:
            try:
                data = json.loads(err.response.text)
            except Exception:
                data = None
        if data:
            code = (data.get("error", {}) or {}).get("message", "")
            mapping = {
                "INVALID_EMAIL": "That email doesn’t look valid.",
                "WEAK_PASSWORD : Password should be at least 6 characters":
                    "Password is too weak. Use at least 8 characters with letters and numbers.",
                "OPERATION_NOT_ALLOWED": "Email/password sign-ups are disabled in Firebase.",
                "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts right now. Please wait a minute and try again.",
                "MISSING_PASSWORD": "Please enter a password.",
                "MISSING_EMAIL": "Please enter an email.",
                "EMAIL_NOT_FOUND": "No account found for that email.",
                "INVALID_PASSWORD": "Incorrect password.",
                "USER_DISABLED": "This account has been disabled by an administrator.",
                "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
            }
            for key, nice in mapping.items():
                if key in code:
                    return nice
            if code:
                return code.replace("_", " ").capitalize()
    return default_msg

def delete_self_account(id_token: str):
    """Delete the currently signed-in account using its idToken."""
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