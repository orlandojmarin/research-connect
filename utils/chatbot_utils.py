# ORLANDO
"""
Chatbot utilities for ResearchConnect SCSU
Handles chatbot functionality, response generation, and conversation management
"""

import datetime
import random
import streamlit as st
import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
# --- NEW (RAG imports) ---
# Vertex AI Search (website context) + Firebase listings helpers
from utils.rag_utils import query_vertex_search, format_context, RAGSearchError
from utils.firebase_query_utils import (
    search_listings_by_keyword,
    search_listings_by_faculty,
    search_paid_listings,
    format_listings_as_context,
)

# Load environment variables
load_dotenv()

@st.cache_resource
def initialize_vertex_ai():
    """
    Initialize Vertex AI. Read from Streamlit secrets first, then .env.
    """
    try:
        project_id = st.secrets.get("GCP_PROJECT_ID") or os.getenv("GCP_PROJECT_ID")
        region = (
            st.secrets.get("VERTEX_REGION") or
            os.getenv("VERTEX_REGION") or
            "us-central1"
        )
        if not project_id:
            print("GCP_PROJECT_ID missing (check .streamlit/secrets.toml or .env)")
            return None

        vertexai.init(project=project_id, location=region)
        model = GenerativeModel("gemini-2.5-flash")
        print(f"Vertex AI initialized (project={project_id}, region={region})")
        return model
    except Exception as e:
        print(f"Failed to initialize Vertex AI: {e}")
        return None

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
            "title": "🧠 ResearchAI Assistant",
            "help_topics": [
                "🔍 Finding research opportunities",
                "👨‍🏫 Information about faculty",
                "📚 Campus resources and offices", 
                "💼 Internship and fellowship programs",
                "📝 Application processes",
                "❓ General research questions"
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
        # Fallback: return first 7 words if AI fails
        words = prompt_text.split()[:7]
        return " ".join(words) + "..."
    
    try:
        summary_prompt = f"""Generate a concise 5-7 word summary of the user's request. 
Only return the summary, nothing else.

Text: {prompt_text}

Summary:"""
        
        response = model.generate_content(summary_prompt)
        summary = response.text.strip()
        
        # Ensure it's not too long (fallback)
        if len(summary.split()) > 10:
            words = prompt_text.split()[:7]
            return " ".join(words) + "..."
        
        return summary
        
    except Exception as e:
        print(f"Summary generation failed: {e}")
        # Fallback: return first 7 words
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

# -------- NEW: RAG classification + context builders --------
RESEARCH_KWS = {
    "research", "opportunity", "opportunities", "listing", "listings",
    "position", "opening", "paid", "unpaid", "hours", "machine learning",
    "ai", "data"
}
FACULTY_KWS  = {"professor", "faculty", "dr.", "dr ", "dr", "advisor", "pi"}

def _classify_question(q: str) -> str:
    """Classify the question: listings | faculty | general."""
    ql = (q or "").lower()
    if any(k in ql for k in FACULTY_KWS):
        return "faculty"
    if any(k in ql for k in RESEARCH_KWS):
        return "listings"
    return "general"

def _build_context(q: str) -> str:
    """
    Retrieve context from Firebase and/or Vertex AI Search based on question type.
    Returns a plain-text context block (may be empty).
    """
    qtype = _classify_question(q)

    if qtype == "listings":
        # Quick paid filter
        if "paid" in (q or "").lower():
            listings = search_paid_listings(True)
        else:
            listings = search_listings_by_keyword(q)
        return format_listings_as_context(listings)

    if qtype == "faculty":
        fb_ctx = format_listings_as_context(search_listings_by_faculty(q))
        try:
            web_ctx = format_context(query_vertex_search(q, top_k=5))
        except RAGSearchError:
            web_ctx = ""
        parts = [p for p in (fb_ctx, web_ctx) if p]
        return "\n\n".join(parts)

    # general → website
    try:
        return format_context(query_vertex_search(q, top_k=5))
    except RAGSearchError:
        return ""
# -------- /NEW --------

def generate_chatbot_response(user_input):
    """
    Generate chatbot responses using Vertex AI with conversation context.
    
    Args:
        user_input (str): User's input message
        
    Returns:
        str: Generated response
    """
    # Get cached model instance
    model = initialize_vertex_ai()
    
    if not model:
        return "Vertex AI is not initialized."

    try:
        # System instructions
        system_prompt = """You are ResearchAI, an AI assistant for Southern Connecticut State University (SCSU). 
Your role is to help students find research opportunities, connect with faculty, and navigate campus resources.
Be friendly, helpful, and specific to SCSU when possible. If you don't know something specific about SCSU, 
guide the user to check the appropriate office or webpage."""


        # Take the last 10 messages from session state for context
        conversation_history = st.session_state.messages[-10:]
        
        # Build the prompt including both user and assistant messages
        history_text = ""
        for msg in conversation_history:
            role = "Student" if msg["role"] == "user" else "ResearchAI"
            history_text += f"{role}: {msg['content']}\n"

        
        # Add the new user input at the end
        history_text += f"Student: {user_input}\nResearchAI:"
        # --- NEW: fetch context for RAG ---
        context_block = _build_context(user_input)
        # --- /NEW ---
        # Combine system prompt + conversation
        #full_prompt = f"{system_prompt}\n\n{history_text}"
        full_prompt = (
            f"{system_prompt}\n\n"
            f"CONTEXT (may be empty):\n{context_block or '[no context]'}\n\n"
            f"{history_text}"
        )
        # Generate response
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        print(f"Vertex AI response failed: {e}")
        return "Sorry, I'm having trouble generating a response right now."


def log_conversation(user_input, bot_response):
    """
    Log conversation for analytics and improvement
    
    Args:
        user_input (str): User's input
        bot_response (str): Bot's response
    """
    # Placeholder for conversation logging
    # In the real application, log this to a database
    log_entry = {
        "timestamp": datetime.datetime.now(),
        "user_input": user_input,
        "bot_response": bot_response,
        "session_id": st.session_state.get("session_id", "unknown")
    }
    
    # For now, just store in session state
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []
    
    st.session_state.conversation_log.append(log_entry)

#-----END OF FILE-----