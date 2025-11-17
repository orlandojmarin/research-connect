# TATIANA
# resources.py
# Streamlit Documentation: https://docs.streamlit.io/get-started 
# run the program with streamlit run home.py

import streamlit as st
from utils.resources_utils import (
    get_innovation_hub_info,
    get_ocpd_info,
    get_stem_centers_info,
    get_jobs_info,
    track_resource_interaction,
    initialize_resources_session
)
from utils.general_utils import (
    auth_gate, get_current_user, configure_page,
    render_scsu_logo, render_sidebar_auth
)

# Configure page FIRST
configure_page(
    title="Campus Resources - ResearchConnect SCSU",
    icon="📚",
    layout="centered"
)

# Auth gate
auth_gate()

# Get user info
user_info = get_current_user()

# Sidebar
render_scsu_logo()
with st.sidebar:
    render_sidebar_auth(show_role=True)

def render_header():
    """Render main page header"""
    st.title("Campus Resources 📚")
    st.subheader("Your guide to SCSU's key support centers and professional development resources")
    st.divider()

def render_innovation_hub():
    """Render Innovation Hub container section"""
    hub_info = get_innovation_hub_info()
    
    with st.container(border=True):
        st.subheader("🚀 Innovation Hub")
        
        # Contact Information at the top, full width
        with st.container(border=True):
            st.write("**📍 Contact Information**")
            st.write(f"**Email:** {hub_info['email']}")
            if hub_info.get('website'):
                st.write(f"**Website:** [{hub_info['website']}]({hub_info['website']})")
        
        st.write()
        st.write("**About the Innovation Hub:**")
        st.write(hub_info['description'])
        
        st.write()
        st.write("**🎯 Research Support:**")
        for service in hub_info['services']:
            st.write(f"• {service}")
            
        if hub_info.get('student_programs'):
            st.write()
            st.write("**🎯 Student Programs:**")
            for program in hub_info['student_programs']:
                st.write(f"• **{program['name']}**: {program['description']}")

def render_jobs():
    """Render JOBSs container section"""
    jobs_info = get_jobs_info()
    
    with st.container(border=True):
        st.subheader("📄 JOBSs")
        
        # Contact Information at the top, full width
        with st.container(border=True):
            st.write("**📍 Contact Information**")
            st.write(f"**Website:** [{jobs_info['website']}]({jobs_info['website']})")
        
        st.write()
        st.write("**About JOBSs:**")
        st.write(jobs_info['description'])

def render_ocpd():
    """Render Office of Career & Professional Development container section"""
    ocpd_info = get_ocpd_info()
    
    with st.container(border=True):
        st.subheader("💼 Office of Career & Professional Development (OCPD)")
        
        # Contact Information at the top, full width
        with st.container(border=True):
            st.write("**📍 Contact Information**")
            st.write(f"**Email:** {ocpd_info['email']}")
            if ocpd_info.get('website'):
                st.write(f"**Website:** [{ocpd_info['website']}]({ocpd_info['website']})")
        
        st.write()
        st.write("**About the Office of Career & Professional Development:**")
        st.write(ocpd_info['description'])
        
        st.write()
        st.write("**🎯 Career Services:**")
        for service in ocpd_info['career_services']:
            st.write(f"• {service}")

def render_stem_centers():
    """Render STEM Centers and Offices container section"""
    stem_info = get_stem_centers_info()
    
    with st.container(border=True):
        st.subheader("🧬 STEM Centers and Offices")
        
        # Contact Information at the top, full width
        with st.container(border=True):
            st.write("**📍 Contact Information**")
            contact = stem_info['stem_center']['contact']
            st.write(f"**Email:** {contact['email']}")
            st.write(f"**Website:** {contact['website']}")
        
        st.write()
        st.write("**About SCSU's STEM Centers and Offices:**")
        st.write(stem_info['stem_center']['description'])
            
        st.write()
        st.write("**🎯 Programs & Services:**")
        for service in stem_info['stem_center']['services']:
            st.write(f"• **{service['name']}**: {service['description']}")

def main():
    """Main function to render the resources page"""
    # Initialize session
    initialize_resources_session()
    
    # Render header
    render_header()
    
    # One column for all resources
    render_jobs()
    render_ocpd()
    render_innovation_hub()
    render_stem_centers()

if __name__ == "__main__":
    main()

#-----END OF FILE-----