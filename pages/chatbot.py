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
    st.caption(f"Role: {role}")
    if st.button("Log Out"):
        st.session_state.user = None
        st.session_state.page = "landing"
        st.rerun()

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
    """Render the main chat interface with side-by-side layout using native Streamlit."""
    
    # Initialize expander state tracking if not exists
    if "expander_states" not in st.session_state:
        st.session_state.expander_states = {}
    
    # Group messages into pairs (user prompt + assistant response)
    message_pairs = []
    temp_user = None
    
    for message in st.session_state.messages:
        if message["role"] == "user":
            temp_user = message
        elif message["role"] == "assistant" and temp_user:
            message_pairs.append((temp_user, message))
            temp_user = None
    
    # Display each pair side by side
    for idx, (user_msg, assistant_msg) in enumerate(message_pairs):
        col_left, col_right = st.columns([1, 1], gap="large")
        
        # Create unique key based on message content and timestamp for persistence
        expander_key = f"expander_{user_msg['timestamp'].strftime('%Y%m%d%H%M%S%f')}"
        
        # Initialize expander state if not exists (default to True for new messages)
        if expander_key not in st.session_state.expander_states:
            st.session_state.expander_states[expander_key] = True
        
        with col_left:
            with st.chat_message("user"):
                # Create columns within the chat message for prompt and timestamp
                msg_col1, msg_col2 = st.columns([4, 1])
                with msg_col1:
                    st.write(user_msg['content'])
                with msg_col2:
                    st.caption(f"🕒 {user_msg['timestamp'].strftime('%I:%M %p')}")
        
        with col_right:
            # Use stored state for expanded parameter
            with st.expander(
                "**ResearchAI Response** 🦉", 
                expanded=st.session_state.expander_states[expander_key]
            ):
                # Container with fixed height and scrolling
                st.markdown(
                    """
                    <style>
                    .scrollable-response {
                        max-height: 400px;
                        overflow-y: auto;
                        padding-right: 10px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="scrollable-response">{assistant_msg["content"]}</div>',
                    unsafe_allow_html=True
                )
                st.caption(f"🕒 {assistant_msg['timestamp'].strftime('%I:%M %p')}")

def handle_user_input():
    """Handle user input and generate responses"""
    # Chat input at the bottom
    prompt = st.chat_input(
        placeholder="Ask ResearchAI about research opportunities, campus resources, or anything else...",
        key="chat_input"
    )
    
    # Process user input
    if prompt:
        # Add user message
        add_user_message(prompt)
        
        # Show loading spinner while generating response
        with st.spinner("🤔 ResearchAI is thinking..."):
            # Simulate processing time
            time.sleep(random.uniform(1, 2.5))
            
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