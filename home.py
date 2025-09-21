# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py

import streamlit as st

st.logo("images/scsu_logo.jpg", size="large")

st.title("Welcome to ResearchConnect 🦉")
st.divider()

st.image("images/logo.png")
st.caption("Hello, I am your friendly AI Assistant, ResearchAI! I can assist you with your research related questions!")

# Introductory text
st.subheader("Getting Started")
st.write(
    """
    ResearchConnect is your one-stop platform for discovering research opportunities, 
    connecting with faculty, and exploring campus resources at SCSU. 

    Use the sidebar to navigate through the different sections of the app:
    """
)

# Page descriptions
st.markdown("### 🔹 Chatbot")
st.write("Ask questions about research, internships, or campus offices and get instant answers.")

st.markdown("### 🔹 Listings")
st.write("Browse and filter current faculty-led research projects.")

st.markdown("### 🔹 Resources")
st.write("Find support offices, career services, and academic resources available at SCSU.")
