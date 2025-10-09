# ORLANDO

"""
Home utilities for ResearchConnect SCSU
Handles functionality and data management for the home page
"""

import datetime
import streamlit as st


def get_quick_actions():
    """
    Define quick action buttons configuration
    
    Returns:
        list: List of quick action configurations
    """
    actions = [
        {
            "text": "🧠 Ask ResearchAI",
            "page": "pages/chatbot.py",
            "type": "primary",
            "help": "Get instant answers about research opportunities"
        },
        {
            "text": "📋 Browse Research", 
            "page": "pages/listings.py",
            "type": "secondary",
            "help": "Explore current faculty-led projects"
        },
        {
            "text": "📚 Find Resources",
            "page": "pages/resources.py", 
            "type": "secondary",
            "help": "Discover campus support services"
        }
    ]
    return actions

def get_feature_descriptions():
    """
    Get detailed feature descriptions for the platform
    
    Returns:
        dict: Dictionary containing feature information
    """
    features = {
        "chatbot": {
            "title": "🧠 ResearchAI Chatbot",
            "subtitle": "Instant, intelligent assistance for all your research questions",
            "benefits": [
                "Ask about specific research opportunities",
                "Get guidance on application processes", 
                "Find information about faculty and their work",
                "Learn about internship and fellowship programs",
                "Discover campus support offices and services",
                "Available 24/7 to help you navigate your research journey"
            ]
        },
        "listings": {
            "title": "📋 Research Listings",
            "subtitle": "Comprehensive database of faculty-led research projects",
            "benefits": [
                "Browse opportunities by department or field",
                "Filter by research type and commitment level",
                "View detailed project descriptions",
                "Connect directly with faculty researchers", 
                "Find both undergraduate and graduate opportunities",
                "Updated regularly with new opportunities across all disciplines"
            ]
        },
        "resources": {
            "title": "📚 Campus Resources", 
            "subtitle": "Your comprehensive guide to SCSU's academic and career support services",
            "academic_support": [
                "STEM Center resources and programs",
                "Research methodology workshops",
                "Academic writing support", 
                "Statistical analysis assistance"
            ],
            "career_services": [
                "Office of Career and Professional Development",
                "Internship and fellowship programs",
                "Women in Leadership Academy",
                "Business career resources"
            ]
        }
    }
    return features

def initialize_session_state():
    """
    Initialize session state variables for the home page
    """
    if "home_visited" not in st.session_state:
        st.session_state.home_visited = True
        st.session_state.visit_time = datetime.datetime.now()