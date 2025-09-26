# TATIANA

"""
Resources utilities for ResearchConnect SCSU
Handles campus resource data for Innovation Hub, OCPD, and STEM Centers
"""

import datetime
import streamlit as st

def initialize_resources_session():
    """Initialize resources session state"""
    if "resource_interactions" not in st.session_state:
        st.session_state.resource_interactions = []
    if "feedback_submitted" not in st.session_state:
        st.session_state.feedback_submitted = False

def get_innovation_hub_info():
    """
    Get comprehensive Innovation Hub information
    
    Returns:
        dict: Innovation Hub details
    """
    return {
        "description": """
        SCSU's Innovation Hub advances awareness, experience and skill development, and access to jobs and internships in STEM.
        """,
        "email": "innovation@southernct.edu",
        "website": "https://innovation.southernct.edu/",
        "services": [
            "Use-Inspired Research",
            "Educator Professional Development", 
            "BioPath",
            "Industry Needs Assessment",
            "Career Coaching",
            "Research & Innovation Grant Support",
            "Professional Collaborations & Grant-Funded Projects",
            "Bioscience Careers Forum",
            "Connecting Students & Professionals of Color",
            "SCSU Centers for Research Excellence"
        ],
        "special_programs": [
            {
                "name": "Startup Accelerator",
                "description": "12-week intensive program for early-stage startups with mentorship and funding opportunities"
            },
            {
                "name": "Innovation Challenge",
                "description": "Annual competition where student teams compete for cash prizes and startup funding"
            },
            {
                "name": "Women in Leadership Academy",
                "description": "Professional development program focused on leadership skills for women entrepreneurs"
            }
        ]
    }

def get_ocpd_info():
    """
    Get comprehensive OCPD (Office of Career & Professional Development) information
    
    Returns:
        dict: OCPD details
    """
    return {
        "description": """
        The Office of Career & Professional Development (OCPD) provides comprehensive career services 
        to help students and alumni achieve their professional goals. From resume writing to interview 
        preparation, internship placement to job search strategies, OCPD is your partner in career success. 
        We work with students at all stages of their academic journey to build skills, explore careers, 
        and connect with employers.
        """,
        "email": "careerservices@southernct.edu", 
        "website": "https://www.southernct.edu/career",
        "career_services": [
            "One-on-one career counseling sessions",
            "Resume and cover letter review and assistance",
            "Interview preparation and mock interviews",
            "Job search strategies and techniques",
            "LinkedIn profile optimization",
            "Salary negotiation workshops",
            "Career assessment and exploration tools",
            "Graduate school application guidance"
        ]
    }

def get_stem_centers_info():
    """
    Get comprehensive STEM Centers and Offices information
    
    Returns:
        dict: STEM centers details
    """
    return {
        "stem_center": {
            "description": """
            The STEM Center at SCSU is the hub for Science, Technology, Engineering, and Mathematics 
            education and research support. We provide academic assistance, research opportunities, 
            and career guidance specifically tailored to STEM students. Our goal is to help you 
            succeed in your STEM coursework, engage in cutting-edge research, and prepare for 
            STEM careers or graduate school.
            """,
            "contact": {
                "email": "stemcenter@southernct.edu",
                "website": "https://www.southernct.edu/stem/centers"
            },
            "services": [
                "Individual and group tutoring in STEM subjects",
                "Study groups and peer mentoring programs",
                "Research opportunity coordination and placement",
                "Graduate school preparation and application assistance",
                "STEM career counseling and industry connections",
                "Workshop series on research methods and skills",
                "Equipment and laboratory access for student projects",
                "Scholarship and funding opportunity notifications"
            ]
        },
        "other_offices": [
            {
                "name": "Environmental Science Center",
                "description": "Specialized facility supporting environmental research, sustainability studies, and field work coordination.",
                "location": "Jennings Hall 300",
                "phone": "(203) 392-6145",
                "email": "envscience@southernct.edu",
                "services": [
                    "Environmental research project support",
                    "Field study coordination and equipment",
                    "Sustainability initiative development",
                    "Laboratory access and training"
                ]
            }
        ]
    }

def get_jobs_info():
    """
    Get comprehensive JOBSs (Job Opportunities Benefiting Southern Students) information

    Returns:
        dict: JOBSs details
    """
    return {
        "description": (
            "Job Opportunities Benefiting Southern Students (JOBSs) is an online job board "
            "available to students and alumni looking for full-time or part-time work, "
            "co-ops, internships, and on-campus student employment."
        ),
        "website": "https://southernct-csm.symplicity.com/students/?signin_tab=0"
    }

def track_resource_interaction(resource_name, interaction_type):
    """
    Track user interactions with resources for analytics
    
    Args:
        resource_name (str): Name of the resource interacted with
        interaction_type (str): Type of interaction (e.g., 'contact_clicked', 'visit_requested')
    """
    interaction = {
        "timestamp": datetime.datetime.now(),
        "resource": resource_name,
        "interaction": interaction_type,
        "session_id": st.session_state.get("session_id", "unknown")
    }
    
    # Store interaction in session state
    if "resource_interactions" not in st.session_state:
        st.session_state.resource_interactions = []
    
    st.session_state.resource_interactions.append(interaction)

def get_resource_usage_stats():
    """
    Get usage statistics for resources
    
    Returns:
        dict: Usage statistics
    """
    interactions = st.session_state.get("resource_interactions", [])
    
    if not interactions:
        return {"total_interactions": 0, "most_popular": "None"}
    
    resource_counts = {}
    for interaction in interactions:
        resource = interaction["resource"]
        resource_counts[resource] = resource_counts.get(resource, 0) + 1
    
    most_popular = max(resource_counts, key=resource_counts.get) if resource_counts else "None"
    
    return {
        "total_interactions": len(interactions),
        "most_popular": most_popular,
        "unique_resources": len(resource_counts)
    }