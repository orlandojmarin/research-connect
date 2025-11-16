# chatbot_utils.py
# ORLANDO with Firebase integration from SANA

"""
Chatbot utilities for ResearchConnect SCSU
Handles chatbot functionality, response generation, and conversation management
Combines Orlando's conversation handling with Sana's Firebase listing integration
"""

import datetime
import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import os
import json

# ==========================================================
# Firebase Imports (from Sana)
# ==========================================================
try:
    from utils import firebase_query_utils as fq
except Exception:
    fq = None

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
# Configuration
# ==========================================================

def get_config(key, default=None):
    """
    Get config from environment variables (Cloud Run) or st.secrets (local).
    
    Args:
        key: Configuration key to retrieve
        default: Default value if key not found
    
    Returns:
        Configuration value or default
    """
    env_value = os.environ.get(key)
    if env_value:
        return env_value
    
    try:
        return st.secrets[key]
    except:
        return default

@st.cache_resource
def initialize_vertex_ai():
    """
    Initialize Vertex AI connection with caching to avoid repeated initializations
    
    Returns:
        GenerativeModel or None: Initialized model or None if fails
    """
    try:
        project_id = get_config("GCP_PROJECT_ID")
        
        if not project_id:
            print("Error: GCP_PROJECT_ID not found in environment variables or secrets")
            return None
        
        # Try to get service account from environment variable first (Cloud Run)
        service_account_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
        
        if service_account_json:
            service_account_dict = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                service_account_dict
            )
        else:
            try:
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"]
                )
            except Exception as e:
                print(f"Warning: Could not load service account from secrets: {e}")
                credentials = None
        
        vertexai.init(
            project=project_id, 
            location="us-central1",
            credentials=credentials
        )
        
        # Using Gemini 2.5 Flash - best balance of speed, cost, and quality
        model = GenerativeModel("gemini-2.5-flash")
        print("Vertex AI initialized successfully")
        return model
    except Exception as e:
        print(f"Failed to initialize Vertex AI: {e}")
        return None

# ==========================================================
# Chat Session Management
# ==========================================================

def initialize_chat_session():
    """
    Initialize chat session state without an initial welcome message.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_sidebar_info():
    """
    Get sidebar information and statistics
    
    Returns:
        dict: Sidebar content configuration
    """
    sidebar_config = {
        "assistant_description": {
            "title": "ResearchAI Assistant",
            "help_topics": [
                "Finding research opportunities",
                "Information about faculty",
                "Campus resources and offices", 
                "Internship and fellowship programs",
                "Application processes",
                "General research questions"
            ]
        },
    }
    return sidebar_config

def clear_conversation():
    """
    Clear the conversation history
    """
    st.session_state.messages = []
    initialize_chat_session()

def generate_prompt_summary(prompt_text):
    """
    Generate a concise 5-7 word summary of a user prompt using Vertex AI.
    
    Args:
        prompt_text (str): The full user prompt
        
    Returns:
        str: A 5-7 word summary
    """
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
            words = prompt_text.split()[:7]
            return " ".join(words) + "..."
        
        return summary
        
    except Exception as e:
        print(f"Summary generation failed: {e}")
        words = prompt_text.split()[:7]
        return " ".join(words) + "..."

def add_user_message(content):
    """
    Add user message to chat history with optional summary for long prompts
    
    Args:
        content (str): User message content
    """
    message = {
        "role": "user",
        "content": content,
        "timestamp": datetime.datetime.now()
    }
    
    # Generate summary if prompt is long (>200 characters)
    if len(content) > 200:
        message["summary"] = generate_prompt_summary(content)
    
    st.session_state.messages.append(message)

def add_assistant_message(content):
    """
    Add assistant message to chat history
    
    Args:
        content (str): Assistant message content
    """
    message = {
        "role": "assistant", 
        "content": content,
        "timestamp": datetime.datetime.now()
    }
    st.session_state.messages.append(message)

# ==========================================================
# Query Classification (from Sana)
# ==========================================================

RESEARCH_KWS = {
    "research", "opportunity", "opportunities", "listing", "listings",
    "position", "opening", "paid", "unpaid", "hours",
}
FACULTY_KWS = {"professor", "faculty", "dr.", "dr ", "advisor", "pi"}

def _classify_question(q: str) -> str:
    """Classify query type"""
    ql = q.lower()
    if any(k in ql for k in FACULTY_KWS):
        return "faculty"
    if any(k in ql for k in RESEARCH_KWS):
        return "listings"
    return "general"

# ==========================================================
# Context Building - Listings Only (adapted from Sana)
# ==========================================================

def _build_context(q: str) -> str:
    """
    Build context from research listings database.
    Returns formatted listing information or empty string if no matches.
    """
    ql = q.lower()

    # Show all listings patterns
    show_all_patterns = [
        "show all", "all research", "all opportunities", "all listings",
        "everything", "currently available", "list all", "display all",
        "show me all", "available research",
    ]

    if any(p in ql for p in show_all_patterns):
        listings = get_all_listings_raw()
        if not listings:
            return "CONTEXT: No research listings are currently available."
        return "CONTEXT: All available research listings:\n\n" + format_listings_brief(listings)

    # Classify query type
    qtype = _classify_question(q)

    # Research listings search
    if qtype == "listings":
        if "paid" in ql and "unpaid" not in ql:
            listings = search_paid_listings(True, max_results=None)
            heading = "CONTEXT: Paid research opportunities:"
        elif "unpaid" in ql and "paid" not in ql:
            listings = search_paid_listings(False, max_results=None)
            heading = "CONTEXT: Unpaid research opportunities:"
        else:
            listings = search_listings_by_keywords(q, max_results=20)
            heading = "CONTEXT: Matching research opportunities:"

        if not listings:
            return ""  # Return empty - let Gemini handle naturally
        return f"{heading}\n\n{format_listings_brief(listings)}"

    # Faculty search
    if qtype == "faculty":
        listings = search_listings_by_faculty(q, max_results=None)
        
        if not listings:
            # Check if asking general question about faculty
            general_patterns = ["which faculty", "what faculty", "who should", "best faculty", "recommend"]
            if any(p in ql for p in general_patterns):
                all_listings = get_all_listings_raw()
                if all_listings:
                    return "CONTEXT: Faculty members with current research opportunities:\n\n" + format_listings_brief(all_listings)
            return ""  # Return empty - let Gemini handle naturally
        
        return "CONTEXT: Faculty-led research projects:\n\n" + format_listings_brief(listings)

    return ""

# ==========================================================
# Response Generation - Natural conversation with AI
# ==========================================================

def generate_chatbot_response(user_input):
    """
    Generate chatbot responses using Vertex AI with conversation context and listing data.
    Minimal hardcoded responses - let Gemini handle naturally with intelligent redirects.
    
    Args:
        user_input (str): User's input message
        
    Returns:
        str: Generated response
    """
    model = initialize_vertex_ai()
    
    # Only hardcoded response for technical errors
    if not model:
        return "I'm having trouble connecting to my AI system right now. Please try again in a moment, or contact support if this issue persists."

    try:
        # Build context from listings
        context_block = _build_context(user_input)

        # Take the last 10 messages from session state for conversation context
        conversation_history = st.session_state.messages[-10:]
        
        # Build the conversation history
        history_text = ""
        for msg in conversation_history:
            role = "Student" if msg["role"] == "user" else "ResearchAI"
            history_text += f"{role}: {msg['content']}\n"
        
        # Add the new user input
        history_text += f"Student: {user_input}\nResearchAI:"

        # Enhanced system prompt with clear redirect guidance
        system_prompt = """You are ResearchAI, a friendly and knowledgeable AI assistant for Southern Connecticut State University (SCSU).

Your primary role is to help students find research opportunities and connect with faculty at SCSU.

CORE CAPABILITIES:
- Search and explain research listings
- Help students find paid/unpaid research positions
- Connect students with faculty members who have active research projects
- Answer questions about research opportunities at SCSU
- Guide students on how to get started with research

IMPORTANT GUIDELINES:
1. Be natural, conversational, and helpful in your responses
2. When research listings are provided in the CONTEXT, use that information to give specific, accurate answers
3. NEVER use technical terms like "database", "system", "data source" - instead say "current opportunities", "available positions", "active listings"
4. When users ask to see ALL listings and you're given a preview, show the preview provided and direct them to the Listings page: "For the complete list of all [X] opportunities with full details and filtering options, visit the Listings page in ResearchConnect."
5. For questions about campus resources (Innovation Hub, JOBSs, OCPD, STEM Center), politely redirect to the Resources page: "For detailed information about [resource name], please visit the Resources page in ResearchConnect."
6. For off-topic questions (jokes, weather, sports, entertainment, personal questions), use this pattern: Briefly acknowledge → Politely redirect → Ask about research interests
7. Always maintain context from the conversation history to handle follow-up questions naturally
8. If you don't have specific information, be honest and suggest how the student can find it
9. Keep responses concise but informative

LANGUAGE TO USE:
✅ "Here are some of the current research opportunities"
✅ "I found these research listings for you"
✅ "Currently available opportunities include"
✅ "For the complete list, visit the Listings page"
✅ "There are [X] total opportunities available"

❌ NEVER SAY: "in the database", "from the database", "database shows", "according to my data sources", "my database"

REDIRECT EXAMPLES FOR OFF-TOPIC QUESTIONS:
- Weather: "I don't have weather information, but I can help you find research opportunities! What field interests you?"
- Jokes: "I appreciate the humor, but I'm focused on helping you discover research opportunities at SCSU. Are you interested in exploring positions in a particular field?"
- Movies/Sports: "That's outside my expertise - I specialize in SCSU research opportunities. Would you like to see current listings?"
- General knowledge: "I'm specifically designed for SCSU research assistance. Let me help you find research positions instead - what's your major or area of interest?"

ABOUT SCSU:
- SCSU stands for Southern Connecticut State University in New Haven, Connecticut
- ResearchConnect is the platform for finding faculty-led research opportunities
- ResearchConnect has dedicated pages: Listings (for browsing all opportunities with filters), Resources (for campus resources), and this Chatbot

Remember: Always redirect off-topic questions back to research opportunities while staying friendly and professional."""

        # Construct the full prompt
        if context_block:
            full_prompt = f"""{system_prompt}

{context_block}

CONVERSATION HISTORY:
{history_text}

Respond naturally based on the research listings context and conversation history. If this is an off-topic question, follow the redirect guidelines."""
        else:
            full_prompt = f"""{system_prompt}

Note: No research listings matched the specific search criteria.

CONVERSATION HISTORY:
{history_text}

Respond naturally and helpfully. If this is an off-topic question, follow the redirect guidelines."""

        # Generate response
        response = model.generate_content(full_prompt)
        return response.text.strip()

    except Exception as e:
        print(f"Vertex AI response failed: {e}")
        return "Sorry, I'm having trouble generating a response right now. Please try rephrasing your question or try again in a moment."
    
# ==========================================================
# Logging
# ==========================================================

def log_conversation(user_input, bot_response):
    """
    Log conversation for analytics and improvement
    
    Args:
        user_input (str): User's input
        bot_response (str): Bot's response
    """
    log_entry = {
        "timestamp": datetime.datetime.now(),
        "user_input": user_input,
        "bot_response": bot_response,
        "session_id": st.session_state.get("session_id", "unknown")
    }
    
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []
    
    st.session_state.conversation_log.append(log_entry)

#-----END OF FILE-----