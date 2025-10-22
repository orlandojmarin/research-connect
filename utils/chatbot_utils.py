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

# Load environment variables
load_dotenv()

def initialize_vertex_ai():
    """
    Initialize Vertex AI connection
    
    Returns:
        GenerativeModel or None: Initialized model or None if fails
    """
    try:
        project_id = os.getenv('GCP_PROJECT_ID')
        if not project_id:
            print("GCP_PROJECT_ID not found in environment variables")
            return None
        
        vertexai.init(project=project_id, location="us-central1")
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

def add_user_message(content):
    """
    Add user message to chat history
    
    Args:
        content (str): User message content
    """
    message = {
        "role": "user",
        "content": content,
        "timestamp": datetime.datetime.now()
    }
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

        # Combine system prompt + conversation
        full_prompt = f"{system_prompt}\n\n{history_text}"

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
