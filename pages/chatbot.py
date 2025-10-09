# ORLANDO
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py

import streamlit as st
import time
import random
from utils.chatbot_utils import (initialize_chat_session,get_sidebar_info,clear_conversation,
add_user_message,add_assistant_message,generate_chatbot_response,log_conversation)

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
    
    sidebar_config = get_sidebar_info()
    
    with st.sidebar:
        # Assistant description
        st.subheader(sidebar_config["assistant_description"]["title"])
        st.write("I'm here to help you with:")
        for topic in sidebar_config["assistant_description"]["help_topics"]:
            st.write(f"• {topic}")
        
        st.divider()
        
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
    """Render main chat interface"""
    st.subheader("💬 Conversation")
    
    # Display chat history
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.write(message["content"])
            st.caption(f"*{message['timestamp'].strftime('%I:%M %p')}*")

def handle_user_input():
    """Handle user input and generate responses"""
    # Chat input
    prompt = st.chat_input(
        placeholder="Ask ResearchAI about research opportunities, campus resources, or anything else...",
        key="chat_input"
    )
    
    # Process user input
    if prompt:
        # Add user message
        add_user_message(prompt)
        
        # Display user message immediately
        with st.chat_message("user"):
            st.write(prompt)
            st.caption(f"*{st.session_state.messages[-1]['timestamp'].strftime('%I:%M %p')}*")
        
        # Show thinking message and generate response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                # Simulate processing time
                time.sleep(random.uniform(1, 2.5))
                
                # Generate response
                response = generate_chatbot_response(prompt)
                
                # Display response
                st.write(response)
                response_time = st.session_state.messages[-1]['timestamp'].strftime('%I:%M %p')
                st.caption(f"*{response_time}*")
        
        # Add assistant response to history
        add_assistant_message(response)
        
        # Log the conversation
        log_conversation(prompt, response)

if __name__ == "__main__":
    main()