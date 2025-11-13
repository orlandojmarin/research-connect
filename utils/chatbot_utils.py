# ORLANDO
# chatbot_utils.py

"""
Chatbot utilities for ResearchConnect SCSU
Handles chatbot functionality, response generation, and conversation management
Updated to support environment variables for Cloud Run deployment
"""

import datetime
import random
import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account
import os
import json

def get_config(key, default=None):
    """
    Get config from environment variables (Cloud Run) or st.secrets (local).
    
    Args:
        key: Configuration key to retrieve
        default: Default value if key not found
    
    Returns:
        Configuration value or default
    """
    # Try environment variable first (for Cloud Run)
    env_value = os.environ.get(key)
    if env_value:
        return env_value
    
    # Fall back to st.secrets (for local development)
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
        # Get project ID from environment or secrets
        project_id = get_config("GCP_PROJECT_ID")
        
        if not project_id:
            print("Error: GCP_PROJECT_ID not found in environment variables or secrets")
            return None
        
        # Try to get service account from environment variable first (Cloud Run)
        service_account_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
        
        if service_account_json:
            # Cloud Run: parse JSON string from environment variable
            service_account_dict = json.loads(service_account_json)
            credentials = service_account.Credentials.from_service_account_info(
                service_account_dict
            )
        else:
            # Local: use secrets.toml
            try:
                credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"]
                )
            except Exception as e:
                print(f"Warning: Could not load service account from secrets: {e}")
                # Try using default credentials as last resort
                credentials = None
        
        # Initialize Vertex AI with credentials
        vertexai.init(
            project=project_id, 
            location="us-central1",
            credentials=credentials
        )
        
        model = GenerativeModel("gemini-2.5-flash")
        print("Vertex AI initialized successfully")
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
        return "I'm having trouble connecting to my AI system right now. Please try again in a moment, or contact support if this issue persists."

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

        # Combine system prompt + conversation
        full_prompt = f"{system_prompt}\n\n{history_text}"

        # Generate response
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        print(f"Vertex AI response failed: {e}")
        return "Sorry, I'm having trouble generating a response right now. Please try rephrasing your question or try again in a moment."


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