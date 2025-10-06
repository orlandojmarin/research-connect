# ORLANDO
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py

import streamlit as st
from utils.home_utils import (get_quick_actions, get_feature_descriptions, 
initialize_session_state)

def main():
    """Main function to render the home page"""
    # Configure page and initialize session
    configure_page()
    initialize_session_state()
    st.logo("images/scsu_logo.jpg", size="large")
    
    # Render page components
    render_header()
    render_quick_actions()
    st.divider()
    render_features()
    render_footer()

def configure_page():
    """Configure page settings and metadata"""
    st.set_page_config(
        page_title="ResearchConnect SCSU",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_header():
    """Render main header and welcome section"""
    st.title("Welcome to ResearchConnect 🦉")
    st.subheader("Your gateway to research opportunities and academic resources at SCSU")
    
    # Display logo and welcome message
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("images/logo.png", width=300)
    
    st.success("**Hello! I'm ResearchAI, your friendly AI assistant.** I'm here to help you discover research opportunities, connect with faculty, and navigate SCSU's academic resources!")
    st.divider()

def render_quick_actions():
    """Render quick action buttons"""
    st.subheader("🚀 Quick Actions")
    actions = get_quick_actions()
    
    cols = st.columns(len(actions))
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(
                action["text"], 
                type=action["type"], 
                use_container_width=True, 
                help=action["help"]
            ):
                st.switch_page(action["page"])

def render_features():
    """Render platform features section"""
    st.subheader("🌟 Platform Features")
    features = get_feature_descriptions()
    
    # Chatbot feature
    with st.container(border=True):
        st.subheader(features["chatbot"]["title"])
        st.write(f"**{features['chatbot']['subtitle']}**")
        
        col1, col2 = st.columns(2)
        benefits = features["chatbot"]["benefits"]
        mid_point = len(benefits) // 2
        
        with col1:
            for benefit in benefits[:mid_point]:
                st.write(f"✅ {benefit}")
        with col2:
            for benefit in benefits[mid_point:]:
                st.write(f"✅ {benefit}")
    
    # Research Listings feature
    with st.container(border=True):
        st.subheader(features["listings"]["title"])
        st.write(f"**{features['listings']['subtitle']}**")
        
        col1, col2 = st.columns(2)
        benefits = features["listings"]["benefits"]
        mid_point = len(benefits) // 2
        
        with col1:
            for benefit in benefits[:mid_point]:
                st.write(f"🔍 {benefit}")
        with col2:
            for benefit in benefits[mid_point:]:
                st.write(f"🔍 {benefit}")
    
    # Resources feature
    with st.container(border=True):
        st.subheader(features["resources"]["title"])
        st.write(f"**{features['resources']['subtitle']}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**🔬 Academic Support:**")
            for item in features["resources"]["academic_support"]:
                st.write(f"• {item}")
        with col2:
            st.write("**💼 Career Services:**")
            for item in features["resources"]["career_services"]:
                st.write(f"• {item}")

def render_footer():
    """Render footer information"""
    st.divider()
    st.info("**ResearchConnect SCSU** | Connecting Students with Research Opportunities")
    st.caption("Developed by Tatiana Eng, Orlando Marin, and Sana Muneer | CSC 400 Capstone Project")

if __name__ == "__main__":
    main()