# ORLANDO
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# Run the app with streamlit run home.py

import streamlit as st
import time
import random
from utils.chatbot_utils import (initialize_chat_session,get_sidebar_info,clear_conversation,
add_user_message,add_assistant_message,generate_chatbot_response,log_conversation)

# --- USER BADGE + LOG OUT and Auth gate ---
if "user" not in st.session_state or st.session_state.user is None:
    st.switch_page("home.py")
    st.stop()

# NEW — grab user info for this page
user = st.session_state.user              
email = user["email"]                     
uid   = user["uid"]                       
role  = user.get("role", "student")       

with st.sidebar:
    st.success(f"Logged in as {email}")
    if st.button("Log Out", use_container_width=True):
        st.session_state.user = None
        st.session_state.page = "landing"
        st.rerun()
    st.divider()

def main():
    """Main function to render the chatbot page"""
    # Configure page
    configure_page()
    
    # Initialize chat session
    initialize_chat_session()
    
    # Render page components
    render_sidebar()
    render_header()
    render_chat_interface()
    handle_user_input()

def configure_page():
    """Configure page settings and metadata"""
    st.set_page_config(
        page_title="ResearchAI Chatbot - ResearchConnect SCSU",
        page_icon="🧠",
        layout="wide"
    )

def render_sidebar():
    """Render sidebar with chatbot info and statistics"""
    st.logo("images/scsu_logo.jpg", size="large")
    
    with st.sidebar:
        # Clear conversation button
        if st.button("🔄 Clear Conversation", type="secondary", use_container_width=True):
            clear_conversation()
            st.rerun()

def render_header():
    """Render main page header"""
    st.title("ResearchAI Chatbot 🧠")
    st.subheader("Your intelligent assistant for research opportunities and campus resources at SCSU")
    st.divider()

def render_chat_interface():
    """Render the main chat interface with vertical layout using native Streamlit."""
    for idx, message in enumerate(st.session_state.messages):
        with st.container():
            if message["role"] == "user":
                render_user_message(message)
            elif message["role"] == "assistant":
                render_assistant_message(message, idx)

def render_user_message(message):
    """Render a user message in vertical layout with timestamp at bottom-left."""
    with st.chat_message("user"):
        content_container = st.container()
        with content_container:
            if "summary" in message and len(message['content']) > 150:
                with st.expander(f"**{message['summary']}**", expanded=False):
                    st.write(message['content'])
            else:
                st.write(message['content'])

        # Always show timestamp in the same bottom-left area
        st.caption(f"🕒 {message['timestamp'].strftime('%I:%M %p')}")


def render_assistant_message(message, idx):
    """Render an assistant message with timestamp bottom-left aligned."""
    with st.chat_message("assistant", avatar="🦉"):
        content_container = st.container()
        with content_container:
            st.markdown(message['content'])
        st.caption(f"🕒 {message['timestamp'].strftime('%I:%M %p')}")


def handle_user_input():
    """Handle user input and generate responses"""
    # Chat input at the bottom
    prompt = st.chat_input(
        placeholder="Ask ResearchAI about research opportunities or campus resources...",
        key="chat_input"
    )
    
    # Process user input
    if prompt:
        # Add user message
        add_user_message(prompt)
        
        # Show loading spinner while generating response
        with st.spinner("🤔 ResearchAI is thinking..."):
            # Generate response
            response = generate_chatbot_response(prompt)
        
        # Add assistant response to history
        add_assistant_message(response)
        
        # Log the conversation
        log_conversation(prompt, response)
        
        # Rerun to display the new messages
        st.rerun()

if __name__ == "__main__":
    main()

#-----END OF FILE-----