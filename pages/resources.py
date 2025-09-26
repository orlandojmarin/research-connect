# TATIANA
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

def configure_page():
    """Configure page settings and metadata"""
    st.set_page_config(
        page_title="Campus Resources - ResearchConnect SCSU",
        page_icon="📚",
        layout="wide"
    )
        
def render_header():
    """Render main page header"""
    st.title("Campus Resources 📚")
    st.subheader("Your guide to SCSU's key support centers and professional development resources")
    
    # st.info("**Explore the resource centers below** - click on each section to learn more about services, programs, and contact information.")
    st.divider()

def render_innovation_hub():
    """Render Innovation Hub expandable section"""
    hub_info = get_innovation_hub_info()
    
    with st.expander("🚀 Innovation Hub", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**About the Innovation Hub:**")
            st.write(hub_info['description'])
            
            st.write()
            st.write("**🎯 Programs & Services:**")
            for service in hub_info['services']:
                st.write(f"• {service}")
                
            if hub_info.get('special_programs'):
                st.write()
                st.write("**⭐ Special Programs:**")
                for program in hub_info['special_programs']:
                    st.write(f"• **{program['name']}**: {program['description']}")
        
        with col2:
            with st.container(border=True):
                st.write("**📍 Contact Information**")
                st.write(f"**Email:** {hub_info['email']}")
                if hub_info.get('website'):
                    st.write(f"**Website:** [{hub_info['website']}]({hub_info['website']})")

def render_jobs():
    """Render JOBSs expandable section"""
    jobs_info = get_jobs_info()
    
    with st.expander("📄 JOBSs", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**About JOBSs:**")
            st.write(jobs_info['description'])
        
        with col2:
            with st.container(border=True):
                st.write("**📍 Contact Information**")
                st.write(f"**Website:** [{jobs_info['website']}]({jobs_info['website']})")

def render_ocpd():
    """Render Office of Career & Professional Development expandable section"""
    ocpd_info = get_ocpd_info()
    
    with st.expander("💼 Office of Career & Professional Development (OCPD)", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**About the Office of Career & Professional Development:**")
            st.write(ocpd_info['description'])
            
            st.write("**🎯 Career Services:**")
            for service in ocpd_info['career_services']:
                st.write(f"• {service}")
        
        with col2:
            with st.container(border=True):
                st.write("**📍 Contact Information**")
                st.write(f"**Email:** {ocpd_info['email']}")
                if ocpd_info.get('website'):
                    st.write(f"**Website:** [{ocpd_info['website']}]({ocpd_info['website']})")

def render_stem_centers():
    """Render STEM Centers and Offices expandable section"""
    stem_info = get_stem_centers_info()
    
    with st.expander("🧬 STEM Centers and Offices", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**About the STEM Center:**")
            st.write(stem_info['stem_center']['description'])
            
            st.write("**🎯 Services & Programs:**")
            for service in stem_info['stem_center']['services']:
                st.write(f"• {service}")
            
            # if stem_info['stem_center'].get('research_opportunities'):
            #     st.write("**🔬 Research Opportunities:**")
            #     for opportunity in stem_info['stem_center']['research_opportunities']:
            #         st.write(f"🧪 {opportunity}")
        
        with col2:
            with st.container(border=True):
                st.write("**📍 Contact Information**")
                contact = stem_info['stem_center']['contact']
                st.write(f"**Email:** {contact['email']}")
                st.write(f"**Website:** {contact['website']}")
        
        # st.divider()
        
        # # Other STEM Offices
        # st.subheader("🏢 Related STEM Offices")
        
        # offices = stem_info.get('other_offices', [])
        # for i, office in enumerate(offices):
        #     col1, col2 = st.columns([3, 1])
            
        #     with col1:
        #         st.write(f"**{office['name']}**")
        #         st.write(office['description'])
                
        #         if office.get('services'):
        #             st.write("*Services:*")
        #             for service in office['services']:
        #                 st.write(f"  • {service}")
            
        #     with col2:
        #         st.write(f"📍 {office['location']}")
        #         if office.get('phone'):
        #             st.write(f"📞 {office['phone']}")
        #         if office.get('email'):
        #             st.write(f"✉️ {office['email']}")
                
        #         if st.button(f"Contact {office['name'].split()[0]}", key=f"stem_office_{i}", use_container_width=True):
        #             track_resource_interaction(office['name'], "contact_requested")
        #             st.info(f"Reach out to {office['name']} for specialized assistance!")
            
        #     if i < len(offices) - 1:
        #         st.divider()

def main():
    """Main function to render the resources page"""
    # Configure page and initialize session
    configure_page()
    initialize_resources_session()
    
    # Render page components
    render_header()
    render_innovation_hub()
    render_jobs()
    render_ocpd()
    render_stem_centers()

if __name__ == "__main__":
    main()