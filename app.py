# app.py
import os
import re
import time
import json
import unicodedata
from datetime import datetime

import streamlit as st
import pyrebase
from requests.exceptions import HTTPError
import requests

# ============================ SETTINGS ============================
ALLOWED_DOMAINS = {"southernct.edu", "owls.southernct.edu"}

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


def go(page: str):
    st.session_state.page = page



def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    if "user" not in st.session_state:
        st.session_state.user = None

# ============================ PAGES ============================
def render_landing():
    st.markdown('<div id="landing">', unsafe_allow_html=True)

    # top row: bigger logo on the left
    c1, c2 = st.columns([2, 6])
    with c1:
        st.image("images/scsu_logo.png", width=250)  # ↑ was 56; now clearly visible
    with c2:
        st.write("")  # spacer

    # centered title
    st.markdown(
        "<h1 style='text-align:center; color:#0B4DBB; font-size:52px; margin:0.5rem 0 1.5rem;'>ResearchConnect SCSU</h1>",
        unsafe_allow_html=True,
    )

    # centered buttons (yellow LOGIN, underlined CREATE)
    left, mid, right = st.columns([2, 3, 2])
    with mid:
        if st.button("LOG IN", use_container_width=True):
            go("login")
        if st.button("CREATE AN ACCOUNT", use_container_width=True, key="create-account"):
            go("signup")

    st.markdown("</div>", unsafe_allow_html=True)


def render_signup():
    st.title("Create Account")

    c1, c2 = st.columns(2)
    with c1:
        first = st.text_input("First name")
        email_raw = st.text_input("SCSU email address")
    with c2:
        last = st.text_input("Last name")
        password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm password", type="password")

    col_a, col_b = st.columns(2)
    create_clicked = col_a.button("Continue", use_container_width=True)
    back_clicked = col_b.button("Back to landing", use_container_width=True)

    if create_clicked:
        try:
            email = sanitize_email(email_raw)

            # Email / domain checks
            if not is_allowed_sc_su_email(email):
                st.error("Please use your SCSU email (…@southernct.edu).")
                st.stop()

            # Password checks
            ok, msg = strong_password(password)
            if not ok:
                st.error(msg); st.stop()
            if password != confirm:
                st.error("Passwords do not match."); st.stop()

            # Try to create user
            try:
                user = auth.create_user_with_email_and_password(email, password)
                uid = user["localId"]
            except HTTPError as ce:
                # If email exists, optionally recreate if password matches
                body = None
                try:
                    body = ce.response.json()
                except Exception:
                    pass
                code = (body or {}).get("error", {}).get("message", "")
                if "EMAIL_EXISTS" in code:
                    # Try to sign in with the provided password
                    try:
                        signed = auth.sign_in_with_email_and_password(email, password)
                        if ALLOW_RECREATE_SAME_EMAIL:
                            # delete and recreate fresh
                            delete_self_account(signed["idToken"])
                            time.sleep(0.4)
                            user = auth.create_user_with_email_and_password(email, password)
                            uid = user["localId"]
                        else:
                            # treat as success without surfacing "exists"
                            uid = signed["localId"]
                    except Exception:
                        st.error("Couldn’t create that account. Try a different SCSU email or use the original password.")
                        st.stop()
                else:
                    st.error(friendly_firebase_error(ce))
                    st.stop()

            # Save/refresh minimal profile
            db.child("users").child(uid).set({
                "email": email,
                "name": f"{first} {last}".strip(),
                "role": "student",
                "created_at": datetime.utcnow().isoformat() + "Z",
            })

            st.success("Account is ready. Please log in.")
            time.sleep(0.8)
            go("login")

        except Exception as e:
            st.error(friendly_firebase_error(e))

    if back_clicked:
        go("landing")

def render_login():
    st.title("Log in")
#test
    email_raw = st.text_input("SCSU email address")
    password = st.text_input("Password", type="password")

    col_a, col_b = st.columns(2)
    login_clicked = col_a.button("Continue", use_container_width=True)
    back_clicked  = col_b.button("Back to landing", use_container_width=True)

    if login_clicked:
        email = sanitize_email(email_raw)

        if not is_allowed_sc_su_email(email):
            st.error("Please use your SCSU email (…@southernct.edu).")
            st.stop()

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            info = auth.get_account_info(user["idToken"])

            st.session_state.user = {
                "uid": info["users"][0]["localId"],
                "email": email,
                "idToken": user["idToken"],
            }
            go("post_login")   

        except Exception as e:
            st.error(friendly_firebase_error(e))

    if back_clicked:
        go("landing")      
# ============================ APP ============================
st.set_page_config(page_title="ResearchConnect SCSU", page_icon="🔐", layout="centered")
st.markdown(
    """
    <style>
      .block-container{padding-top:2rem;}

      /* Landing-only styles */
      #landing .stButton>button{
        background:#FDCB3D; color:#0B4DBB; font-weight:700;
        font-size:22px; padding:18px 48px; border:0; border-radius:8px;
      }
      #landing .stButton + .stButton>button{
        background:transparent; color:#0B4DBB; text-decoration:underline;
        box-shadow:none; border:0; padding:6px 0; font-weight:600; font-size:18px;
      }
    </style>
    """,
    unsafe_allow_html=True,
) 
# --- initialize session state ---
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "user" not in st.session_state:
    st.session_state.user = None

page = st.session_state.page
if page == "landing":
    render_landing()
elif page == "signup":
    render_signup()
elif page == "login":
    render_login()
elif page == "post_login":
    render_post_login()
