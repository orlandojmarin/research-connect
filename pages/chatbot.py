# chatbot.py
# ORLANDO (chatbot UI and vertex AI integration) and SANA (RAG)
# Streamlit Documentation: https://docs.streamlit.io/get-started 

import streamlit as st
from utils.chatbot_utils import (
    initialize_chat_session, get_sidebar_info, clear_conversation,
    add_user_message, add_assistant_message, generate_chatbot_response, log_conversation
)
from utils.general_utils import (
    auth_gate, get_current_user, configure_page, 
    render_scsu_logo, render_sidebar_auth
)

# Configure page FIRST
configure_page(
    title="ResearchAI Chatbot - ResearchConnect SCSU",
    icon="🧠",
    layout="wide"
)

# Auth gate
auth_gate()

# Get user info
user_info = get_current_user()

# Sidebar
render_scsu_logo()
with st.sidebar:
    render_sidebar_auth(show_role=True)
    st.divider()
    
    # Clear conversation button
    if st.button("🔄 Clear Conversation", type="secondary", width="stretch"):
        clear_conversation()
        st.rerun()

def main():
    """Main function to render the chatbot page"""
    # Initialize chat session
    initialize_chat_session()
    
    # Render page components
    render_header()
    render_chat_interface()
    handle_user_input()

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

# def render_user_message(message):
#     """Render a user message in vertical layout with timestamp at bottom-left."""
#     with st.chat_message("user"):
#         content_container = st.container()
#         with content_container:
#             if "summary" in message and len(message['content']) > 150:
#                 with st.expander(f"**{message['summary']}**", expanded=False):
#                     st.write(message['content'])
#             else:
#                 st.write(message['content'])

#         # Always show timestamp in the same bottom-left area
#         st.caption(f"🕒 {message['timestamp'].strftime('%I:%M %p')}")

# def render_assistant_message(message, idx):
#     """Render an assistant message with timestamp bottom-left aligned."""
#     with st.chat_message("assistant", avatar="🦉"):
#         content_container = st.container()
#         with content_container:
#             st.markdown(message['content'])

#         st.caption(f"🕒 {message['timestamp'].strftime('%I:%M %p')}")

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

        # Convert UTC timestamp to local time for display
        local_time = message['timestamp'].astimezone()
        st.caption(f"🕒 {local_time.strftime('%I:%M %p')}")

def render_assistant_message(message, idx):
    """Render an assistant message with timestamp bottom-left aligned."""
    with st.chat_message("assistant", avatar="🦉"):
        content_container = st.container()
        with content_container:
            st.markdown(message['content'])

        # Convert UTC timestamp to local time for display
        local_time = message['timestamp'].astimezone()
        st.caption(f"🕒 {local_time.strftime('%I:%M %p')}")

def handle_user_input():
    """Handle user input and generate responses"""
    # Chat input at the bottom
    prompt = st.chat_input(
        placeholder="Ask ResearchAI about research opportunities at SCSU...",
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