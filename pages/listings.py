# TATIANA
# listings.py

# import streamlit as st
# from datetime import datetime
# from utils.listings_utils import (
#     filter_listings,
#     save_listing_to_firebase,
#     get_all_listings_from_firebase,
#     get_user_listings_from_firebase,
#     delete_listing_from_firebase,
#     update_listing_in_firebase
# )
# from utils.profile_utils import get_user_profile
# from utils.general_utils import (
#     auth_gate, get_current_user, configure_page,
#     render_scsu_logo, render_sidebar_auth
# )

# FACULTY_NAMES = [
#     "Amal Abed El-Raouf",
#     "Hao Wu",
#     "Imad Antonios",
#     "Lisa Lancor",
#     "Md Shafaeat Hossain",
#     "Mohammad Islam",
#     "Sahar Al Seesi",
#     "Winnie Yu"
# ]

# SKILLS_OPTIONS = [
#     "Python",
#     "Java",
#     "C++",
#     "SQL",
#     "Web Development (HTML, CSS, JavaScript)",
#     "Data Science",
#     "Artificial Intelligence/Machine Learning",
#     "Data Visualization",
#     "Software Development",
#     "Cloud Computing (AWS, Azure, GCP)",
#     "Database Design and Management",
#     "Research Methods / Experimental Design"
# ]

# # Configure page FIRST
# configure_page(
#     title="Research Opportunities 🔍",
#     icon="🔍",
#     layout="wide"
# )

# # Auth gate
# auth_gate()

# # Get user info
# user_info = get_current_user()

# # Sidebar
# render_scsu_logo()
# with st.sidebar:
#     render_sidebar_auth(show_role=True)
#     st.divider()

# def render_sidebar_filters():
#     """Render sidebar filters for refining research opportunity listings."""
#     st.sidebar.title("Filters")
#     with st.sidebar.expander("Hours per Week", expanded=False):
#         hours_filter = st.radio("", ["All", "0 to 5", "6 to 10", "10+"], index=0, key="hours_filter")
#     with st.sidebar.expander("Compensation Type", expanded=False):
#         compensation_filter = st.radio("", ["All", "Paid", "Unpaid"], index=0, key="comp_filter")
#     with st.sidebar.expander("Faculty", expanded=False):
#         faculty_filter = st.radio("", options=["All"] + FACULTY_NAMES, index=0, key="faculty_filter")
#     return hours_filter, compensation_filter, faculty_filter

# def render_edit_form(listing, listing_id, form_key_prefix):
#     """Render the edit form for a listing.
    
#     Args:
#         listing: The listing data dictionary
#         listing_id: The unique listing ID
#         form_key_prefix: Prefix for form keys to ensure uniqueness
#     """
#     st.subheader(f"Editing: {listing['title']}")
    
#     with st.form(key=f"edit_form_{form_key_prefix}_{listing_id}"):
#         title = st.text_input("Project Title *", value=listing['title'], key=f"edit_title_{form_key_prefix}_{listing_id}")
#         team = st.text_input("Additional Collaborators", value=listing.get('team', 'n/a') if listing.get('team') != 'n/a' else "", key=f"edit_team_{form_key_prefix}_{listing_id}")
        
#         dept_index = 0 if listing['department'] == "Computer Science" else 1
#         department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=dept_index, key=f"edit_dept_{form_key_prefix}_{listing_id}")
        
#         openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=listing['openings'], step=1, key=f"edit_openings_{form_key_prefix}_{listing_id}")
        
#         # Parse start date
#         try:
#             start_date_obj = datetime.strptime(listing['start_date'], "%B %d, %Y")
#         except:
#             start_date_obj = datetime.now()
#         start_date = st.date_input("Start Date *", value=start_date_obj, key=f"edit_start_date_{form_key_prefix}_{listing_id}")
#         st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
        
#         duration_options = ["1 semester", "2 semesters", "More than 2 semesters"]
#         duration_index = duration_options.index(listing['duration']) if listing['duration'] in duration_options else 0
#         duration = st.selectbox("Duration *", options=duration_options, index=duration_index, key=f"edit_duration_{form_key_prefix}_{listing_id}")
        
#         weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=listing['weekly_hours'], step=1, key=f"edit_hours_{form_key_prefix}_{listing_id}")
        
#         comp_index = 0 if listing['compensation_type'] == "paid" else 1
#         compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=comp_index, key=f"edit_comp_type_{form_key_prefix}_{listing_id}")
        
#         pay_rate = None
#         if compensation_type == "Paid":
#             pay_rate = st.number_input(
#                 "Hourly Pay Rate ($) *",
#                 min_value=0.0,
#                 value=float(listing.get('pay_rate', 0)),
#                 step=0.01,
#                 format="%.2f",
#                 key=f"edit_pay_rate_{form_key_prefix}_{listing_id}"
#             )
        
#         st.write("Skills Required *")
#         current_skills = [s.strip() for s in listing['skills'].split(',')] if listing['skills'] else []
#         skills = st.multiselect(
#             "Select skills",
#             options=SKILLS_OPTIONS,
#             default=[s for s in current_skills if s in SKILLS_OPTIONS],
#             placeholder="Select all that apply",
#             label_visibility="collapsed",
#             key=f"edit_skills_{form_key_prefix}_{listing_id}"
#         )
        
#         website_urls = st.text_input("Website URL(s)", value=listing.get('website_urls', '') if listing.get('website_urls') != 'n/a' else "", key=f"edit_website_{form_key_prefix}_{listing_id}")
#         summary = st.text_area("Summary/Description *", value=listing['summary'], key=f"edit_summary_{form_key_prefix}_{listing_id}")
        
#         st.write("Preferred Method of Communication *")
#         current_comm = [c.strip() for c in listing.get('communication', '').split(',')] if listing.get('communication') else []
#         communication = st.multiselect(
#             "Select communication methods",
#             options=["Email", "Teams"],
#             default=[c for c in current_comm if c in ["Email", "Teams"]],
#             placeholder="Select all that apply",
#             label_visibility="collapsed",
#             key=f"edit_comm_{form_key_prefix}_{listing_id}"
#         )
        
#         col1, col2 = st.columns(2)
#         with col1:
#             save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
#         with col2:
#             cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
#         if cancel_button:
#             st.session_state.editing_listing = None
#             st.rerun()
        
#         if save_button:
#             errors = []
#             if not title.strip():
#                 errors.append("Project Title")
#             if not department:
#                 errors.append("Department/Lab")
#             if openings < 1:
#                 errors.append("Number of Openings")
#             if not start_date:
#                 errors.append("Start Date")
#             if not duration:
#                 errors.append("Duration")
#             if weekly_hours < 1:
#                 errors.append("Number of Hours per Week")
#             if not compensation_type:
#                 errors.append("Compensation Type")
#             if compensation_type == "Paid" and (pay_rate is None or pay_rate <= 0):
#                 errors.append("Hourly Pay Rate")
#             if not skills:
#                 errors.append("Skills Required")
#             if not summary.strip():
#                 errors.append("Summary/Description")
#             if not communication:
#                 errors.append("Preferred Method of Communication")
            
#             if errors:
#                 st.error(f"Please fill out the following required fields: {', '.join(errors)}")
#             else:
#                 start_date_formatted = start_date.strftime("%B %d, %Y")
#                 skills_str = ", ".join(skills)
#                 communication_str = ", ".join(communication)
                
#                 updated_listing = {
#                     "title": title,
#                     "team": team if team else "n/a",
#                     "department": department,
#                     "skills": skills_str,
#                     "openings": openings,
#                     "start_date": start_date_formatted,
#                     "duration": duration,
#                     "pay_rate": pay_rate if compensation_type == "Paid" else 0,
#                     "weekly_hours": weekly_hours,
#                     "summary": summary,
#                     "compensation_type": compensation_type.lower(),
#                     "website_urls": website_urls if website_urls else "n/a",
#                     "communication": communication_str,
#                 }
                
#                 try:
#                     update_listing_in_firebase(listing_id, updated_listing)
#                     st.success(f"✅ Listing '{title}' has been updated successfully!")
#                     st.session_state.editing_listing = None
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Failed to update listing: {e}")

# def render_listings(listings, show_edit=False, show_delete=False, user_info=None, tab_prefix="browse"):
#     """Display a list of research opportunity listings in a structured and readable format.
    
#     Args:
#         listings: List of listing dictionaries to display
#         show_edit: Whether to show edit buttons
#         show_delete: Whether to show delete buttons (admin only in Browse tab)
#         user_info: Current user information for permission checks
#         tab_prefix: Prefix for session state keys to avoid conflicts between tabs
#     """
#     col1, col2, col3 = st.columns([1, 3, 1])
#     with col2:
#         for idx, listing in enumerate(listings):
#             listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
#             container_key = f"{tab_prefix}_listing_container_{listing_id}_{idx}"
            
#             # Check if this listing is being edited
#             is_editing = (st.session_state.get("editing_listing") == listing_id and 
#                          st.session_state.get("editing_tab") == tab_prefix)
            
#             with st.container(key=container_key, border=True):
#                 if is_editing:
#                     render_edit_form(listing, listing_id, tab_prefix)
#                 else:
#                     st.subheader(listing["title"])
#                     st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
#                     st.write(f"**Additional Collaborators:** {listing['team']}")
#                     st.write(f"**Department/Lab:** {listing['department']}")
#                     st.write(f"**Number of Openings:** {listing['openings']}")
#                     st.write(f"**Start Date:** {listing['start_date']}")
#                     st.write(f"**Duration:** {listing['duration']}")
#                     st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
#                     st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
#                     st.write(f"**Skills Required:** {listing['skills']}")
#                     if "website_urls" in listing and listing["website_urls"] != "n/a":
#                         st.write(f"**Website URL(s):** {listing['website_urls']}")
#                     st.write(f"**Summary/Description:** {listing['summary']}")
#                     if "communication" in listing and listing["communication"]:
#                         st.write(f"**Preferred Method of Communication:** {listing['communication']}")
#                     st.write("")
                    
#                     # Initialize session state for confirmation if not present
#                     delete_confirm_key = f"delete_confirm_{tab_prefix}"
#                     if delete_confirm_key not in st.session_state:
#                         st.session_state[delete_confirm_key] = {}
                    
#                     # Check if delete confirmation is active for this listing
#                     if st.session_state[delete_confirm_key].get(listing_id):
#                         # Show full-width delete confirmation
#                         st.warning(f"Are you sure you want to delete **{listing['title']}**?")
#                         col_yes, col_no = st.columns([1, 1])
#                         with col_yes:
#                             if st.button("🗑️ Confirm Delete", key=f"confirm_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
#                                 try:
#                                     delete_listing_from_firebase(listing.get("listing_id"))
#                                     st.success(f"'{listing['title']}' has been deleted.")
#                                     st.session_state[delete_confirm_key][listing_id] = False
#                                     st.rerun()
#                                 except Exception as e:
#                                     st.error(f"Failed to delete listing: {e}")
#                         with col_no:
#                             if st.button("❌ Cancel", key=f"cancel_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
#                                 st.session_state[delete_confirm_key][listing_id] = False
#                                 st.rerun()
#                     else:
#                         # Action buttons row - keeping original narrow width
#                         button_cols = st.columns([1, 1, 4])
                        
#                         # Edit button
#                         if show_edit:
#                             with button_cols[0]:
#                                 if st.button("✏️ Edit", key=f"edit_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
#                                     st.session_state.editing_listing = listing_id
#                                     st.session_state.editing_tab = tab_prefix
#                                     st.rerun()
                        
#                         # Delete button
#                         if show_delete:
#                             with button_cols[1]:
#                                 if st.button("🗑️ Delete", key=f"delete_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
#                                     st.session_state[delete_confirm_key][listing_id] = True
#                                     st.rerun()

# def main():
#     """Main entry point for the Research Opportunities page."""
#     st.title("Research Opportunities 🔍")

#     if user_info['role'] in ("faculty", "admin"):
#         tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "My Listings"])
#     else:
#         tab1, = st.tabs(["Browse Listings"])

#     # Browse Listings
#     with tab1:
#         hours_filter, compensation_filter, faculty_filter = render_sidebar_filters()
#         listings = get_all_listings_from_firebase()[::-1]  # Firebase only
#         filtered_listings = filter_listings(listings, hours_filter, compensation_filter, faculty_filter)
        
#         # Show admin edit/delete capability notice
#         if user_info['role'] == "admin":
#             st.info("👑 **Admin View:** You can edit or delete any listing from this tab.")
        
#         if filtered_listings:
#             # Pass show_edit and show_delete=True only for admins
#             render_listings(
#                 filtered_listings, 
#                 show_edit=(user_info['role'] == "admin"),
#                 show_delete=(user_info['role'] == "admin"), 
#                 user_info=user_info,
#                 tab_prefix="browse"
#             )
#         else:
#             st.info("No listings match your filters.")

#     # Create Listing
#     if user_info['role'] in ("faculty", "admin"):
#         with tab2:
#             st.header("Create a New Research Listing")

#             if "form_counter" not in st.session_state:
#                 st.session_state.form_counter = 0

#             col1, col2, col3 = st.columns([1, 3, 1])
#             with col2:
#                 if st.session_state.get("listing_created", False):
#                     st.success(f"Listing '{st.session_state.listing_title}' successfully created!")
#                     st.session_state.listing_created = False

#                 with st.container(border=True):
#                     form_key = st.session_state.form_counter
#                     title = st.text_input("Project Title *", value="", placeholder="ex. Biometric Authentication in Smartphones", key=f"title_input_{form_key}")
#                     team = st.text_input("Additional Collaborators", value="", placeholder="ex. Grace Hopper, John von Neumann", key=f"team_input_{form_key}")
#                     department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=0, key=f"dept_input_{form_key}")
#                     openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=1, step=1, key=f"openings_input_{form_key}")
#                     start_date = st.date_input("Start Date *", key=f"start_date_input_{form_key}")
#                     st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
#                     duration = st.selectbox("Duration *", options=["1 semester", "2 semesters", "More than 2 semesters"], index=0, key=f"duration_input_{form_key}")
#                     weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=1, step=1, key=f"hours_input_{form_key}")

#                     compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=None, key=f"comp_type_{form_key}")
#                     if compensation_type == "Paid":
#                         pay_rate = st.number_input(
#                             "Hourly Pay Rate ($) *",
#                             min_value=0.0,
#                             step=0.01,
#                             format="%.2f",
#                             key=f"pay_rate_input_{form_key}"
#                         )

#                     st.write("Skills Required *")
#                     skills = st.multiselect(
#                         "Select skills",
#                         options=SKILLS_OPTIONS,
#                         default=None,
#                         placeholder="Select all that apply",
#                         label_visibility="collapsed",
#                         key=f"skills_input_{form_key}"
#                     )

#                     website_urls = st.text_input("Website URL(s)", value="", placeholder="ex. https://example.com", key=f"website_input_{form_key}")
#                     summary = st.text_area("Summary/Description *", value="", key=f"summary_input_{form_key}")
                    
#                     st.write("Preferred Method of Communication *")
#                     communication = st.multiselect(
#                         "Select communication methods",
#                         options=["Email", "Teams"],
#                         default=None,
#                         placeholder="Select all that apply",
#                         label_visibility="collapsed",
#                         key=f"comm_input_{form_key}"
#                     )

#                     submitted = st.button("Post Listing")
#                     if submitted:
#                         errors = []
#                         if not title.strip():
#                             errors.append("Project Title")
#                         if not department:
#                             errors.append("Department/Lab")
#                         if openings < 1:
#                             errors.append("Number of Openings")
#                         if not start_date:
#                             errors.append("Start Date")
#                         if not duration:
#                             errors.append("Duration")
#                         if weekly_hours < 1:
#                             errors.append("Number of Hours per Week")
#                         if not compensation_type:
#                             errors.append("Compensation Type")
#                         if compensation_type == "Paid" and (not 'pay_rate' in locals() or pay_rate <= 0):
#                             errors.append("Hourly Pay Rate")
#                         if not skills:
#                             errors.append("Skills Required")
#                         if not summary.strip():
#                             errors.append("Summary/Description")
#                         if not communication:
#                             errors.append("Preferred Method of Communication")

#                         if errors:
#                             st.error(f"Please fill out the following required fields: {', '.join(errors)}")
#                         else:
#                             date_posted_formatted = datetime.now().strftime("%B %d, %Y")
#                             profile_data = get_user_profile(user_info['uid'])
#                             posted_by = profile_data.get('name', 'Unknown') if profile_data else 'Unknown'
#                             start_date_formatted = start_date.strftime("%B %d, %Y")
#                             skills_str = ", ".join(skills)
#                             communication_str = ", ".join(communication)

#                             new_listing = {
#                                 "title": title,
#                                 "pi": posted_by,
#                                 "team": team if team else "n/a",
#                                 "department": department,
#                                 "skills": skills_str,
#                                 "openings": openings,
#                                 "start_date": start_date_formatted,
#                                 "duration": duration,
#                                 "pay_rate": pay_rate if compensation_type == "Paid" else 0,
#                                 "weekly_hours": weekly_hours,
#                                 "summary": summary,
#                                 "date_posted": date_posted_formatted,
#                                 "compensation_type": compensation_type.lower(),
#                                 "website_urls": website_urls if website_urls else "n/a",
#                                 "communication": communication_str,
#                                 "posted_by_uid": user_info['uid']
#                             }

#                             try:
#                                 listing_id = save_listing_to_firebase(new_listing)
#                                 st.session_state.listing_created = True
#                                 st.session_state.listing_title = title
#                                 st.session_state.listing_posted_by = posted_by
#                                 st.session_state.listing_date = date_posted_formatted
#                                 st.session_state.form_counter += 1
#                                 st.rerun()
#                             except Exception as e:
#                                 st.error(f"Failed to create listing: {e}")

#         # My Listings
#         with tab3:
#             st.header("My Listings")
            
#             # Both admins and faculty see only their own listings here
#             my_listings = get_user_listings_from_firebase(user_info['uid'])
            
#             if my_listings:
#                 col1, col2, col3 = st.columns([1, 3, 1])
#                 with col2:
#                     for idx, listing in enumerate(my_listings[::-1]):
#                         listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
#                         container_key = f"my_listing_container_{listing_id}"
                        
#                         # Check if this listing is being edited
#                         is_editing = (st.session_state.get("editing_listing") == listing_id and 
#                                      st.session_state.get("editing_tab") == "my")

#                         with st.container(key=container_key, border=True):
#                             if is_editing:
#                                 render_edit_form(listing, listing_id, "my")
#                             else:
#                                 st.subheader(listing["title"])
#                                 st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
#                                 st.write(f"**Additional Collaborators:** {listing['team']}")
#                                 st.write(f"**Department/Lab:** {listing['department']}")
#                                 st.write(f"**Number of Openings:** {listing['openings']}")
#                                 st.write(f"**Start Date:** {listing['start_date']}")
#                                 st.write(f"**Duration:** {listing['duration']}")
#                                 st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
#                                 st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
#                                 st.write(f"**Skills Required:** {listing['skills']}")
#                                 if "website_urls" in listing and listing["website_urls"] != "n/a":
#                                     st.write(f"**Website URL(s):** {listing['website_urls']}")
#                                 st.write(f"**Summary/Description:** {listing['summary']}")
#                                 if "communication" in listing and listing["communication"]:
#                                     st.write(f"**Preferred Method of Communication:** {listing['communication']}")
#                                 st.write("")

#                                 # Initialize session state for confirmation if not present
#                                 if "delete_confirm_my" not in st.session_state:
#                                     st.session_state.delete_confirm_my = {}

#                                 # Check if delete confirmation is active for this listing
#                                 if st.session_state.delete_confirm_my.get(listing_id):
#                                     # Show full-width delete confirmation
#                                     st.warning(f"Are you sure you want to delete **{listing['title']}**?")
#                                     col_yes, col_no = st.columns([1, 1])
#                                     with col_yes:
#                                         if st.button("🗑️ Confirm Delete", key=f"confirm_my_{listing_id}", use_container_width=True):
#                                             try:
#                                                 delete_listing_from_firebase(listing.get("listing_id"))
#                                                 st.success(f"'{listing['title']}' has been deleted.")
#                                                 st.session_state.delete_confirm_my[listing_id] = False
#                                                 st.rerun()
#                                             except Exception as e:
#                                                 st.error(f"Failed to delete listing: {e}")
#                                     with col_no:
#                                         if st.button("❌ Cancel", key=f"cancel_my_{listing_id}", use_container_width=True):
#                                             st.session_state.delete_confirm_my[listing_id] = False
#                                             st.rerun()
#                                 else:
#                                     # Action buttons row - keeping original narrow width
#                                     button_cols = st.columns([1, 1, 4])
                                    
#                                     # Edit button
#                                     with button_cols[0]:
#                                         if st.button("✏️ Edit", key=f"edit_my_{listing_id}", use_container_width=True):
#                                             st.session_state.editing_listing = listing_id
#                                             st.session_state.editing_tab = "my"
#                                             st.rerun()
                                    
#                                     # Delete button
#                                     with button_cols[1]:
#                                         if st.button("🗑️ Delete", key=f"delete_my_{listing_id}", use_container_width=True):
#                                             st.session_state.delete_confirm_my[listing_id] = True
#                                             st.rerun()
#             else:
#                 st.info("You haven't created any listings yet.")

# if __name__ == "__main__":
#     main()

# #-----END OF FILE-----

# TATIANA
# listings.py
# favorite/unfavorite functionality works

# import streamlit as st
# from datetime import datetime
# from utils.listings_utils import (
#     filter_listings,
#     save_listing_to_firebase,
#     get_all_listings_from_firebase,
#     get_user_listings_from_firebase,
#     delete_listing_from_firebase,
#     update_listing_in_firebase,
#     toggle_favorite_listing,
#     get_user_favorite_listings
# )
# from utils.profile_utils import get_user_profile
# from utils.general_utils import (
#     auth_gate, get_current_user, configure_page,
#     render_scsu_logo, render_sidebar_auth
# )

# FACULTY_NAMES = [
#     "Amal Abed El-Raouf",
#     "Hao Wu",
#     "Imad Antonios",
#     "Lisa Lancor",
#     "Md Shafaeat Hossain",
#     "Mohammad Islam",
#     "Sahar Al Seesi",
#     "Winnie Yu"
# ]

# SKILLS_OPTIONS = [
#     "Python",
#     "Java",
#     "C++",
#     "SQL",
#     "Web Development (HTML, CSS, JavaScript)",
#     "Data Science",
#     "Artificial Intelligence/Machine Learning",
#     "Data Visualization",
#     "Software Development",
#     "Cloud Computing (AWS, Azure, GCP)",
#     "Database Design and Management",
#     "Research Methods / Experimental Design"
# ]

# # Configure page FIRST
# configure_page(
#     title="Research Opportunities 🔍",
#     icon="🔍",
#     layout="wide"
# )

# # Auth gate
# auth_gate()

# # Get user info
# user_info = get_current_user()

# # Sidebar
# render_scsu_logo()
# with st.sidebar:
#     render_sidebar_auth(show_role=True)
#     st.divider()

# def render_sidebar_filters():
#     """Render sidebar filters for refining research opportunity listings."""
#     st.sidebar.title("Filters")
#     with st.sidebar.expander("Hours per Week", expanded=False):
#         hours_filter = st.radio("", ["All", "0 to 5", "6 to 10", "10+"], index=0, key="hours_filter")
#     with st.sidebar.expander("Compensation Type", expanded=False):
#         compensation_filter = st.radio("", ["All", "Paid", "Unpaid"], index=0, key="comp_filter")
#     with st.sidebar.expander("Faculty", expanded=False):
#         faculty_filter = st.radio("", options=["All"] + FACULTY_NAMES, index=0, key="faculty_filter")
#     return hours_filter, compensation_filter, faculty_filter

# def render_edit_form(listing, listing_id, form_key_prefix):
#     """Render the edit form for a listing.
    
#     Args:
#         listing: The listing data dictionary
#         listing_id: The unique listing ID
#         form_key_prefix: Prefix for form keys to ensure uniqueness
#     """
#     st.subheader(f"Editing: {listing['title']}")
    
#     with st.form(key=f"edit_form_{form_key_prefix}_{listing_id}"):
#         title = st.text_input("Project Title *", value=listing['title'], key=f"edit_title_{form_key_prefix}_{listing_id}")
#         team = st.text_input("Additional Collaborators", value=listing.get('team', 'n/a') if listing.get('team') != 'n/a' else "", key=f"edit_team_{form_key_prefix}_{listing_id}")
        
#         dept_index = 0 if listing['department'] == "Computer Science" else 1
#         department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=dept_index, key=f"edit_dept_{form_key_prefix}_{listing_id}")
        
#         openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=listing['openings'], step=1, key=f"edit_openings_{form_key_prefix}_{listing_id}")
        
#         # Parse start date
#         try:
#             start_date_obj = datetime.strptime(listing['start_date'], "%B %d, %Y")
#         except:
#             start_date_obj = datetime.now()
#         start_date = st.date_input("Start Date *", value=start_date_obj, key=f"edit_start_date_{form_key_prefix}_{listing_id}")
#         st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
        
#         duration_options = ["1 semester", "2 semesters", "More than 2 semesters"]
#         duration_index = duration_options.index(listing['duration']) if listing['duration'] in duration_options else 0
#         duration = st.selectbox("Duration *", options=duration_options, index=duration_index, key=f"edit_duration_{form_key_prefix}_{listing_id}")
        
#         weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=listing['weekly_hours'], step=1, key=f"edit_hours_{form_key_prefix}_{listing_id}")
        
#         comp_index = 0 if listing['compensation_type'] == "paid" else 1
#         compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=comp_index, key=f"edit_comp_type_{form_key_prefix}_{listing_id}")
        
#         pay_rate = None
#         if compensation_type == "Paid":
#             pay_rate = st.number_input(
#                 "Hourly Pay Rate ($) *",
#                 min_value=0.0,
#                 value=float(listing.get('pay_rate', 0)),
#                 step=0.01,
#                 format="%.2f",
#                 key=f"edit_pay_rate_{form_key_prefix}_{listing_id}"
#             )
        
#         st.write("Skills Required *")
#         current_skills = [s.strip() for s in listing['skills'].split(',')] if listing['skills'] else []
#         skills = st.multiselect(
#             "Select skills",
#             options=SKILLS_OPTIONS,
#             default=[s for s in current_skills if s in SKILLS_OPTIONS],
#             placeholder="Select all that apply",
#             label_visibility="collapsed",
#             key=f"edit_skills_{form_key_prefix}_{listing_id}"
#         )
        
#         website_urls = st.text_input("Website URL(s)", value=listing.get('website_urls', '') if listing.get('website_urls') != 'n/a' else "", key=f"edit_website_{form_key_prefix}_{listing_id}")
#         summary = st.text_area("Summary/Description *", value=listing['summary'], key=f"edit_summary_{form_key_prefix}_{listing_id}")
        
#         st.write("Preferred Method of Communication *")
#         current_comm = [c.strip() for c in listing.get('communication', '').split(',')] if listing.get('communication') else []
#         communication = st.multiselect(
#             "Select communication methods",
#             options=["Email", "Teams"],
#             default=[c for c in current_comm if c in ["Email", "Teams"]],
#             placeholder="Select all that apply",
#             label_visibility="collapsed",
#             key=f"edit_comm_{form_key_prefix}_{listing_id}"
#         )
        
#         col1, col2 = st.columns(2)
#         with col1:
#             save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
#         with col2:
#             cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
#         if cancel_button:
#             st.session_state.editing_listing = None
#             st.rerun()
        
#         if save_button:
#             errors = []
#             if not title.strip():
#                 errors.append("Project Title")
#             if not department:
#                 errors.append("Department/Lab")
#             if openings < 1:
#                 errors.append("Number of Openings")
#             if not start_date:
#                 errors.append("Start Date")
#             if not duration:
#                 errors.append("Duration")
#             if weekly_hours < 1:
#                 errors.append("Number of Hours per Week")
#             if not compensation_type:
#                 errors.append("Compensation Type")
#             if compensation_type == "Paid" and (pay_rate is None or pay_rate <= 0):
#                 errors.append("Hourly Pay Rate")
#             if not skills:
#                 errors.append("Skills Required")
#             if not summary.strip():
#                 errors.append("Summary/Description")
#             if not communication:
#                 errors.append("Preferred Method of Communication")
            
#             if errors:
#                 st.error(f"Please fill out the following required fields: {', '.join(errors)}")
#             else:
#                 start_date_formatted = start_date.strftime("%B %d, %Y")
#                 skills_str = ", ".join(skills)
#                 communication_str = ", ".join(communication)
                
#                 updated_listing = {
#                     "title": title,
#                     "team": team if team else "n/a",
#                     "department": department,
#                     "skills": skills_str,
#                     "openings": openings,
#                     "start_date": start_date_formatted,
#                     "duration": duration,
#                     "pay_rate": pay_rate if compensation_type == "Paid" else 0,
#                     "weekly_hours": weekly_hours,
#                     "summary": summary,
#                     "compensation_type": compensation_type.lower(),
#                     "website_urls": website_urls if website_urls else "n/a",
#                     "communication": communication_str,
#                 }
                
#                 try:
#                     update_listing_in_firebase(listing_id, updated_listing)
#                     st.success(f"✅ Listing '{title}' has been updated successfully!")
#                     st.session_state.editing_listing = None
#                     st.rerun()
#                 except Exception as e:
#                     st.error(f"Failed to update listing: {e}")

# def render_listings(listings, show_edit=False, show_delete=False, show_favorite=False, user_info=None, tab_prefix="browse"):
#     """Display a list of research opportunity listings in a structured and readable format.
    
#     Args:
#         listings: List of listing dictionaries to display
#         show_edit: Whether to show edit buttons
#         show_delete: Whether to show delete buttons (admin only in Browse tab)
#         show_favorite: Whether to show favorite/star button
#         user_info: Current user information for permission checks
#         tab_prefix: Prefix for session state keys to avoid conflicts between tabs
#     """
#     # Get user's favorited listings if showing favorites
#     favorited_listing_ids = set()
#     if show_favorite and user_info:
#         favorited_listing_ids = set(get_user_favorite_listings(user_info['uid'], user_info.get('idToken')))
    
#     col1, col2, col3 = st.columns([1, 3, 1])
#     with col2:
#         for idx, listing in enumerate(listings):
#             listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
#             container_key = f"{tab_prefix}_listing_container_{listing_id}_{idx}"
            
#             # Check if this listing is being edited
#             is_editing = (st.session_state.get("editing_listing") == listing_id and 
#                          st.session_state.get("editing_tab") == tab_prefix)
            
#             with st.container(key=container_key, border=True):
#                 if is_editing:
#                     render_edit_form(listing, listing_id, tab_prefix)
#                 else:
#                     # Header row with title and favorite button
#                     if show_favorite:
#                         header_cols = st.columns([5, 1])
#                         with header_cols[0]:
#                             st.subheader(listing["title"])
#                         with header_cols[1]:
#                             is_favorited = listing_id in favorited_listing_ids
#                             star_icon = "⭐" if is_favorited else "☆"
#                             star_label = "Unfavorite" if is_favorited else "Favorite"
#                             if st.button(star_icon, key=f"fav_{tab_prefix}_{listing_id}_{idx}", help=star_label, use_container_width=True):
#                                 try:
#                                     toggle_favorite_listing(user_info['uid'], listing_id, user_info.get('idToken'))
#                                     st.rerun()
#                                 except Exception as e:
#                                     st.error(f"Failed to update favorite: {e}")
#                     else:
#                         st.subheader(listing["title"])
                    
#                     st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
#                     st.write(f"**Additional Collaborators:** {listing['team']}")
#                     st.write(f"**Department/Lab:** {listing['department']}")
#                     st.write(f"**Number of Openings:** {listing['openings']}")
#                     st.write(f"**Start Date:** {listing['start_date']}")
#                     st.write(f"**Duration:** {listing['duration']}")
#                     st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
#                     st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
#                     st.write(f"**Skills Required:** {listing['skills']}")
#                     if "website_urls" in listing and listing["website_urls"] != "n/a":
#                         st.write(f"**Website URL(s):** {listing['website_urls']}")
#                     st.write(f"**Summary/Description:** {listing['summary']}")
#                     if "communication" in listing and listing["communication"]:
#                         st.write(f"**Preferred Method of Communication:** {listing['communication']}")
#                     st.write("")
                    
#                     # Initialize session state for confirmation if not present
#                     delete_confirm_key = f"delete_confirm_{tab_prefix}"
#                     if delete_confirm_key not in st.session_state:
#                         st.session_state[delete_confirm_key] = {}
                    
#                     # Check if delete confirmation is active for this listing
#                     if st.session_state[delete_confirm_key].get(listing_id):
#                         # Show full-width delete confirmation
#                         st.warning(f"Are you sure you want to delete **{listing['title']}**?")
#                         col_yes, col_no = st.columns([1, 1])
#                         with col_yes:
#                             if st.button("🗑️ Confirm Delete", key=f"confirm_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
#                                 try:
#                                     delete_listing_from_firebase(listing.get("listing_id"))
#                                     st.success(f"'{listing['title']}' has been deleted.")
#                                     st.session_state[delete_confirm_key][listing_id] = False
#                                     st.rerun()
#                                 except Exception as e:
#                                     st.error(f"Failed to delete listing: {e}")
#                         with col_no:
#                             if st.button("❌ Cancel", key=f"cancel_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
#                                 st.session_state[delete_confirm_key][listing_id] = False
#                                 st.rerun()
#                     else:
#                         # Action buttons row - keeping original narrow width
#                         button_cols = st.columns([1, 1, 4])
                        
#                         # Edit button
#                         if show_edit:
#                             with button_cols[0]:
#                                 if st.button("✏️ Edit", key=f"edit_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
#                                     st.session_state.editing_listing = listing_id
#                                     st.session_state.editing_tab = tab_prefix
#                                     st.rerun()
                        
#                         # Delete button
#                         if show_delete:
#                             with button_cols[1]:
#                                 if st.button("🗑️ Delete", key=f"delete_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
#                                     st.session_state[delete_confirm_key][listing_id] = True
#                                     st.rerun()

# def main():
#     """Main entry point for the Research Opportunities page."""
#     st.title("Research Opportunities 🔍")

#     # Show tabs based on role
#     if user_info['role'] in ("faculty", "admin"):
#         tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "My Listings"])
#     else:
#         # Students see Browse and My Listings (for favorites)
#         tab1, tab3 = st.tabs(["Browse Listings", "My Listings"])
#         tab2 = None  # No create tab for students

#     # Browse Listings
#     with tab1:
#         hours_filter, compensation_filter, faculty_filter = render_sidebar_filters()
#         listings = get_all_listings_from_firebase()[::-1]  # Firebase only
#         filtered_listings = filter_listings(listings, hours_filter, compensation_filter, faculty_filter)
        
#         # Show admin edit/delete capability notice
#         if user_info['role'] == "admin":
#             st.info("👑 **Admin View:** You can edit or delete any listing from this tab.")
        
#         if filtered_listings:
#             # Students see favorite button, admins see edit/delete
#             render_listings(
#                 filtered_listings, 
#                 show_edit=(user_info['role'] == "admin"),
#                 show_delete=(user_info['role'] == "admin"),
#                 show_favorite=(user_info['role'] == "student"),
#                 user_info=user_info,
#                 tab_prefix="browse"
#             )
#         else:
#             st.info("No listings match your filters.")

#     # Create Listing (faculty/admin only)
#     if user_info['role'] in ("faculty", "admin") and tab2 is not None:
#         with tab2:
#             st.header("Create a New Research Listing")

#             if "form_counter" not in st.session_state:
#                 st.session_state.form_counter = 0

#             col1, col2, col3 = st.columns([1, 3, 1])
#             with col2:
#                 if st.session_state.get("listing_created", False):
#                     st.success(f"Listing '{st.session_state.listing_title}' successfully created!")
#                     st.session_state.listing_created = False

#                 with st.container(border=True):
#                     form_key = st.session_state.form_counter
#                     title = st.text_input("Project Title *", value="", placeholder="ex. Biometric Authentication in Smartphones", key=f"title_input_{form_key}")
#                     team = st.text_input("Additional Collaborators", value="", placeholder="ex. Grace Hopper, John von Neumann", key=f"team_input_{form_key}")
#                     department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=0, key=f"dept_input_{form_key}")
#                     openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=1, step=1, key=f"openings_input_{form_key}")
#                     start_date = st.date_input("Start Date *", key=f"start_date_input_{form_key}")
#                     st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
#                     duration = st.selectbox("Duration *", options=["1 semester", "2 semesters", "More than 2 semesters"], index=0, key=f"duration_input_{form_key}")
#                     weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=1, step=1, key=f"hours_input_{form_key}")

#                     compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=None, key=f"comp_type_{form_key}")
#                     if compensation_type == "Paid":
#                         pay_rate = st.number_input(
#                             "Hourly Pay Rate ($) *",
#                             min_value=0.0,
#                             step=0.01,
#                             format="%.2f",
#                             key=f"pay_rate_input_{form_key}"
#                         )

#                     st.write("Skills Required *")
#                     skills = st.multiselect(
#                         "Select skills",
#                         options=SKILLS_OPTIONS,
#                         default=None,
#                         placeholder="Select all that apply",
#                         label_visibility="collapsed",
#                         key=f"skills_input_{form_key}"
#                     )

#                     website_urls = st.text_input("Website URL(s)", value="", placeholder="ex. https://example.com", key=f"website_input_{form_key}")
#                     summary = st.text_area("Summary/Description *", value="", key=f"summary_input_{form_key}")
                    
#                     st.write("Preferred Method of Communication *")
#                     communication = st.multiselect(
#                         "Select communication methods",
#                         options=["Email", "Teams"],
#                         default=None,
#                         placeholder="Select all that apply",
#                         label_visibility="collapsed",
#                         key=f"comm_input_{form_key}"
#                     )

#                     submitted = st.button("Post Listing")
#                     if submitted:
#                         errors = []
#                         if not title.strip():
#                             errors.append("Project Title")
#                         if not department:
#                             errors.append("Department/Lab")
#                         if openings < 1:
#                             errors.append("Number of Openings")
#                         if not start_date:
#                             errors.append("Start Date")
#                         if not duration:
#                             errors.append("Duration")
#                         if weekly_hours < 1:
#                             errors.append("Number of Hours per Week")
#                         if not compensation_type:
#                             errors.append("Compensation Type")
#                         if compensation_type == "Paid" and (not 'pay_rate' in locals() or pay_rate <= 0):
#                             errors.append("Hourly Pay Rate")
#                         if not skills:
#                             errors.append("Skills Required")
#                         if not summary.strip():
#                             errors.append("Summary/Description")
#                         if not communication:
#                             errors.append("Preferred Method of Communication")

#                         if errors:
#                             st.error(f"Please fill out the following required fields: {', '.join(errors)}")
#                         else:
#                             date_posted_formatted = datetime.now().strftime("%B %d, %Y")
#                             profile_data = get_user_profile(user_info['uid'])
#                             posted_by = profile_data.get('name', 'Unknown') if profile_data else 'Unknown'
#                             start_date_formatted = start_date.strftime("%B %d, %Y")
#                             skills_str = ", ".join(skills)
#                             communication_str = ", ".join(communication)

#                             new_listing = {
#                                 "title": title,
#                                 "pi": posted_by,
#                                 "team": team if team else "n/a",
#                                 "department": department,
#                                 "skills": skills_str,
#                                 "openings": openings,
#                                 "start_date": start_date_formatted,
#                                 "duration": duration,
#                                 "pay_rate": pay_rate if compensation_type == "Paid" else 0,
#                                 "weekly_hours": weekly_hours,
#                                 "summary": summary,
#                                 "date_posted": date_posted_formatted,
#                                 "compensation_type": compensation_type.lower(),
#                                 "website_urls": website_urls if website_urls else "n/a",
#                                 "communication": communication_str,
#                                 "posted_by_uid": user_info['uid']
#                             }

#                             try:
#                                 listing_id = save_listing_to_firebase(new_listing)
#                                 st.session_state.listing_created = True
#                                 st.session_state.listing_title = title
#                                 st.session_state.listing_posted_by = posted_by
#                                 st.session_state.listing_date = date_posted_formatted
#                                 st.session_state.form_counter += 1
#                                 st.rerun()
#                             except Exception as e:
#                                 st.error(f"Failed to create listing: {e}")

#     # My Listings (all users)
#     with tab3:
#         if user_info['role'] == "student":
#             st.header("My Favorite Listings")
            
#             # Get favorited listing IDs
#             favorited_ids = get_user_favorite_listings(user_info['uid'], user_info.get('idToken'))
            
#             if favorited_ids:
#                 # Get all listings and filter to favorites
#                 all_listings = get_all_listings_from_firebase()
#                 favorite_listings = [l for l in all_listings if l.get("listing_id") in favorited_ids]
                
#                 if favorite_listings:
#                     render_listings(
#                         favorite_listings[::-1],
#                         show_edit=False,
#                         show_delete=False,
#                         show_favorite=True,
#                         user_info=user_info,
#                         tab_prefix="favorites"
#                     )
#                 else:
#                     st.info("You haven't favorited any listings yet. Click the ☆ icon on listings in the Browse tab to save them here!")
#             else:
#                 st.info("You haven't favorited any listings yet. Click the ☆ icon on listings in the Browse tab to save them here!")
        
#         else:  # Faculty and admin see their created listings
#             st.header("My Listings")
            
#             # Both admins and faculty see only their own listings here
#             my_listings = get_user_listings_from_firebase(user_info['uid'])
            
#             if my_listings:
#                 col1, col2, col3 = st.columns([1, 3, 1])
#                 with col2:
#                     for idx, listing in enumerate(my_listings[::-1]):
#                         listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
#                         container_key = f"my_listing_container_{listing_id}"
                        
#                         # Check if this listing is being edited
#                         is_editing = (st.session_state.get("editing_listing") == listing_id and 
#                                      st.session_state.get("editing_tab") == "my")

#                         with st.container(key=container_key, border=True):
#                             if is_editing:
#                                 render_edit_form(listing, listing_id, "my")
#                             else:
#                                 st.subheader(listing["title"])
#                                 st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
#                                 st.write(f"**Additional Collaborators:** {listing['team']}")
#                                 st.write(f"**Department/Lab:** {listing['department']}")
#                                 st.write(f"**Number of Openings:** {listing['openings']}")
#                                 st.write(f"**Start Date:** {listing['start_date']}")
#                                 st.write(f"**Duration:** {listing['duration']}")
#                                 st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
#                                 st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
#                                 st.write(f"**Skills Required:** {listing['skills']}")
#                                 if "website_urls" in listing and listing["website_urls"] != "n/a":
#                                     st.write(f"**Website URL(s):** {listing['website_urls']}")
#                                 st.write(f"**Summary/Description:** {listing['summary']}")
#                                 if "communication" in listing and listing["communication"]:
#                                     st.write(f"**Preferred Method of Communication:** {listing['communication']}")
#                                 st.write("")

#                                 # Initialize session state for confirmation if not present
#                                 if "delete_confirm_my" not in st.session_state:
#                                     st.session_state.delete_confirm_my = {}

#                                 # Check if delete confirmation is active for this listing
#                                 if st.session_state.delete_confirm_my.get(listing_id):
#                                     # Show full-width delete confirmation
#                                     st.warning(f"Are you sure you want to delete **{listing['title']}**?")
#                                     col_yes, col_no = st.columns([1, 1])
#                                     with col_yes:
#                                         if st.button("🗑️ Confirm Delete", key=f"confirm_my_{listing_id}", use_container_width=True):
#                                             try:
#                                                 delete_listing_from_firebase(listing.get("listing_id"))
#                                                 st.success(f"'{listing['title']}' has been deleted.")
#                                                 st.session_state.delete_confirm_my[listing_id] = False
#                                                 st.rerun()
#                                             except Exception as e:
#                                                 st.error(f"Failed to delete listing: {e}")
#                                     with col_no:
#                                         if st.button("❌ Cancel", key=f"cancel_my_{listing_id}", use_container_width=True):
#                                             st.session_state.delete_confirm_my[listing_id] = False
#                                             st.rerun()
#                                 else:
#                                     # Action buttons row - keeping original narrow width
#                                     button_cols = st.columns([1, 1, 4])
                                    
#                                     # Edit button
#                                     with button_cols[0]:
#                                         if st.button("✏️ Edit", key=f"edit_my_{listing_id}", use_container_width=True):
#                                             st.session_state.editing_listing = listing_id
#                                             st.session_state.editing_tab = "my"
#                                             st.rerun()
                                    
#                                     # Delete button
#                                     with button_cols[1]:
#                                         if st.button("🗑️ Delete", key=f"delete_my_{listing_id}", use_container_width=True):
#                                             st.session_state.delete_confirm_my[listing_id] = True
#                                             st.rerun()
#             else:
#                 st.info("You haven't created any listings yet.")

# if __name__ == "__main__":
#     main()

# #-----END OF FILE-----

# TATIANA
# listings.py

import streamlit as st
from datetime import datetime
from utils.listings_utils import (
    filter_listings,
    save_listing_to_firebase,
    get_all_listings_from_firebase,
    get_user_listings_from_firebase,
    delete_listing_from_firebase,
    update_listing_in_firebase,
    toggle_favorite_listing,
    get_user_favorite_listings
    update_listing_in_firebase,
    toggle_favorite_listing,
    get_user_favorite_listings
)
from utils.profile_utils import get_user_profile
from utils.general_utils import (
    auth_gate, get_current_user, configure_page,
    render_scsu_logo, render_sidebar_auth
)

FACULTY_NAMES = [
    "Amal Abed El-Raouf",
    "Hao Wu",
    "Imad Antonios",
    "Lisa Lancor",
    "Md Shafaeat Hossain",
    "Mohammad Islam",
    "Sahar Al Seesi",
    "Winnie Yu"
]

SKILLS_OPTIONS = [
    "Python",
    "Java",
    "C++",
    "SQL",
    "Web Development (HTML, CSS, JavaScript)",
    "Data Science",
    "Artificial Intelligence/Machine Learning",
    "Data Visualization",
    "Software Development",
    "Cloud Computing (AWS, Azure, GCP)",
    "Database Design and Management",
    "Research Methods / Experimental Design"
]

# Configure page FIRST
configure_page(
    title="Research Opportunities 🔍",
    icon="🔍",
    layout="wide"
)

# Auth gate
auth_gate()

# Get user info
user_info = get_current_user()

# Sidebar
render_scsu_logo()
with st.sidebar:
    render_sidebar_auth(show_role=True)
    st.divider()

def render_sidebar_filters():
    """Render sidebar filters for refining research opportunity listings."""
    st.sidebar.title("Filters")
    with st.sidebar.expander("Hours per Week", expanded=False):
        hours_filter = st.radio("", ["All", "0 to 5", "6 to 10", "10+"], index=0, key="hours_filter")
    with st.sidebar.expander("Compensation Type", expanded=False):
        compensation_filter = st.radio("", ["All", "Paid", "Unpaid"], index=0, key="comp_filter")
    with st.sidebar.expander("Faculty", expanded=False):
        faculty_filter = st.radio("", options=["All"] + FACULTY_NAMES, index=0, key="faculty_filter")
    return hours_filter, compensation_filter, faculty_filter

def render_edit_form(listing, listing_id, form_key_prefix):
    """Render the edit form for a listing.
    
    Args:
        listing: The listing data dictionary
        listing_id: The unique listing ID
        form_key_prefix: Prefix for form keys to ensure uniqueness
    """
    st.subheader(f"Editing: {listing['title']}")
    
    with st.form(key=f"edit_form_{form_key_prefix}_{listing_id}"):
        title = st.text_input("Project Title *", value=listing['title'], key=f"edit_title_{form_key_prefix}_{listing_id}")
        team = st.text_input("Additional Collaborators", value=listing.get('team', 'n/a') if listing.get('team') != 'n/a' else "", key=f"edit_team_{form_key_prefix}_{listing_id}")
        
        dept_index = 0 if listing['department'] == "Computer Science" else 1
        department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=dept_index, key=f"edit_dept_{form_key_prefix}_{listing_id}")
        
        openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=listing['openings'], step=1, key=f"edit_openings_{form_key_prefix}_{listing_id}")
        
        # Parse start date
        try:
            start_date_obj = datetime.strptime(listing['start_date'], "%B %d, %Y")
        except:
            start_date_obj = datetime.now()
        start_date = st.date_input("Start Date *", value=start_date_obj, key=f"edit_start_date_{form_key_prefix}_{listing_id}")
        st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
        
        duration_options = ["1 semester", "2 semesters", "More than 2 semesters"]
        duration_index = duration_options.index(listing['duration']) if listing['duration'] in duration_options else 0
        duration = st.selectbox("Duration *", options=duration_options, index=duration_index, key=f"edit_duration_{form_key_prefix}_{listing_id}")
        
        weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=listing['weekly_hours'], step=1, key=f"edit_hours_{form_key_prefix}_{listing_id}")
        
        comp_index = 0 if listing['compensation_type'] == "paid" else 1
        compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=comp_index, key=f"edit_comp_type_{form_key_prefix}_{listing_id}")
        
        pay_rate = None
        if compensation_type == "Paid":
            pay_rate = st.number_input(
                "Hourly Pay Rate ($) *",
                min_value=0.0,
                value=float(listing.get('pay_rate', 0)),
                step=0.01,
                format="%.2f",
                key=f"edit_pay_rate_{form_key_prefix}_{listing_id}"
            )
        
        st.write("Skills Required *")
        current_skills = [s.strip() for s in listing['skills'].split(',')] if listing['skills'] else []
        skills = st.multiselect(
            "Select skills",
            options=SKILLS_OPTIONS,
            default=[s for s in current_skills if s in SKILLS_OPTIONS],
            placeholder="Select all that apply",
            label_visibility="collapsed",
            key=f"edit_skills_{form_key_prefix}_{listing_id}"
        )
        
        website_urls = st.text_input("Website URL(s)", value=listing.get('website_urls', '') if listing.get('website_urls') != 'n/a' else "", key=f"edit_website_{form_key_prefix}_{listing_id}")
        summary = st.text_area("Summary/Description *", value=listing['summary'], key=f"edit_summary_{form_key_prefix}_{listing_id}")
        
        st.write("Preferred Method of Communication *")
        current_comm = [c.strip() for c in listing.get('communication', '').split(',')] if listing.get('communication') else []
        communication = st.multiselect(
            "Select communication methods",
            options=["Email", "Teams"],
            default=[c for c in current_comm if c in ["Email", "Teams"]],
            placeholder="Select all that apply",
            label_visibility="collapsed",
            key=f"edit_comm_{form_key_prefix}_{listing_id}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with col2:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel_button:
            st.session_state.editing_listing = None
            st.rerun()
        
        if save_button:
            errors = []
            if not title.strip():
                errors.append("Project Title")
            if not department:
                errors.append("Department/Lab")
            if openings < 1:
                errors.append("Number of Openings")
            if not start_date:
                errors.append("Start Date")
            if not duration:
                errors.append("Duration")
            if weekly_hours < 1:
                errors.append("Number of Hours per Week")
            if not compensation_type:
                errors.append("Compensation Type")
            if compensation_type == "Paid" and (pay_rate is None or pay_rate <= 0):
                errors.append("Hourly Pay Rate")
            if not skills:
                errors.append("Skills Required")
            if not summary.strip():
                errors.append("Summary/Description")
            if not communication:
                errors.append("Preferred Method of Communication")
            
            if errors:
                st.error(f"Please fill out the following required fields: {', '.join(errors)}")
            else:
                start_date_formatted = start_date.strftime("%B %d, %Y")
                skills_str = ", ".join(skills)
                communication_str = ", ".join(communication)
                
                updated_listing = {
                    "title": title,
                    "team": team if team else "n/a",
                    "department": department,
                    "skills": skills_str,
                    "openings": openings,
                    "start_date": start_date_formatted,
                    "duration": duration,
                    "pay_rate": pay_rate if compensation_type == "Paid" else 0,
                    "weekly_hours": weekly_hours,
                    "summary": summary,
                    "compensation_type": compensation_type.lower(),
                    "website_urls": website_urls if website_urls else "n/a",
                    "communication": communication_str,
                }
                
                try:
                    update_listing_in_firebase(listing_id, updated_listing, user_info.get('idToken'))
                    st.success(f"✅ Listing '{title}' has been updated successfully!")
                    st.session_state.editing_listing = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to update listing: {e}")

def render_listings(listings, show_edit=False, show_delete=False, show_favorite=False, user_info=None, tab_prefix="browse"):
    """Display a list of research opportunity listings in a structured and readable format.
    
    Args:
        listings: List of listing dictionaries to display
        show_edit: Whether to show edit buttons
        show_delete: Whether to show delete buttons (admin only in Browse tab)
        show_favorite: Whether to show favorite/star button
        user_info: Current user information for permission checks
        tab_prefix: Prefix for session state keys to avoid conflicts between tabs
    """
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        for idx, listing in enumerate(listings):
            listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
            container_key = f"{tab_prefix}_listing_container_{listing_id}_{idx}"
            
            # Check if this listing is being edited
            is_editing = (st.session_state.get("editing_listing") == listing_id and 
                         st.session_state.get("editing_tab") == tab_prefix)
            
            with st.container(key=container_key, border=True):
                if is_editing:
                    render_edit_form(listing, listing_id, tab_prefix)
                else:
                    st.subheader(listing["title"])
                    st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
                    st.write(f"**Additional Collaborators:** {listing['team']}")
                    st.write(f"**Department/Lab:** {listing['department']}")
                    st.write(f"**Number of Openings:** {listing['openings']}")
                    st.write(f"**Start Date:** {listing['start_date']}")
                    st.write(f"**Duration:** {listing['duration']}")
                    st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
                    st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
                    st.write(f"**Skills Required:** {listing['skills']}")
                    if "website_urls" in listing and listing["website_urls"] != "n/a":
                        st.write(f"**Website URL(s):** {listing['website_urls']}")
                    st.write(f"**Summary/Description:** {listing['summary']}")
                    if "communication" in listing and listing["communication"]:
                        st.write(f"**Preferred Method of Communication:** {listing['communication']}")
                    st.write("")
                    
                    # Initialize session state for confirmation if not present
                    delete_confirm_key = f"delete_confirm_{tab_prefix}"
                    if delete_confirm_key not in st.session_state:
                        st.session_state[delete_confirm_key] = {}
                    
                    # Check if delete confirmation is active for this listing
                    if st.session_state[delete_confirm_key].get(listing_id):
                        # Show full-width delete confirmation
                        st.warning(f"Are you sure you want to delete **{listing['title']}**?")
                        col_yes, col_no = st.columns([1, 1])
                        with col_yes:
                            if st.button("🗑️ Confirm Delete", key=f"confirm_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
                                try:
                                    delete_listing_from_firebase(listing.get("listing_id"), user_info.get('idToken'))
                                    st.success(f"'{listing['title']}' has been deleted.")
                                    st.session_state[delete_confirm_key][listing_id] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete listing: {e}")
                        with col_no:
                            if st.button("❌ Cancel", key=f"cancel_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
                                st.session_state[delete_confirm_key][listing_id] = False
                                st.rerun()
                    else:
                        # Action buttons row - keeping original narrow width
                        button_cols = st.columns([1, 1, 4])
                        
                        # Edit button
                        if show_edit:
                            with button_cols[0]:
                                if st.button("✏️ Edit", key=f"edit_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
                                    st.session_state.editing_listing = listing_id
                                    st.session_state.editing_tab = tab_prefix
                                    st.rerun()
                        
                        # Delete button
                        if show_delete:
                            with button_cols[1]:
                                if st.button("🗑️ Delete", key=f"delete_{tab_prefix}_{listing_id}_{idx}", use_container_width=True):
                                    st.session_state[delete_confirm_key][listing_id] = True
                                    st.rerun()

def main():
    """Main entry point for the Research Opportunities page."""
    st.title("Research Opportunities 🔍")

    # Show tabs based on role
    if user_info['role'] in ("faculty", "admin"):
        tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "My Listings"])
    else:
        tab1, = st.tabs(["Browse Listings"])

    # Browse Listings
    with tab1:
        hours_filter, compensation_filter, faculty_filter = render_sidebar_filters()
        listings = get_all_listings_from_firebase()[::-1]  # Firebase only
        filtered_listings = filter_listings(listings, hours_filter, compensation_filter, faculty_filter)
        
        # Show admin edit/delete capability notice
        if user_info['role'] == "admin":
            st.info("👑 **Admin View:** You can edit or delete any listing from this tab.")
        
        if filtered_listings:
            # Students see favorite button, admins see edit/delete
            render_listings(
                filtered_listings, 
                show_edit=(user_info['role'] == "admin"),
                show_delete=(user_info['role'] == "admin"),
                show_favorite=(user_info['role'] == "student"),
                user_info=user_info,
                tab_prefix="browse"
            )
        else:
            st.info("No listings match your filters.")

    # Create Listing (faculty/admin only)
    if user_info['role'] in ("faculty", "admin") and tab2 is not None:
        with tab2:
            st.header("Create a New Research Listing")

            if "form_counter" not in st.session_state:
                st.session_state.form_counter = 0

            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                if st.session_state.get("listing_created", False):
                    st.success(f"Listing '{st.session_state.listing_title}' successfully created!")
                    st.session_state.listing_created = False

                with st.container(border=True):
                    form_key = st.session_state.form_counter
                    title = st.text_input("Project Title *", value="", placeholder="ex. Biometric Authentication in Smartphones", key=f"title_input_{form_key}")
                    team = st.text_input("Additional Collaborators", value="", placeholder="ex. Grace Hopper, John von Neumann", key=f"team_input_{form_key}")
                    department = st.selectbox("Department/Lab *", options=["Computer Science", "Data Science"], index=0, key=f"dept_input_{form_key}")
                    openings = st.number_input("Number of Openings *", min_value=1, max_value=10, value=1, step=1, key=f"openings_input_{form_key}")
                    start_date = st.date_input("Start Date *", key=f"start_date_input_{form_key}")
                    st.caption(f"Will display as: {start_date.strftime('%B %d, %Y')}")
                    duration = st.selectbox("Duration *", options=["1 semester", "2 semesters", "More than 2 semesters"], index=0, key=f"duration_input_{form_key}")
                    weekly_hours = st.number_input("Number of Hours per Week *", min_value=1, value=1, step=1, key=f"hours_input_{form_key}")

                    compensation_type = st.radio("Compensation Type *", ["Paid", "Unpaid"], index=None, key=f"comp_type_{form_key}")
                    if compensation_type == "Paid":
                        pay_rate = st.number_input(
                            "Hourly Pay Rate ($) *",
                            min_value=0.0,
                            step=0.01,
                            format="%.2f",
                            key=f"pay_rate_input_{form_key}"
                        )

                    st.write("Skills Required *")
                    skills = st.multiselect(
                        "Select skills",
                        options=SKILLS_OPTIONS,
                        default=None,
                        placeholder="Select all that apply",
                        label_visibility="collapsed",
                        key=f"skills_input_{form_key}"
                    )

                    website_urls = st.text_input("Website URL(s)", value="", placeholder="ex. https://example.com", key=f"website_input_{form_key}")
                    summary = st.text_area("Summary/Description *", value="", key=f"summary_input_{form_key}")
                    
                    st.write("Preferred Method of Communication *")
                    communication = st.multiselect(
                        "Select communication methods",
                        options=["Email", "Teams"],
                        default=None,
                        placeholder="Select all that apply",
                        label_visibility="collapsed",
                        key=f"comm_input_{form_key}"
                    )

                    submitted = st.button("Post Listing")
                    if submitted:
                        errors = []
                        if not title.strip():
                            errors.append("Project Title")
                        if not department:
                            errors.append("Department/Lab")
                        if openings < 1:
                            errors.append("Number of Openings")
                        if not start_date:
                            errors.append("Start Date")
                        if not duration:
                            errors.append("Duration")
                        if weekly_hours < 1:
                            errors.append("Number of Hours per Week")
                        if not compensation_type:
                            errors.append("Compensation Type")
                        if compensation_type == "Paid" and (not 'pay_rate' in locals() or pay_rate <= 0):
                            errors.append("Hourly Pay Rate")
                        if not skills:
                            errors.append("Skills Required")
                        if not summary.strip():
                            errors.append("Summary/Description")
                        if not communication:
                            errors.append("Preferred Method of Communication")

                        if errors:
                            st.error(f"Please fill out the following required fields: {', '.join(errors)}")
                        else:
                            date_posted_formatted = datetime.now().strftime("%B %d, %Y")
                            profile_data = get_user_profile(user_info['uid'])
                            posted_by = profile_data.get('name', 'Unknown') if profile_data else 'Unknown'
                            start_date_formatted = start_date.strftime("%B %d, %Y")
                            skills_str = ", ".join(skills)
                            communication_str = ", ".join(communication)

                            new_listing = {
                                "title": title,
                                "pi": posted_by,
                                "team": team if team else "n/a",
                                "department": department,
                                "skills": skills_str,
                                "openings": openings,
                                "start_date": start_date_formatted,
                                "duration": duration,
                                "pay_rate": pay_rate if compensation_type == "Paid" else 0,
                                "weekly_hours": weekly_hours,
                                "summary": summary,
                                "date_posted": date_posted_formatted,
                                "compensation_type": compensation_type.lower(),
                                "website_urls": website_urls if website_urls else "n/a",
                                "communication": communication_str,
                                "posted_by_uid": user_info['uid']
                            }

                            try:
                                listing_id = save_listing_to_firebase(new_listing)
                                st.session_state.listing_created = True
                                st.session_state.listing_title = title
                                st.session_state.listing_posted_by = posted_by
                                st.session_state.listing_date = date_posted_formatted
                                st.session_state.form_counter += 1
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to create listing: {e}")

        # My Listings
        with tab3:
            st.header("My Listings")
            
            # Both admins and faculty see only their own listings here
            my_listings = get_user_listings_from_firebase(user_info['uid'])
            
            if my_listings:
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    for idx, listing in enumerate(my_listings[::-1]):
                        listing_id = listing.get("listing_id") or f"{listing['title']}_{idx}"
                        container_key = f"my_listing_container_{listing_id}"
                        
                        # Check if this listing is being edited
                        is_editing = (st.session_state.get("editing_listing") == listing_id and 
                                     st.session_state.get("editing_tab") == "my")

                        with st.container(key=container_key, border=True):
                            if is_editing:
                                render_edit_form(listing, listing_id, "my")
                            else:
                                st.subheader(listing["title"])
                                st.write(f"Posted by {listing['pi']} on {listing['date_posted']}")
                                st.write(f"**Additional Collaborators:** {listing['team']}")
                                st.write(f"**Department/Lab:** {listing['department']}")
                                st.write(f"**Number of Openings:** {listing['openings']}")
                                st.write(f"**Start Date:** {listing['start_date']}")
                                st.write(f"**Duration:** {listing['duration']}")
                                st.write(f"**Number of Hours per Week:** {listing['weekly_hours']}")
                                st.write(f"**Hourly Pay Rate:** ${listing['pay_rate']}")
                                st.write(f"**Skills Required:** {listing['skills']}")
                                if "website_urls" in listing and listing["website_urls"] != "n/a":
                                    st.write(f"**Website URL(s):** {listing['website_urls']}")
                                st.write(f"**Summary/Description:** {listing['summary']}")
                                if "communication" in listing and listing["communication"]:
                                    st.write(f"**Preferred Method of Communication:** {listing['communication']}")
                                st.write("")

                                # Initialize session state for confirmation if not present
                                if "delete_confirm_my" not in st.session_state:
                                    st.session_state.delete_confirm_my = {}

                                # Check if delete confirmation is active for this listing
                                if st.session_state.delete_confirm_my.get(listing_id):
                                    # Show full-width delete confirmation
                                    st.warning(f"Are you sure you want to delete **{listing['title']}**?")
                                    col_yes, col_no = st.columns([1, 1])
                                    with col_yes:
                                        if st.button("🗑️ Confirm Delete", key=f"confirm_my_{listing_id}", use_container_width=True):
                                            try:
                                                delete_listing_from_firebase(listing.get("listing_id"), user_info.get('idToken'))
                                                st.success(f"'{listing['title']}' has been deleted.")
                                                st.session_state.delete_confirm_my[listing_id] = False
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Failed to delete listing: {e}")
                                    with col_no:
                                        if st.button("❌ Cancel", key=f"cancel_my_{listing_id}", use_container_width=True):
                                            st.session_state.delete_confirm_my[listing_id] = False
                                            st.rerun()
                                else:
                                    # Action buttons row - keeping original narrow width
                                    button_cols = st.columns([1, 1, 4])
                                    
                                    # Edit button
                                    with button_cols[0]:
                                        if st.button("✏️ Edit", key=f"edit_my_{listing_id}", use_container_width=True):
                                            st.session_state.editing_listing = listing_id
                                            st.session_state.editing_tab = "my"
                                            st.rerun()
                                    
                                    # Delete button
                                    with button_cols[1]:
                                        if st.button("🗑️ Delete", key=f"delete_my_{listing_id}", use_container_width=True):
                                            st.session_state.delete_confirm_my[listing_id] = True
                                            st.rerun()
            else:
                st.info("You haven't created any listings yet.")

if __name__ == "__main__":
    main()

#-----END OF FILE-----