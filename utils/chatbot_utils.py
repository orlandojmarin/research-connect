
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
from google.oauth2 import service_account
import json

# ==========================================================
# --- RAG + Firebase Imports ---
# ==========================================================

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
format_listings_brief = getattr(fq, "format_listings_brief", None) or (
    lambda items: "No research listings match your query in the database."
)
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
    except Exception:
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
        region = get_config("VERTEX_REGION") or "us-central1"

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
        vertexai.init(project=project_id, location=region, credentials=credentials)

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
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 Hi! I’m **ResearchConnect**, your AI assistant for SCSU research. "
                    "I can help you explore research opportunities, faculty projects, and "
                    "campus resources. What would you like to know?"
                ),
                "timestamp": datetime.datetime.now(),
            }
        ]


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
    st.session_state.messages.append(
        {
            "role": "user",
            "content": content,
            "timestamp": datetime.datetime.now(),
        }
    )


def add_assistant_message(content):
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": content,
            "timestamp": datetime.datetime.now(),
        }
    )


# ==========================================================
# CLASSIFY QUERY
# ==========================================================
RESEARCH_KWS = {
    "research",
    "opportunity",
    "opportunities",
    "listing",
    "listings",
    "position",
    "opening",
    "paid",
    "unpaid",
    "hours",
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
            lines.append(f"Email: {c.get('email', 'N/A')}")
            lines.append(f"Website: {c.get('website', 'N/A')}")

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
        "currently available",
        "list all",
        "display all",
        "show me all",
        "show me all the research",
        "show me all the research opportunities",
        "show me all research opportunities",
        "all the research",
        "all the research opportunities",
    ]

    if any(p in ql for p in show_all_patterns):
        listings = get_all_listings_raw()
        if not listings:
            return "There are no research listings available right now."

        return (
            "Here are ALL available research opportunities:\n\n"
            + format_listings_brief(listings)
        )

    # =========================================
    # CLASSIFY QUERY TYPE
    # =========================================
    qtype = _classify_question(q)

    # =========================================
    # RESEARCH LISTINGS
    # =========================================
    if qtype == "listings":
        show_all = "show all" in ql or ql.strip() in {
            "all listings",
            "all research",
            "all research listings",
        }

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
        # 1. Try normal faculty search (name or department)
        listings = search_listings_by_faculty(q, max_results=None)

        # 2. If no matches → return ALL faculty who have listings
        if not listings:
            all_listings = get_all_listings_raw()
            if not all_listings:
                return "There are no research listings available right now."

            # Deduplicate by professor
            faculty_map = {}
            for item in all_listings:
                pi = item.get("pi", "").strip()
                if pi:
                    faculty_map.setdefault(pi, []).append(item)

            if not faculty_map:
                return (
                    "I checked the research listings but couldn't find faculty-led projects right now."
                )

            # Build response with all faculty who currently have research listings
            response = ["Here are faculty members who currently have research listings:\n"]
            for pi, items in faculty_map.items():
                for it in items:
                    response.append("- " + format_listings_brief([it]))

            return "\n".join(response)

        # 3. If normal search matched
        return "Here are the faculty-led research projects I found:\n\n" + format_listings_brief(listings)
        


# ==========================================================
# GEMINI — STRICT ANTI-HALLUCINATION MODE
# ==========================================================
def generate_chatbot_response(user_input):
    model = initialize_vertex_ai()
    if not model:
        return (
            "I'm having trouble connecting to my AI system right now. "
            "Please try again in a moment, or contact support if this issue persists."
        )

    cleaned = user_input.lower().strip()

    # Empty / whitespace input
    if not cleaned:
        return (
            "I’m here to help you explore **SCSU research opportunities, faculty projects, "
            "and campus resources**. What would you like to search for?"
        )

    # ============================================
    # 1. FRIENDLY GREETING & SMALL TALK
    # ============================================
    # Normalize simple punctuation for matching
    normalized = cleaned.replace("?", "").replace("!", "").strip()

    # Greetings like "hi", "hi!", "hey there", etc.
    greeting_words = {"hi", "hello", "hey", "hey there", "hi there", "yo"}
    if normalized in greeting_words or normalized.startswith("hi ") or normalized.startswith(
        "hello "
    ):
        return (
            "Hi! 😊 I’m glad you’re here. I’m doing well and ready to help you find "
            "research opportunities, faculty projects, or campus resources at SCSU. "
            "What would you like to explore?"
        )

    # Variations of "how are you"
    if "how are you" in cleaned or "how r u" in cleaned or "how are u" in cleaned:
        return (
            "I’m doing great, thanks for asking! 😊 "
            "I’m here to support you with **research listings, faculty, and campus resources** "
            "at SCSU. What are you curious about today?"
        )

    # ============================================
    # 2. SAFE SCSU BASIC INFORMATION (STATIC)
    # ============================================
    # Questions about SCSU
    if "scsu" in cleaned and (
        "stand for" in cleaned
        or "meaning" in cleaned
        or "what is" in cleaned
        or "tell me about" in cleaned
        or "who are you" in cleaned
        or "what does" in cleaned
    ):
        return (
            "SCSU stands for **Southern Connecticut State University**, located in New Haven, CT. 💙 "
            "I’m focused on helping you find research opportunities and resources connected to SCSU."
        )

    if cleaned == "what is scsu" or cleaned == "scsu":
        return (
            "SCSU is **Southern Connecticut State University**, a public university in New Haven, CT. "
            "I can help you explore research opportunities and campus resources connected to SCSU."
        )

    # Questions about ResearchConnect / the app
    if (
        "researchconnect" in cleaned
        or "research connect" in cleaned
        or ("this app" in cleaned and "what" in cleaned)
        or ("what is" in cleaned and "app" in cleaned)
        or "who are you" in cleaned
        or "tell me about yourself" in cleaned
        or "what can you do" in cleaned
        or "your role" in cleaned
        or "who am i talking to" in cleaned
        or "are you a chatbot" in cleaned
    ):
        return (
            "ResearchConnect is the app you’re using right now 😊.\n\n"
            "It helps SCSU students:\n"
            "- 🔍 Find current **research listings** and opportunities\n"
            "- 👨‍🏫 See **faculty projects** they can join\n"
            "- 📚 Discover **campus resources** like the Innovation Hub or career services\n\n"
            "You can ask things like:\n"
            "- *“Show me all research opportunities”*\n"
            "- *“Which listings are paid?”*\n"
            "- *“Tell me about the Innovation Hub”*"
        )

    # Very vague “tell me more about it”
    if "tell me more about it" in cleaned or "tell me more" in cleaned:
        return (
            "I’m not always sure what “it” refers to, but I can definitely help you learn more about "
            "**research opportunities, faculty, and campus resources** at SCSU.\n\n"
            "For example, you can ask:\n"
            "- “Tell me more about the Innovation Hub”\n"
            "- “Tell me more about Dr. Smith’s research listing”\n"
            "- “Tell me more about paid research opportunities”"
        )

    # ============================================
    # 3. FRIENDLY OFF-TOPIC REDIRECT
    # ============================================
    off_topic_patterns = [
        "what is your name",
        "who created you",
        "who made you",
        "how old are you",
        "do you have feelings",
        "are you real",
        "tell me a story",
        "tell me joke",
        "joke",
        "favorite food",
        "favorite movie",
        "do you like",
        "are you single",
    ]

    if any(p in cleaned for p in off_topic_patterns):
        return (
            "Great question 😄 but I’m mainly designed to help with **SCSU research listings, "
            "faculty projects, and campus resources**.\n\n"
            "Try asking me things like:\n"
            "- “Show me all research opportunities”\n"
            "- “Which listings are paid?”\n"
            "- “Who are the Computer Science faculty in the listings?”\n"
            "- “Tell me about the Innovation Hub.”"
        )
    # ============================================
    # 4. RECOMMENDATION SYSTEM (SAFE + FRIENDLY)
    # ============================================

    # Expanded patterns to catch more natural questions
    recommend_patterns = [
        "recommend", "suggest", "advice", "advise",
        "guide", "guide me",
        "help me start",
        "what do you suggest",
        "which resource", 
    ]

    # --- Check using substring detection ---
    if any(p in cleaned for p in recommend_patterns):

        # -------------------------------------------
        # A. CS Student Resource Recommendation
        # -------------------------------------------
        if (
            "computer science" in cleaned
            or "cs student" in cleaned
            or "tech" in cleaned
            or "programming" in cleaned
            or "resources" in cleaned
            or "engineering" in cleaned
        ):
            return (
                "If you're a Computer Science student, here are strong places to start:\n\n"
                "🌟 **Innovation Hub** – career help, resume review, tech events, networking.\n"
                "📘 **STEM Center** – tutoring, study support, faculty connections.\n"
                "👨‍🏫 **CS Faculty Listings** – see which faculty are mentoring research.\n\n"
                "You can ask me any questions related to research opportunities like:\n"
                "- “Show me all research listings”\n"
                "- “Paid research opportunities”\n"
            )

        # -------------------------------------------
        # B. Recommend Professors FROM LISTINGS ONLY
        # -------------------------------------------
        if "professor" in cleaned or "faculty" in cleaned or "contact" in cleaned:
            faculty_listings = search_listings_by_faculty("", max_results=None)

            if faculty_listings:
                return (
                    "Here are faculty members who are currently running research:\n\n"
                    f"{format_listings_brief(faculty_listings)}\n"
                    "\nIf you want, I can filter by paid, unpaid, or upcoming projects!"
                )
            else:
                return (
                    "I checked the research listings and didn't find any active faculty-led projects.\n\n"
                    "You can still visit the **Innovation Hub** or **STEM Center** to get help "
                    "connecting with professors about future opportunities."
                )

        # -------------------------------------------
        # C. General Research Recommendation
        # -------------------------------------------
        return (
            "Here’s what I recommend if you're trying to get started with research:\n\n"
            "1️⃣ Browse **current research listings** to see open projects.\n"
            "2️⃣ Check **faculty-led projects** to see who is mentoring students.\n"
            "3️⃣ Explore the **Innovation Hub** for resume help, mentoring, and research support.\n\n"
            "Try asking me:\n"
            "- “Show me all research opportunities”\n"
            "- “Which resources help students find research?”\n"
            "- “Which listings are paid?”"
        )
    # ============================================
    # 4. RAG / LISTINGS / RESOURCES CONTEXT
    # ============================================
    context_block = (_build_context(user_input) or "")

    # If context is empty → DO NOT LET GEMINI INVENT ANYTHING
    if not context_block.strip():
        return (
            "I checked the research listings and the available information files, "
            "but I couldn’t find anything related to that question. 😊\n\n"
            "I can help best if you ask about **SCSU research opportunities, faculty, "
            "or campus resources**."
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
        f"{'Student' if m['role'] == 'user' else 'ResearchAI'}: {m['content']}\n"
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
