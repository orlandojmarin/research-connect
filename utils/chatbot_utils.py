# ORLANDO

"""
Chatbot utilities for ResearchConnect SCSU
Handles chatbot functionality, response generation, and conversation management
"""

import datetime
import random
import streamlit as st

def initialize_chat_session():
    """
    Initialize chat session state and welcome message
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_message = {
            "role": "assistant",
            "content": "Hello! I'm ResearchAI, your friendly assistant for all things research at SCSU. How can I help you today?",
            "timestamp": datetime.datetime.now()
        }
        st.session_state.messages.append(welcome_message)

def get_sidebar_info():
    """
    Get sidebar information and statistics
    
    Returns:
        dict: Sidebar content configuration
    """
    sidebar_config = {
        "assistant_description": {
            "title": "🧠 ResearchAI Assistant",
            "help_topics": [
                "🔍 Finding research opportunities",
                "👨‍🏫 Information about faculty",
                "📚 Campus resources and offices", 
                "💼 Internship and fellowship programs",
                "📝 Application processes",
                "❓ General research questions"
            ]
        },
        "quick_tips": {
            "title": "🎯 Quick Tips",
            "example_questions": [
                "What research opportunities are available in Computer Science?",
                "How do I apply for undergraduate research?",
                "Tell me about the STEM Center",
                "What internships are available through the Business department?"
            ]
        }
    }
    return sidebar_config

def get_chat_statistics():
    """
    Calculate and return chat statistics
    
    Returns:
        dict: Chat statistics
    """
    if "messages" not in st.session_state:
        return {"user_messages": 0, "total_messages": 0}
    
    user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
    total_messages = len(st.session_state.messages)
    
    return {
        "user_messages": user_messages,
        "total_messages": total_messages
    }

def clear_conversation():
    """
    Clear the conversation history
    """
    st.session_state.messages = []
    initialize_chat_session()

def get_suggested_questions():
    """
    Get suggested questions for new users
    
    Returns:
        list: List of tuples containing (button_text, question)
    """
    suggestions = [
        ("🔍 Research Opportunities", "What research opportunities are available?"),
        ("🎓 Getting Started", "How do I get involved in undergraduate research?"),
        ("🔬 STEM Center", "Tell me about the STEM Center"),
        ("💼 Career Services", "What career services does SCSU offer?"),
        ("👨‍🏫 Find Mentors", "How do I find a research mentor?"),
        ("📋 Internships", "What internship programs are available?")
    ]
    return suggestions

def add_user_message(content):
    """
    Add user message to chat history
    
    Args:
        content (str): User message content
    """
    message = {
        "role": "user",
        "content": content,
        "timestamp": datetime.datetime.now()
    }
    st.session_state.messages.append(message)

def add_assistant_message(content):
    """
    Add assistant message to chat history
    
    Args:
        content (str): Assistant message content
    """
    message = {
        "role": "assistant", 
        "content": content,
        "timestamp": datetime.datetime.now()
    }
    st.session_state.messages.append(message)

def generate_chatbot_response(user_input):
    """
    Generate chatbot responses based on user input
    
    Args:
        user_input (str): User's input message
        
    Returns:
        str: Generated response
    """
    user_input_lower = user_input.lower()
    
    # Define response templates
    responses = get_response_templates()
    
    # Check for keywords and return appropriate response
    for keywords, response_key in get_keyword_mappings():
        if any(keyword in user_input_lower for keyword in keywords):
            return responses[response_key]
    
    # Default response for unrecognized inputs
    return generate_default_response(user_input)

def get_response_templates():
    """
    Get predefined response templates
    
    Returns:
        dict: Response templates
    """
    return {
        "research_opportunities": """🔍 **Research Opportunities at SCSU:**

I'd be happy to help you find research opportunities! Here are some ways to get started:

**By Department:**
• **Computer Science & Engineering**: AI/ML projects, software development, cybersecurity research
• **Business**: Market research, organizational behavior studies, entrepreneurship projects  
• **Natural Sciences**: Biology, chemistry, environmental science research
• **Social Sciences**: Psychology studies, sociology research, education projects

**How to Get Involved:**
1. Browse our **Listings** page to see current openings
2. Contact faculty members directly about their research
3. Visit department websites for specific opportunities
4. Check with the STEM Center for research programs

**Next Steps:**
What specific area interests you most? I can provide more detailed information about opportunities in your field of interest!""",

        "stem_center": """🔬 **SCSU STEM Center:**

The STEM Center is a fantastic resource for students in Science, Technology, Engineering, and Mathematics!

**Location**: Engleman Hall

**Services Offered:**
• Academic tutoring and support
• Research opportunity coordination  
• STEM career guidance
• Workshop series on research methods
• Peer mentoring programs
• Equipment and lab access

**Programs:**
• Undergraduate Research Program
• STEM Scholars Initiative  
• Summer Research Internships
• Graduate School Preparation

**Contact Information:**
• Email: stemcenter@southernct.edu
• Phone: (203) 392-[XXXX]
• Hours: Monday-Friday 9AM-5PM

Would you like me to help you with anything specific about the STEM Center or connect you with other campus resources?""",

        "career_services": """💼 **Career & Professional Development:**

SCSU offers excellent career support through several offices:

**Office of Career and Professional Development:**
• Resume and cover letter assistance
• Interview preparation
• Career counseling and planning
• Job search strategies
• Professional networking events

**Internship Programs:**
• Business Internships Office
• STEM industry partnerships  
• Government and non-profit placements
• International internship opportunities

**Special Programs:**
• Women in Leadership Academy - Innovation Hub
• Professional development workshops
• Career fairs and employer networking
• Alumni mentorship program

**Resources Available:**
• Handshake job portal access
• Practice interview sessions
• Salary negotiation workshops
• LinkedIn profile optimization

Would you like specific information about internships in your field of study, or help with career planning resources?""",

        "application_process": """📝 **How to Apply for Research Opportunities:**

**Step-by-Step Process:**

**1️⃣ Explore Opportunities**
• Browse our Listings page
• Check department websites
• Talk to professors in your classes

**2️⃣ Prepare Your Application**
• Update your resume/CV
• Write a compelling cover letter
• Gather academic transcripts
• Prepare a personal statement

**3️⃣ Make Contact**
• Email faculty members directly
• Attend office hours to discuss projects
• Show genuine interest in their research

**4️⃣ Application Materials**
• Academic transcript
• Letters of recommendation (usually 1-2)
• Statement of purpose
• Portfolio (if applicable)

**Tips for Success:**
✅ Start early - good opportunities fill quickly
✅ Tailor each application to the specific project
✅ Demonstrate relevant coursework or experience
✅ Show enthusiasm and commitment
✅ Follow up professionally

Need help with any specific part of the application process?""",

        "faculty_mentors": """👨‍🏫 **Finding Faculty & Research Mentors:**

**How to Connect with Faculty:**

**Research Their Work:**
• Check department websites for faculty profiles
• Read recent publications or project descriptions
• Look for research interests that match yours

**Making Contact:**
• Send professional emails introducing yourself
• Attend office hours or department events
• Join research-focused student organizations

**What to Include in Your Outreach:**
• Your academic background and interests
• Specific questions about their research
• Your career goals and how research fits in
• Availability and commitment level

**Building Relationships:**
• Start by taking their courses
• Participate actively in class discussions
• Volunteer for research-related activities
• Show consistent interest and reliability

**Departments with Active Research:**
• Computer Science & Engineering
• Business & Economics  
• Natural Sciences
• Education & Social Work
• Liberal Arts & Humanities

Would you like help crafting an email to a specific faculty member, or information about faculty in a particular department?""",

        "undergraduate_research": """🎓 **Undergraduate Research at SCSU:**

**Why Get Involved:**
• Build skills for graduate school or careers
• Work closely with faculty mentors
• Gain hands-on experience in your field
• Develop critical thinking and problem-solving abilities
• Network with professionals and peers

**Types of Opportunities:**
• **Independent Study Projects** (1-3 credits)
• **Summer Research Programs** (full-time, often paid)
• **Work-Study Research Positions** (part-time, paid)
• **Volunteer Research** (flexible hours)
• **Honors Thesis Projects** (capstone experience)

**Getting Started:**
1. Maintain a good GPA (usually 3.0+)
2. Complete foundational courses in your field
3. Develop relationships with faculty
4. Apply for research programs early
5. Be prepared to commit time and effort

**Funding Opportunities:**
• STEM Research Scholarships
• Undergraduate Research Grants
• Work-study positions
• Summer stipend programs

**Timeline:**
• **Fall**: Applications open for summer programs
• **Spring**: Most research positions begin  
• **Summer**: Intensive research opportunities

Ready to take the next step? I can help you identify opportunities in your major!""",

        "general_help": """🤝 **I'm Here to Help!**

I can assist you with:

**Research & Academics:**
🔍 Finding research opportunities by field or department
👨‍🏫 Connecting with faculty and potential mentors  
📝 Understanding application processes and requirements
🎓 Learning about undergraduate vs graduate research options

**Campus Resources:**
📚 Information about the STEM Center and other support offices
💼 Career services and professional development
🏢 Internship and fellowship programs
📍 Campus office locations and contact information

**Getting Started:**
💡 Tips for new researchers
📋 Application preparation guidance  
⏰ Timeline planning for research opportunities
🎯 Setting academic and career goals

**Just ask me questions like:**
• "What research is available in [your field]?"
• "How do I contact Professor [Name] about their research?"
• "What should I include in my research application?"
• "Tell me about [specific campus office or program]"

What specific area would you like to explore? I'm here to make your research journey at SCSU as smooth as possible! 🦉"""
    }

def get_keyword_mappings():
    """
    Get keyword to response mappings
    
    Returns:
        list: List of tuples containing (keywords, response_key)
    """
    return [
        (["research opportunities", "research projects", "find research"], "research_opportunities"),
        (["stem center", "stem centre"], "stem_center"),
        (["career services", "career development", "internships"], "career_services"),
        (["application", "apply", "how to apply"], "application_process"),
        (["faculty", "professors", "mentor", "advisor"], "faculty_mentors"),
        (["undergraduate research", "undergrad research"], "undergraduate_research"),
        (["help", "assistance", "support"], "general_help")
    ]

def generate_default_response(user_input):
    """
    Generate default response for unrecognized input
    
    Args:
        user_input (str): User's input
        
    Returns:
        str: Default response
    """
    default_responses = [
        f"""That's an interesting question about "{user_input}"! 

While I specialize in research opportunities and campus resources at SCSU, I'd be happy to help you find the right information or connect you with someone who can assist.

**Here are some ways I can help:**
• 🔍 Find research opportunities in your field of interest
• 👨‍🏫 Connect you with faculty and their research areas
• 📚 Information about campus support services
• 💼 Career and internship resources
• 📝 Guidance on applications and next steps

**Or try asking:**
• "What research opportunities are available?"
• "Tell me about the STEM Center"  
• "How do I get involved in undergraduate research?"
• "What career services does SCSU offer?"

What specific aspect of research or campus resources would you like to explore?""",

        f"""Thanks for your question about "{user_input}"! 

I'm ResearchAI, and I'm specifically designed to help SCSU students with research opportunities and campus resources. 

**I can help you with:**
🔬 Research opportunities across all departments
🏢 Campus offices and support services  
💼 Internships and career development
👥 Connecting with faculty and mentors
📋 Application processes and requirements

**Popular questions I get:**
• "What research is available in my major?"
• "How do I find a research mentor?"
• "Tell me about [specific campus office]"
• "What's the application process like?"

Is there something specific about research or campus resources I can help you with today?""",

        f"""I appreciate your question about "{user_input}"! 

As your ResearchAI assistant, I'm here to help you navigate research opportunities and campus resources at SCSU.

**Quick suggestions:**
• Browse our **Listings** page for current research projects
• Check out **Resources** for campus support offices
• Ask me about specific departments or research areas
• Get guidance on application processes

**Try rephrasing your question, or ask me something like:**
• "What research opportunities match my interests in [field]?"
• "How do I get started with undergraduate research?"
• "What support is available through [campus office]?"

What would you like to know about research opportunities or campus resources? 🦉"""
    ]
    
    return random.choice(default_responses)

def get_help_navigation():
    """
    Get help navigation options
    
    Returns:
        dict: Help navigation configuration
    """
    return {
        "other_assistance": [
            "Browse the **Listings** page for current research projects",
            "Visit the **Resources** page for campus offices", 
            "Contact faculty directly through department websites"
        ],
        "navigation_options": [
            {"text": "📋 Go to Listings", "page": "pages/listings.py", "key": "nav_listings"},
            {"text": "📚 Go to Resources", "page": "pages/resources.py", "key": "nav_resources"},
            {"text": "🏠 Back to Home", "page": "home.py", "key": "nav_home"}
        ]
    }

def log_conversation(user_input, bot_response):
    """
    Log conversation for analytics and improvement
    
    Args:
        user_input (str): User's input
        bot_response (str): Bot's response
    """
    # Placeholder for conversation logging
    # In a real application, you would log this to a database
    log_entry = {
        "timestamp": datetime.datetime.now(),
        "user_input": user_input,
        "bot_response": bot_response,
        "session_id": st.session_state.get("session_id", "unknown")
    }
    
    # For now, just store in session state
    if "conversation_log" not in st.session_state:
        st.session_state.conversation_log = []
    
    st.session_state.conversation_log.append(log_entry)