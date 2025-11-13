# Sana
# ORLANDO
# chatbot_utils.py

"""
Chatbot utilities for ResearchConnect SCSU
Handles chatbot functionality, response generation, and conversation management
Updated to support environment variables for Cloud Run deployment
"""

import os
from dotenv import load_dotenv
import datetime
import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import os
import json

# ==========================================================
# --- RAG + Firebase Imports ---
# ==========================================================
from utils.rag_utils import answer_question  # local RAG .txt retrieval

try:
    from utils import firebase_query_utils as fq
    from utils.firebase_query_utils import filter_and_group_by_start_date
except Exception:
    fq = None

from utils.resources_utils import search_resources   # resource lookup

def _noop(*args, **kwargs):
    return []

# Map Firebase functions safely
search_listings_by_keywords = getattr(fq, "search_listings_by_keywords", None) or _noop
search_listings_by_faculty = getattr(fq, "search_listings_by_faculty", None) or _noop
search_paid_listings = getattr(fq, "search_paid_listings", _noop)
format_listings_brief = getattr(fq, "format_listings_brief", None) or (lambda items: "No research listings match your query in the database.")
get_all_listings_raw = getattr(fq, "get_all_listings_raw", _noop)

# ==========================================================
# Load Config (local secrets or Cloud Run env)
# ==========================================================
def get_config(key, default=None):
    """
    Get config from environment variables (Cloud Run) or st.secrets (local).
    """
    env_value = os.environ.get(key)
    if env_value:
        return env_value
    
    try:
        return st.secrets[key]
    except:
        return default

load_dotenv()

@st.cache_resource
def initialize_vertex_ai():
    try:
        # ---------------------------------------------------
        # Get project ID from environment or secrets
        # (Works for BOTH local and Cloud Run)
        # ---------------------------------------------------
        project_id = get_config("GCP_PROJECT_ID")

        if not project_id:
            print("Error: GCP_PROJECT_ID not found in environment variables or secrets")
            return None

        # ---------------------------------------------------
        # Determine region (local → st.secrets, Cloud Run → env)
        # ---------------------------------------------------
        region = (
            get_config("VERTEX_REGION")
            or "us-central1"
        )

        # ---------------------------------------------------
        # Load service account credentials
        # Cloud Run → env var GCP_SERVICE_ACCOUNT_JSON
        # Local → st.secrets["gcp_service_account"]
        # ---------------------------------------------------
        service_account_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")

        if service_account_json:
            # Cloud Run service account as JSON string
            service_account_dict = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                service_account_dict
            )
        else:
            # Local machine
            try:
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"]
                )
            except Exception as e:
                print(f"Warning: Could not load service account from secrets: {e}")
                credentials = None  # Let VertexAI try default credentials

        # ---------------------------------------------------
        # Initialize Vertex AI
        # ---------------------------------------------------
        vertexai.init(
            project=project_id,
            location=region,
            credentials=credentials
        )

        model = GenerativeModel("gemini-2.5-flash")
        print("Vertex AI initialized successfully")
        return model

    except Exception as e:
        print(f"Failed to initialize Vertex AI: {e}")
        return None

    

# ==========================================================
# Chat Session
# ==========================================================
def initialize_chat_session():
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": (
                "👋 Welcome! I’m **ResearchConnect**, your AI assistant for SCSU research. "
                "Ask me about research listings, professors, departments, or campus resources!"
            ),
            "timestamp": datetime.datetime.now(),
        }]

def get_sidebar_info():
    return {
        "assistant_description": {
            "title": "🧠 ResearchAI Assistant",
            "help_topics": [
                "🔍 Finding research opportunities",
                "👨‍🏫 Information about faculty",
                "📚 Campus resources and offices",
                "💼 Internship and fellowship programs",
                "📝 Application processes",
                "❓ General research questions",
            ],
        },
    }

def clear_conversation():
    st.session_state.messages = []
    initialize_chat_session()

def add_user_message(content):
    st.session_state.messages.append({
        "role": "user",
        "content": content,
        "timestamp": datetime.datetime.now(),
    })

def add_assistant_message(content):
    st.session_state.messages.append({
        "role": "assistant",
        "content": content,
        "timestamp": datetime.datetime.now(),
    })

# ==========================================================
# CLASSIFY QUERY
# ==========================================================
RESEARCH_KWS = {
    "research", "opportunity", "opportunities", "listing", "listings",
    "position", "opening", "paid", "unpaid", "hours"
}
FACULTY_KWS = {"professor", "faculty", "dr.", "dr ", "advisor", "pi"}

def _classify_question(q: str) -> str:
    ql = q.lower()
    if any(k in ql for k in FACULTY_KWS):
        return "faculty"
    if any(k in ql for k in RESEARCH_KWS):
        return "listings"
    return "general"

# ==========================================================
# BUILD CONTEXT (NO HALLUCINATION LOGIC HERE)
# ==========================================================
def _build_context(q: str) -> str:
    ql = q.lower()

    # =========================================
    # CAMPUS RESOURCES (Innovation Hub, JOBSs, OCPD, STEM)
    # =========================================
    name, data = search_resources(q)
    if data:
        lines = [f"{name.upper()} INFORMATION:\n"]

        if "description" in data:
            lines.append(data["description"].strip())

        # Services (Innovation Hub, OCPD, STEM)
        if "services" in data:
            lines.append("\nServices:")
            for s in data["services"]:
                lines.append(f"- {s}")

        if "career_services" in data:
            lines.append("\nCareer Services:")
            for s in data["career_services"]:
                lines.append(f"- {s}")

        # Contact information
        if "email" in data:
            lines.append(f"\nEmail: {data['email']}")
        if "website" in data:
            lines.append(f"Website: {data['website']}")

        if "contact" in data:
            c = data["contact"]
            lines.append("\nContact:")
            lines.append(f"Email: {c.get('email','N/A')}")
            lines.append(f"Website: {c.get('website','N/A')}")

        return "\n".join(lines)

    # =========================================
    # "SHOW ALL" OVERRIDE FOR LISTINGS
    # =========================================
    show_all_patterns = [
        "show all",
        "all research",
        "all opportunities",
        "all listings",
        "everything",
        "list all",
        "display all",
        "show me all",
        "show me all the research",
        "show me all the research opportunities",
        "show me all research opportunities",
        "all the research",
        "all the research opportunities"
    ]

    if any(p in ql for p in show_all_patterns):
        listings = get_all_listings_raw()
        if not listings:
            return "There are no research listings available right now."

        upcoming, expired = filter_and_group_by_start_date(listings)

        text = []

        if upcoming:
            text.append("📅 **Upcoming Research Opportunities**:\n")
            text.append(format_listings_brief(upcoming))
            text.append("")

        if expired:
            text.append("⏳ **Already Started / Past Opportunities**:\n")
            text.append(format_listings_brief(expired))

        return "\n".join(text).strip()

    # =========================================
    # CLASSIFY QUERY TYPE
    # =========================================
    qtype = _classify_question(q)

    # =========================================
    # RESEARCH LISTINGS
    # =========================================
    if qtype == "listings":
        show_all = (
            "show all" in ql
            or ql.strip() in {"all listings", "all research", "all research listings"}
        )

        if show_all:
            listings = get_all_listings_raw()
            heading = "Here are all current research opportunities:"
        elif "paid" in ql and "unpaid" not in ql:
            listings = search_paid_listings(True, max_results=None)
            heading = "Here are the paid research opportunities:"
        elif "unpaid" in ql and "paid" not in ql:
            listings = search_paid_listings(False, max_results=None)
            heading = "Here are the unpaid research opportunities:"
        else:
            listings = search_listings_by_keywords(q, max_results=20)
            heading = "Here are some matching research opportunities:"

        if not listings:
            return (
                "I looked through the research listings database but didn’t find "
                "any opportunities matching what you asked."
            )

        return f"{heading}\n\n{format_listings_brief(listings)}"

    # =========================================
    # FACULTY FROM LISTINGS ONLY
    # =========================================
    if qtype == "faculty":
        listings = search_listings_by_faculty(q, max_results=None)
        if not listings:
            return (
                "I checked the research listings but couldn’t find active projects "
                "for that professor or faculty group."
            )
        return (
            "Here are the faculty-led research projects I found:\n\n"
            + format_listings_brief(listings)
        )

    # =========================================
    # GENERAL / RAG (.txt)
    # =========================================
    snippet = answer_question(q)
    return snippet if snippet else ""

# ==========================================================
# GEMINI — STRICT ANTI-HALLUCINATION MODE
# ==========================================================
def generate_chatbot_response(user_input):
    model = initialize_vertex_ai()
    if not model:
        return "I'm having trouble connecting to my AI system right now. Please try again in a moment, or contact support if this issue persists."

    context_block = _build_context(user_input)

    # If context is empty → DO NOT LET GEMINI INVENT ANYTHING
    if not context_block.strip():
        return (
            "I checked the research listings and the available information files, "
            "but I couldn't find anything related to your question. "
            "I can only answer based on those sources."
        )

    # If context already says “no data” → return it directly
    lower_ctx = context_block.lower()
    if (
        "didn’t find" in lower_ctx
        or "didn't find" in lower_ctx
        or "no research listings" in lower_ctx
        or "couldn’t find" in lower_ctx
    ):
        return context_block

    # Build conversation history
    history = st.session_state.messages[-6:]
    history_text = "".join(
        f"{'Student' if m['role']=='user' else 'ResearchAI'}: {m['content']}\n"
        for m in history
    )
    history_text += f"Student: {user_input}\nResearchAI:"

    # Zero-hallucination system prompt
    system_prompt = """
You are ResearchAI, an assistant for Southern Connecticut State University (SCSU).

STRICT RULES:
1. You MUST ONLY use the information provided in the CONTEXT section.
2. You CANNOT add or guess information, even if you believe it is correct.
3. You CANNOT invent new offices, programs, or departments.
4. You may rephrase or summarize what is in the context.
"""

    prompt = f"""{system_prompt}

CONTEXT (the ONLY facts you may use):
{context_block}

Conversation so far:
{history_text}
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return "Something went wrong while generating your answer."

# ==========================================================
# Logging
# ==========================================================
def log_conversation(user_input, bot_response):
    entry = {
        "timestamp": datetime.datetime.now(),
        "user_input": user_input,
        "bot_response": bot_response,
    }
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []
    st.session_state.conversation_log.append(entry)
