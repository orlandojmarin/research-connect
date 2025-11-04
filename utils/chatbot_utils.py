# Sana update and renewed to work with RAG and firebase listings
# ORLANDO
# chatbot_utils.py

"""
Chatbot utilities for ResearchConnect SCSU
Handles chatbot functionality, response generation, and conversation management
"""
import datetime
import random
import re
import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
<<<<<<< HEAD

# ==========================================================
# --- RAG + Firebase Imports (with SAFE ADAPTER) ---
# ==========================================================
from utils.rag_utils import answer_question  # local RAG .txt retrieval

try:
    from utils import firebase_query_utils as fq
except Exception:
    fq = None

def _noop(*args, **kwargs):
    """Return empty list or safe fallback if Firebase import fails."""
    return []

# Dynamically map whichever functions exist
search_listings_by_keywords = (
    getattr(fq, "search_listings_by_keywords", None)
    or getattr(fq, "search_listings_by_keyword", None)
    or _noop
)

search_listings_by_faculty = (
    getattr(fq, "search_listings_by_faculty", None)
    or getattr(fq, "get_listings_by_faculty", None)
    or _noop
)

search_paid_listings = getattr(fq, "search_paid_listings", _noop)

format_listings_brief = (
    getattr(fq, "format_listings_brief", None)
    or getattr(fq, "format_listings_as_context", None)
    or (lambda items: "No research listings match your query in the database.")
)

# Optional: Vertex AI Search helpers (not always defined in local RAG)
try:
    from utils.rag_utils import query_vertex_search, format_context, RAGSearchError
except Exception:
    class RAGSearchError(Exception):
        pass
    def query_vertex_search(q, top_k=5):
        return []
    def format_context(items):
        return ""

# ==========================================================
# Load environment variables and initialize Vertex AI
# ==========================================================
load_dotenv()
=======
from google.oauth2 import service_account
>>>>>>> d979b21e897ff213bbbcd976fad2b145ec767d33

@st.cache_resource
def initialize_vertex_ai():
    """
    Initialize Vertex AI. Read from Streamlit secrets first, then .env.
    """
    try:
<<<<<<< HEAD
        project_id = st.secrets.get("GCP_PROJECT_ID") or os.getenv("GCP_PROJECT_ID")
        region = (
            st.secrets.get("VERTEX_REGION")
            or os.getenv("VERTEX_REGION")
            or "us-central1"
        )
        if not project_id:
            print("GCP_PROJECT_ID missing (check .streamlit/secrets.toml or .env)")
            return None

        vertexai.init(project=project_id, location=region)
=======
        # Get project ID from secrets
        project_id = st.secrets["GCP_PROJECT_ID"]
        
        # Initialize credentials from secrets
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        
        # Initialize Vertex AI with credentials
        vertexai.init(
            project=project_id, 
            location="us-central1",
            credentials=credentials
        )
        
>>>>>>> d979b21e897ff213bbbcd976fad2b145ec767d33
        model = GenerativeModel("gemini-2.5-flash")
        print(f"Vertex AI initialized (project={project_id}, region={region})")
        return model
    except Exception as e:
        print(f"Failed to initialize Vertex AI: {e}")
        return None


# ==========================================================
# Chat Session & Utilities
# ==========================================================
def initialize_chat_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []

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

def generate_prompt_summary(prompt_text):
    """Generate short summaries for long user prompts."""
    model = initialize_vertex_ai()
    if not model:
        words = prompt_text.split()[:7]
        return " ".join(words) + "..."
    try:
        summary_prompt = f"""Generate a concise 5-7 word summary of the user's request.
Only return the summary, nothing else.

Text: {prompt_text}

Summary:"""
        response = model.generate_content(summary_prompt)
        summary = response.text.strip()
        if len(summary.split()) > 10:
            return " ".join(prompt_text.split()[:7]) + "..."
        return summary
    except Exception:
        return " ".join(prompt_text.split()[:7]) + "..."

def add_user_message(content):
    msg = {"role": "user", "content": content, "timestamp": datetime.datetime.now()}
    if len(content) > 200:
        msg["summary"] = generate_prompt_summary(content)
    st.session_state.messages.append(msg)

def add_assistant_message(content):
    st.session_state.messages.append(
        {"role": "assistant", "content": content, "timestamp": datetime.datetime.now()}
    )

# ==========================================================
# Context Builders
# ==========================================================
RESEARCH_KWS = {
    "research", "opportunity", "opportunities", "listing", "listings",
    "position", "opening", "paid", "unpaid", "hours", "machine learning",
    "ai", "data"
}
FACULTY_KWS = {"professor", "faculty", "dr.", "dr ", "advisor", "pi"}

def _classify_question(q: str) -> str:
    ql = (q or "").lower()
    if any(k in ql for k in FACULTY_KWS):
        return "faculty"
    if any(k in ql for k in RESEARCH_KWS):
        return "listings"
    return "general"
#-----------------helper function-----------------------------


#---------------------------------------------------------
def _build_context(q: str) -> str:
    """
    Retrieve relevant context from Firebase or local RAG.
    Returns a conversationally formatted summary.
    """
    qtype = _classify_question(q or "")
    ql = (q or "").lower()

    # --- RESEARCH LISTINGS ---
    if qtype == "listings":
        if "paid" in ql and "unpaid" not in ql:
            listings = search_paid_listings(True)
            heading = "Yes! Here are some paid research opportunities currently available:"
        elif "unpaid" in ql and "paid" not in ql:
            listings = search_paid_listings(False)
            heading = "Here are some unpaid research opportunities you might find interesting:"
        else:
            listings = search_listings_by_keywords(q)
            heading = "Here are some research projects that match what you're asking about:"
    # --- FACULTY ---
    if qtype == "faculty":
        listings = search_listings_by_faculty(q)
        if not listings:
            return "I couldn’t find specific faculty-led research listings for that professor right now."
        intro = "Here’s what I found from the faculty research database:"
        text = format_listings_brief(listings)
        return f"{intro}\n\n{text}\n\nYou can email the professor directly or visit during office hours for more details."

    # --- GENERAL INFO / WEBSITE CONTENT ---
    try:
        snippet = answer_question(q)
        if not snippet:
            return ""
        # Make it sound friendly if it’s a general info query
        if any(word in ql for word in ["ihub", "website", "center", "office", "department", "email", "contact", "phone"]):
            return (
                f"Here’s what I found about that:\n\n{snippet}\n\n"
                "If you’d like, I can give just the contact info or the main description — which would you prefer?"
            )
        return snippet
    except Exception:
        return ""



# ==========================================================
# Chatbot Response (Hybrid Logic)
# ==========================================================
def generate_chatbot_response(user_input):
    """
    Generate conversational chatbot responses with context-based logic.
    """
    model = initialize_vertex_ai()
    if not model:
        return "Vertex AI is not initialized."

    try:
        # Decide context (faculty, listings, or general)
        context_block = _build_context(user_input)
        if not context_block:
            context_block = "[No specific context found; respond naturally.]"

        # Construct prompt with conversational style
        system_prompt = """You are ResearchAI, an AI assistant for Southern Connecticut State University (SCSU).
Your tone should be friendly, conversational, and student-focused.
When showing research listings, speak like you're chatting — not listing data mechanically.
Example:
'Yes! I found a few research projects you might like. One is led by Dr. Tatiana Eng in the Computer Science department...'

When explaining website or office info (like iHub), summarize clearly but sound helpful, not robotic.
Keep responses under 180 words unless asked for more detail."""

        # Include last few messages for flow
        history = st.session_state.messages[-6:]
        history_text = "".join(
            f"{'Student' if m['role']=='user' else 'ResearchAI'}: {m['content']}\n"
            for m in history
        )
        history_text += f"Student: {user_input}\nResearchAI:"

        prompt = (
            f"{system_prompt}\n\nCONTEXT:\n{context_block}\n\n"
            f"Conversation so far:\n{history_text}"
        )

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"[Gemini ERROR] {e}")
        return "Hmm, something went wrong while generating your answer. Try rephrasing or asking again."

# ==========================================================
# Conversation Logging
# ==========================================================
def log_conversation(user_input, bot_response):
    log_entry = {
        "timestamp": datetime.datetime.now(),
        "user_input": user_input,
        "bot_response": bot_response,
        "session_id": st.session_state.get("session_id", "unknown"),
    }
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []
    st.session_state.conversation_log.append(log_entry)
