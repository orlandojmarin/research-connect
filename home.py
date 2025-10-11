#sana (landing + login + signup only, CSS)
# ORLANDO
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py
from utils.auth_utils import auth, friendly_firebase_error
import streamlit as st
from utils.auth_utils import (
    auth, db, sanitize_email, is_allowed_sc_su_email,
    strong_password, friendly_firebase_error, delete_self_account
)
from utils.home_utils import get_quick_actions, get_feature_descriptions, initialize_session_state

import os, time
from streamlit import components
from datetime import datetime
from requests.exceptions import HTTPError


def go(page: str):
    st.session_state.page = page

# --------- pages (landing/login/signup) ----------
def render_landing():
    st.markdown('<div id="landing">', unsafe_allow_html=True)

    c1, c2 = st.columns([2, 6])
    with c1:
        st.image("images/scsu_logo.png", width=250)
    with c2:
        st.write("")

    # keep title simple; CSS will style it
    st.markdown("<h1>ResearchConnect SCSU</h1>", unsafe_allow_html=True)

    left, mid, right = st.columns([2, 3, 2])
    with mid:
        # ⬇⬇ wrap buttons so CSS can hit them 100%
        st.markdown('<div class="rc-primary">', unsafe_allow_html=True)
        if st.button("LOG IN", use_container_width=True, key="landing-login"):
            go("login")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="rc-link">', unsafe_allow_html=True)
        if st.button("CREATE AN ACCOUNT", use_container_width=True, key="landing-signup"):
            go("signup")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

def render_signup():
    st.markdown('<div class="rc-form">', unsafe_allow_html=True)  # (styling wrapper)

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
    with col_b:
        st.markdown('<div class="rc-back">', unsafe_allow_html=True)   # <<< add
        back_clicked = st.button("Back to landing", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True) 

    if create_clicked:
        try:
            email = sanitize_email(email_raw)

            if not is_allowed_sc_su_email(email):
                st.error("Please use your SCSU email (…@southernct.edu).")
                st.stop()

            ok, msg = strong_password(password)
            if not ok:
                st.error(msg); st.stop()
            if password != confirm:
                st.error("Passwords do not match."); st.stop()

            try:
                user = auth.create_user_with_email_and_password(email, password)
                uid = user["localId"]
            except HTTPError as ce:
                body = None
                try:
                    body = ce.response.json()
                except Exception:
                    pass
                code = (body or {}).get("error", {}).get("message", "")
                if "EMAIL_EXISTS" in code:
                    try:
                        signed = auth.sign_in_with_email_and_password(email, password)
                        # optional: delete+recreate handled inside your utils if you want
                        uid = signed["localId"]
                    except Exception:
                        st.error("Couldn’t create that account. Try a different SCSU email or use the original password.")
                        st.stop()
                else:
                    st.error(friendly_firebase_error(ce))
                    st.stop()

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
    st.markdown('</div>', unsafe_allow_html=True)

def render_login():
    st.markdown('<div class="rc-form">', unsafe_allow_html=True)  # (styling wrapper)

    st.title("Log in")
    email_raw = st.text_input("SCSU email address", key="login_email")
    password  = st.text_input("Password", type="password", key="login_pw")

    col_a, col_b = st.columns(2)
    login_clicked = col_a.button("Continue", use_container_width=True)
    with col_b:
        st.markdown('<div class="rc-back">', unsafe_allow_html=True)   # <<< add
        back_clicked  = st.button("Back to landing", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)                  # <<< add

    if login_clicked:
        email = sanitize_email(email_raw)
        if not is_allowed_sc_su_email(email):
            st.error("Please use your SCSU email (…@southernct.edu).")
            st.stop()

        try:
            user = auth.sign_in_with_email_and_password(email, password)
            info = auth.get_account_info(user["idToken"])
            uid = info["users"][0]["localId"]

            # put basics in session
            st.session_state.user = {
                "uid": uid,
                "email": email,
                "idToken": user["idToken"],
            }

            # fetch role from DB and add to session (defaults to "student")
            profile = db.child("users").child(uid).get().val() or {}
            st.session_state.user["role"] = profile.get("role", "student")

            st.session_state.page = "home"
            st.rerun()  # single rerun so auth gate passes and home renders
            return
        except Exception as e:
            st.error(friendly_firebase_error(e))
            st.caption(str(e))

    if back_clicked:
        st.session_state.page = "landing"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.set_page_config(page_title="ResearchConnect SCSU", page_icon="🔐", layout="centered")
st.markdown(
    """
    <style>
      :root{
        --rc-blue:#003DA5;
        --rc-gold:#FFC72C;
        --rc-input:#E6E6E6;
      }

      /* Landing title */
      #landing h1{
        text-align:center; color:var(--rc-blue)!important;
        font-size:60px!important; font-weight:800; margin:1.25rem 0 2.5rem;
      }

      /* Landing buttons */
      #landing .stButton > button{
        background:var(--rc-gold)!important; color:var(--rc-blue)!important;
        font-weight:800; font-size:24px; height:96px; border:0; border-radius:10px;
        box-shadow:none;
      }
      #landing .stButton + .stButton > button{
        background:transparent!important; color:var(--rc-blue)!important;
        text-decoration:underline; height:auto; font-size:18px; font-weight:700;
        padding:0; border:0; box-shadow:none; margin-top:1rem;
      }

      /* Forms (login & signup) */
      .rc-form h1{
        color:var(--rc-blue)!important; font-weight:800; text-align:center;
        margin:0.5rem 0 2rem; font-size:42px!important;
      }
      .rc-form label{ color:var(--rc-blue)!important; font-weight:600; }

      /* DESIGN CHANGE: target Streamlit's nested input element */
      .rc-form .stTextInput > div > div > input{
        background:var(--rc-input)!important; border:0!important; height:56px; border-radius:10px;
      }
      /* DESIGN CHANGE: ensure password inputs match the same style */
      .rc-form .stPassword > div > div > input{
        background:var(--rc-input)!important; border:0!important; height:56px; border-radius:10px;
      }

      /* Primary then link-style buttons inside form */
      .rc-form .stButton > button{
        background:var(--rc-gold)!important; color:var(--rc-blue)!important;
        font-weight:800; font-size:20px; height:64px; border:0; border-radius:10px;
      }
      .rc-form .stButton:nth-of-type(2) > button{
        background:transparent!important; color:var(--rc-blue)!important;
        text-decoration:underline; height:auto; font-size:16px; font-weight:700;
        padding:0; box-shadow:none; border:0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# === END OF BLOCK ===

# --------- AUTH GATE ---------
# Ensure keys exist
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "landing"  # landing | login | signup

# If NOT logged in → hide sidebar + render auth screens and STOP
if st.session_state.user is None:
    st.markdown("""
        <style>
            /* Hide the entire sidebar */
            [data-testid="stSidebar"],
            section[data-testid="stSidebar"] { display: none !important; }
            /* Hide multi-page nav (older/newer selectors) */
            nav[data-testid="stSidebarNav"] { display: none !important; }
            /* Hide the little header chevron */
            button[kind="header"] { visibility: hidden; }
            /* Slightly widen content since sidebar is gone */
            .block-container { padding-left: 2rem; padding-right: 2rem; }
        </style>
    """, unsafe_allow_html=True)

    page = st.session_state.page
    if page == "landing":
        render_landing()
    elif page == "signup":
        render_signup()
    elif page == "login":
        render_login()
    st.stop()

# Logged in → show home; add logout
with st.sidebar:
    st.success(f"Logged in as {st.session_state.user['email']}")
    if st.button("Log Out"):
        st.session_state.user = None
        st.session_state.page = "landing"
        st.rerun()
# --------- END AUTH GATE ---------


# (-------------------------------------------------------------------------------------------)
def main():
    """Main function to render the home page"""
    # Configure page and initialize session
    configure_page()
    initialize_session_state()
    st.logo("images/scsu_logo.jpg", size="large")
    
    # Render page components
    render_header()
    render_quick_actions()
    st.divider()
    render_features()
    render_footer()

def configure_page():
    """Configure page settings and metadata"""
    st.set_page_config(
        page_title="ResearchConnect SCSU",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_header():
    """Render main header and welcome section"""
    st.title("Welcome to ResearchConnect 🦉")
    st.subheader("Your gateway to research opportunities and academic resources at SCSU")
    
    # Display logo and welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/logo.png", width=300)
    
    st.success("**Hello! I'm ResearchAI, your friendly AI assistant.** I'm here to help you discover research opportunities, connect with faculty, and navigate SCSU's academic resources!")
    st.divider()

def render_quick_actions():
    """Render quick action buttons"""
    st.subheader("🚀 Quick Actions")
    actions = get_quick_actions()
    
    cols = st.columns(len(actions))
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(
                action["text"], 
                type=action["type"], 
                use_container_width=True, 
                help=action["help"]
            ):
                st.switch_page(action["page"])

def render_features():
    """Render platform features section"""
    st.subheader("🌟 Platform Features")
    features = get_feature_descriptions()
    
    # Chatbot feature
    with st.container(border=True):
        st.subheader(features["chatbot"]["title"])
        st.write(f"**{features['chatbot']['subtitle']}**")
        
        col1, col2 = st.columns(2)
        benefits = features["chatbot"]["benefits"]
        mid_point = len(benefits) // 2
        
        with col1:
            for benefit in benefits[:mid_point]:
                st.write(f"✅ {benefit}")
        with col2:
            for benefit in benefits[mid_point:]:
                st.write(f"✅ {benefit}")
    
    # Research Listings feature
    with st.container(border=True):
        st.subheader(features["listings"]["title"])
        st.write(f"**{features['listings']['subtitle']}**")
        
        col1, col2 = st.columns(2)
        benefits = features["listings"]["benefits"]
        mid_point = len(benefits) // 2
        
        with col1:
            for benefit in benefits[:mid_point]:
                st.write(f"🔍 {benefit}")
        with col2:
            for benefit in benefits[mid_point:]:
                st.write(f"🔍 {benefit}")
    
    # Resources feature
    with st.container(border=True):
        st.subheader(features["resources"]["title"])
        st.write(f"**{features['resources']['subtitle']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**🔬 Academic Support:**")
            for item in features["resources"]["academic_support"]:
                st.write(f"• {item}")
        with col2:
            st.write("**💼 Career Services:**")
            for item in features["resources"]["career_services"]:
                st.write(f"• {item}")

def render_footer():
    """Render footer information"""
    st.divider()
    st.info("**ResearchConnect SCSU** | Connecting Students with Research Opportunities")
    st.caption("Developed by Tatiana Eng, Orlando Marin, and Sana Muneer | CSC 400 Capstone Project")

if __name__ == "__main__":
        main()