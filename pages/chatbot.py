# import the necessary libraries
import streamlit as st

# display the SCSU logo in the sidebar
st.logo("images/scsu_logo.jpg", size="large")

# displaya the title of the page with a divider underneath
st.title("ResearchAI Chatbot 🧠")
st.divider()

# add a chat feature to the page with placeholder text
prompt = st.chat_input(placeholder="Ask ResearchAI for research help...")
if prompt:
    with st.chat_message("user"):
        st.write(prompt)