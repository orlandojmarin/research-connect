# ORLANDO
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py

import streamlit as st
import time
import random
from utils.chatbot_utils import (
    initialize_chat_session,
    get_sidebar_info,
    get_chat_statistics,
    clear_conversation,
    get_suggested_questions,
    add_user_message,
    add_assistant_message,
    generate_chatbot_response,
    get_help_navigation,
    log_conversation
)

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
        
        # Quick tips
        with st.container(border=True):
            st.subheader(sidebar_config["quick_tips"]["title"])
            st.write("**Ask me things like:**")
            for question in sidebar_config["quick_tips"]["example_questions"]:
                st.write(f'• "{question}"')
        
        st.divider()
        
        # Clear conversation button
        if st.button("🔄 Clear Conversation", type="secondary", use_container_width=True):
            clear_conversation()
            st.rerun()
        
        # Show conversation stats if there are messages
        stats = get_chat_statistics()
        if stats["total_messages"] > 1:
            st.metric("Questions Asked", stats["user_messages"])
            st.metric("Total Messages", stats["total_messages"])

def render_header():
    """Render main page header"""
    st.title("ResearchAI Chatbot 🧠")
    st.subheader("Your intelligent assistant for research opportunities and campus resources at SCSU")
    st.divider()

def render_suggested_questions():
    """Render suggested questions for new users"""
    if len(st.session_state.messages) <= 1:
        st.subheader("💡 Popular Questions")
        st.write("Click on any question below to get started:")
        
        # Get suggestions and create columns
        suggestions = get_suggested_questions()
        col1, col2 = st.columns(2)
        
        # Display suggestions as buttons
        for i, (button_text, question) in enumerate(suggestions):
            col = col1 if i % 2 == 0 else col2
            with col:
                if st.button(button_text, key=f"suggestion_{i}", use_container_width=True):
                    add_user_message(question)
                    st.rerun()
        
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

def render_help_section():
    """Render additional help section at bottom"""
    if len(st.session_state.messages) > 1:
        st.divider()
        
        help_config = get_help_navigation()
        
        with st.expander("🆘 Need more help?"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Other ways to get assistance:**")
                for assistance_option in help_config["other_assistance"]:
                    st.write(f"• {assistance_option}")
            
            with col2:
                st.write("**Quick navigation:**")
                for nav_option in help_config["navigation_options"]:
                    if st.button(nav_option["text"], key=nav_option["key"]):
                        st.switch_page(nav_option["page"])

def main():
    """Main function to render the chatbot page"""
    # Configure page
    configure_page()
    
    # Initialize chat session
    initialize_chat_session()
    
    # Render page components
    render_sidebar()
    render_header()
    render_suggested_questions()
    render_chat_interface()
    handle_user_input()
    render_help_section()

if __name__ == "__main__":
    main()