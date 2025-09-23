# ORLANDO

"""
Home utilities for ResearchConnect SCSU
Handles functionality and data management for the home page
"""

import datetime
import streamlit as st

def get_platform_stats():
    """
    Retrieve platform statistics for display on homepage
    
    Returns:
        dict: Dictionary containing platform statistics
    """
    # Mock data - replace with actual database queries
    stats = {
        "active_projects": 47,
        "project_change": 3,
        "available_resources": 23,
        "resource_change": 1,
        "total_faculty": 156,
        "active_students": 892
    }
    return stats

def get_last_updated_date():
    """
    Get the last updated timestamp for the platform
    
    Returns:
        str: Formatted date string
    """
    return datetime.datetime.now().strftime('%B %d, %Y')

def get_featured_opportunities():
    """
    Get featured research opportunities for homepage display
    
    Returns:
        list: List of featured opportunities
    """
    # Mock data - replace with database queries
    featured = [
        {
            "title": "AI/ML Research Assistant",
            "department": "Computer Science",
            "faculty": "Dr. Smith",
            "type": "Paid Position"
        },
        {
            "title": "Environmental Science Project",
            "department": "Biology",
            "faculty": "Dr. Johnson",
            "type": "Summer Research"
        },
        {
            "title": "Business Analytics Study",
            "department": "Business",
            "faculty": "Dr. Williams",
            "type": "Volunteer"
        }
    ]
    return featured

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

def get_success_tips():
    """
    Get success tips for students and faculty
    
    Returns:
        dict: Dictionary containing tips for different user types
    """
    tips = {
        "students": {
            "title": "🎯 For Students:",
            "tips": [
                "Create a detailed profile highlighting your interests and skills",
                "Don't hesitate to reach out to faculty about their research",
                "Consider both paid and unpaid research opportunities", 
                "Look for projects that align with your career goals",
                "Use the chatbot to get quick answers and guidance"
            ]
        },
        "faculty": {
            "title": "👨‍🏫 For Faculty:",
            "tips": [
                "Post detailed project descriptions to attract the right students",
                "Specify required skills and time commitments clearly",
                "Update your listings regularly to keep them current",
                "Use the platform to find motivated student researchers",
                "Connect with campus resource offices for additional support"
            ]
        }
    }
    return tips

def get_example_interactions():
    """
    Get example interactions for new users
    
    Returns:
        dict: Dictionary containing example questions and actions
    """
    examples = {
        "chatbot_questions": [
            '"What research opportunities are available in Computer Science?"',
            '"How do I apply for undergraduate research?"',
            '"Tell me about the STEM Center"',
            '"What internships are available through the Business department?"'
        ],
        "listings_browse": [
            "Current faculty-led projects in your field",
            "Summer research opportunities", 
            "Paid research assistant positions"
        ],
        "resources_explore": [
            "Campus support offices and their services",
            "Career development programs",
            "Academic support resources"
        ]
    }
    return examples

def get_contact_info():
    """
    Get contact and support information
    
    Returns:
        dict: Dictionary containing contact information
    """
    contact = {
        "chatbot_help": {
            "title": "🧠 Use ResearchAI",
            "description": "Ask our chatbot any questions about:",
            "topics": [
                "Research opportunities",
                "Application processes", 
                "Campus resources",
                "Faculty information"
            ]
        },
        "technical_support": {
            "title": "📧 Contact Support",
            "description": "For technical issues:",
            "details": [
                "Email: researchconnect@southernct.edu",
                "Phone: (203) 392-XXXX",
                "Office hours: Mon-Fri 9AM-5PM"
            ]
        },
        "in_person": {
            "title": "📍 Visit Campus Resources", 
            "description": "In-person assistance:",
            "locations": [
                "STEM Center (Engleman Hall)",
                "Career Services (Student Center)",
                "Academic Support (Library)"
            ]
        }
    }
    return contact

def initialize_session_state():
    """
    Initialize session state variables for the home page
    """
    if "home_visited" not in st.session_state:
        st.session_state.home_visited = True
        st.session_state.visit_time = datetime.datetime.now()

def track_user_interaction(action_type, details=None):
    """
    Track user interactions for analytics
    
    Args:
        action_type (str): Type of interaction
        details (dict, optional): Additional interaction details
    """
    # Placeholder for analytics tracking
    # In a real application, you would log this to a database
    interaction = {
        "timestamp": datetime.datetime.now(),
        "action": action_type,
        "details": details or {}
    }
    
    # For now, just store in session state
    if "interactions" not in st.session_state:
        st.session_state.interactions = []
    
    st.session_state.interactions.append(interaction)