# ORLANDO
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py

import streamlit as st
from utils.home_utils import (
    get_platform_stats, 
    get_last_updated_date,
    get_quick_actions,
    get_feature_descriptions,
    get_success_tips,
    get_example_interactions,
    get_contact_info,
    initialize_session_state,
    track_user_interaction
)

def configure_page():
    """Configure page settings and metadata"""
    st.set_page_config(
        page_title="ResearchConnect SCSU",
        page_icon="🦉",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def render_sidebar():
    """Render sidebar with navigation and statistics"""
    st.logo("images/scsu_logo.jpg", size="large")
    
    with st.sidebar:
        st.divider()
        st.subheader("🎯 Quick Navigation")
        st.write("- 🧠 **Chatbot**: Get instant AI assistance")
        st.write("- 📋 **Listings**: Browse research opportunities")
        st.write("- 📚 **Resources**: Find campus support")
        
        st.divider()
        st.subheader("📊 Platform Stats")
        
        # Get and display platform statistics
        stats = get_platform_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Research Projects", stats["active_projects"], stats["project_change"])
        with col2:
            st.metric("Available Resources", stats["available_resources"], stats["resource_change"])
        
        st.divider()
        st.caption(f"**Last Updated:** {get_last_updated_date()}")

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
                track_user_interaction("quick_action_click", {"action": action["text"]})
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

def render_success_tips():
    """Render success tips section"""
    st.subheader("💡 Tips for Success")
    tips = get_success_tips()
    
    tip_col1, tip_col2 = st.columns(2)
    
    with tip_col1:
        with st.container(border=True):
            st.write(f"**{tips['students']['title']}**")
            for tip in tips['students']['tips']:
                st.write(f"• {tip}")
    
    with tip_col2:
        with st.container(border=True):
            st.write(f"**{tips['faculty']['title']}**")
            for tip in tips['faculty']['tips']:
                st.write(f"• {tip}")

def render_getting_started():
    """Render getting started section"""
    st.subheader("🚀 Getting Started")
    st.write("""
    ResearchConnect is your one-stop platform for discovering research opportunities, 
    connecting with faculty, and exploring campus resources at SCSU. 
    
    Use the sidebar to navigate through the different sections of the app, or use the quick action buttons above!
    """)
    
    # Example interactions expandable section
    examples = get_example_interactions()
    with st.expander("🤔 Not sure where to start? Here are some ideas:"):
        st.write("**Try asking ResearchAI:**")
        for question in examples["chatbot_questions"]:
            st.write(f"• {question}")
        
        st.write("**Browse Research Listings for:**")
        for item in examples["listings_browse"]:
            st.write(f"• {item}")
        
        st.write("**Explore Resources to find:**")
        for item in examples["resources_explore"]:
            st.write(f"• {item}")

def render_contact_info():
    """Render contact and support information"""
    st.subheader("🤝 Need Help?")
    contact = get_contact_info()
    
    help_col1, help_col2, help_col3 = st.columns(3)
    
    with help_col1:
        with st.container(border=True):
            st.write(f"**{contact['chatbot_help']['title']}**")
            st.write(contact['chatbot_help']['description'])
            for topic in contact['chatbot_help']['topics']:
                st.write(f"• {topic}")
    
    with help_col2:
        with st.container(border=True):
            st.write(f"**{contact['technical_support']['title']}**")
            st.write(contact['technical_support']['description'])
            for detail in contact['technical_support']['details']:
                st.write(f"• {detail}")
    
    with help_col3:
        with st.container(border=True):
            st.write(f"**{contact['in_person']['title']}**")
            st.write(contact['in_person']['description'])
            for location in contact['in_person']['locations']:
                st.write(f"• {location}")

def render_footer():
    """Render footer information"""
    st.divider()
    st.info("**ResearchConnect SCSU** | Connecting Students with Research Opportunities")
    st.caption("Developed by Tatiana Eng, Orlando Marin, and Sana Muneer | CSC 400 Capstone Project")

def main():
    """Main function to render the home page"""
    # Configure page and initialize session
    configure_page()
    initialize_session_state()
    st.logo("images/scsu_logo.jpg", size="large")
    
    # Render page components
    # render_sidebar()
    render_header()
    render_quick_actions()
    st.divider()
    render_features()
    # st.divider()
    # render_success_tips()
    # st.divider()
    # render_getting_started()
    # st.divider()
    # render_contact_info()
    render_footer()

if __name__ == "__main__":
    main()