# TATIANA
# resources_utils.py

"""
Resources utilities for ResearchConnect SCSU
Handles campus resource data for Innovation Hub, JOBSs, OCPD, and STEM Centers
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
        SCSU's Innovation Hub advances awareness, experience, skill development, and access to jobs and internships in STEM.
        """,
        "email": "innovation@southernct.edu",
        "website": "https://innovation.southernct.edu/",
        "services": [
            "Professional Collaborations & Grant-Funded Projects",
            "Research & Innovation Grant Support"
        ],
        "student_programs": [
            {
                "name": "BioPath",
                "description": "The Bioscience Academic & Career Pathway (BioPath) program was launched in 2015 as a partnership with the City of New Haven to increase student awareness of, skills, and access to opportunities among Life Science and STEM companies in New Haven and Connecticut more broadly."
            },
            {
                "name": "Career Coaching",
                "description": "The Innovation Hub team offers individualized sessions to support students with career development."
            },
            {
                "name": "Emerging Technologies Forum",
                "description": "This conference brings education and industry leaders together with university faculty, teachers, students, and community stakeholders to ensure that today's students are prepared to join the thriving innovatiion ecosystem here in Connecticut."
            },
            {
                "name": "Use-inspired Research",
                "description": "In the CSCU Center for Nanotechnology, students conduct emerging tech research projects through the Werth Industry Academic Fellowship."
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
            SCSU's STEM Centers and Offices provide academic assistance, research opportunities, 
            and career guidance specifically tailored to STEM students. Our goal is to help you 
            succeed in your STEM coursework, engage in cutting-edge research, and prepare for 
            STEM careers or graduate school.
            """,
            "contact": {
                "email": "stemcenter@southernct.edu",
                "website": "https://www.southernct.edu/stem/centers"
            },
            "services": [
                # "Individual and group tutoring in STEM subjects",
                # "Study groups and peer mentoring programs",
                # "Research opportunity coordination and placement",
                # "Graduate school preparation and application assistance",
                # "STEM career counseling and industry connections",
                # "Workshop series on research methods and skills",
                # "Equipment and laboratory access for student projects",
                # "Scholarship and funding opportunity notifications"
                {
                    "name": "Center for Research on Interface Structures and Phenomena (CRISP)",
                    "description": "Aims to enhance the education of future scientists, science teachers, K-12 students, parents, and the general public."
                },
                {
                    "name": "STEM Leadership Institute",
                    "description": "Engages participants in hands-on STEM activities and offers collaborative learning opportunities for school leaders and teachers to participate in a STEM leadership network."
                },
                {
                    "name": "CSCU Center for Nanotechnology",
                    "description": "Fosters collaborative, interdisciplinary research and educational initiatives/programs in micro- and nanotechnology in collaboration with Yale, UConn, and CT State Community College."
                },
                {
                    "name": "Center for Excellence and Mathematics (CEMS)",
                    "description": "Fosters outstanding teaching and research through the enhancement of existing campus initiatives, with the goal of increasing the number and quality of students pursuing careers in STEM."
                },
                {
                    "name": "Werth Center for Coastal Marine Studies",
                    "description": "Provides a means for faculty and students to participate in coastal and marine research and education along Connecticut's urbanized coast and harbors."
                },
                {
                    "name": "SCSU Office of Sustainability",
                    "description": "Connects students, faculty, and staff with the information, people, and tools needed to make our campus more sustainable."
                },
                {
                    "name": "Research Center on Values in Emerging Science and Technology (RC-VEST)",
                    "description": "Focuses on issues located at the intersection of science and values as implemented in emerging technologies."
                }
            ]
        },
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
def search_resources(query: str):
    """
    Return (name, data) for Innovation Hub, JOBSs, OCPD, or STEM Center.
    """
    q = query.lower()

    resources = {
        "innovation hub": get_innovation_hub_info(),
        "jobs": get_jobs_info(),
        "jobss": get_jobs_info(),
        "ocpd": get_ocpd_info(),
        "career center": get_ocpd_info(),
        "stem center": get_stem_centers_info().get("stem_center", {}),
        "stem": get_stem_centers_info().get("stem_center", {}),
    }

    # direct name match
    for name in resources:
        if name in q:
            return name, resources[name]

    # keyword categories
    if any(k in q for k in ["career", "resume", "interview"]):
        return "ocpd", get_ocpd_info()

    if any(k in q for k in ["innovation", "startup", "grant"]):
        return "innovation hub", get_innovation_hub_info()

    if "stem" in q:
        return "stem center", get_stem_centers_info().get("stem_center", {})

    return None, None

#-----END OF FILE-----

