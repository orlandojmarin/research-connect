# ResearchConnect SCSU

**Connecting Students with Research Opportunities at Southern Connecticut State University**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://researchconnect-scsu.streamlit.app/)

## Overview

ResearchConnect SCSU is a web platform designed to bridge the gap between students and research opportunities at Southern Connecticut State University. Built with Streamlit and powered by Google Cloud Platform, this application provides an intelligent, user-friendly interface for discovering research positions, connecting with faculty, and accessing campus resources.

**Live Application**: [researchconnect-scsu.streamlit.app](https://researchconnect-scsu.streamlit.app/)

## Contributors

This project was developed as a capstone project by:

- **Tatiana Eng** - Full-Stack Development and UI/UX Design
- **Orlando Marin** - Full-Stack Development and Cloud Deployment
- **Sana Muneer** - RAG Implementation and Quality Assurance

**Course**: Computer Science Project Seminar - CSC 400

**Institution**: Southern Connecticut State University

## Features

### ResearchAI Chatbot
Intelligent assistant powered by Google Vertex AI (Gemini 2.5 Flash) that helps students find research opportunities, get information about faculty projects, and navigate campus resources through natural language queries.

### Research Listings
Comprehensive database of faculty-led research projects with advanced filtering capabilities. Students can browse and save favorite opportunities, faculty can create and manage their postings, and administrators have full oversight of all listings.

### Role-Based Access
Tailored experiences for students, faculty, and administrators with appropriate permissions and functionality for each user type.

### Campus Resources
Centralized directory providing information about SCSU's Innovation Hub, Office of Career & Professional Development, JOBSs, and STEM Centers.

### Secure Authentication
Microsoft OIDC integration ensures only SCSU users can access the platform, with automatic role assignment based on email address.

## Technology Stack

### Frontend
- Streamlit - Interactive web application framework
- Python 3.9+

### Backend & Cloud Services
- **Google Cloud Platform**
  - Vertex AI (Gemini 2.5 Flash) for conversational AI
  - Service Account authentication
- **Firebase**
  - Realtime Database for data storage
  - Admin SDK for backend operations
- **Microsoft Azure**
  - OIDC authentication for SCSU accounts

### Key Dependencies
- `streamlit>=1.28.0`
- `firebase-admin>=6.2.0`
- `google-cloud-aiplatform>=1.66.0`
- `vertexai`
- `requests>=2.31.0`
- `Authlib`

See `requirements.txt` for complete dependency list.

## Local Development Setup

### Prerequisites
- Python 3.9 or higher
- Google Cloud Platform account with Vertex AI enabled
- Firebase project with Realtime Database
- Microsoft Azure app registration for OIDC

### Installation

1. Clone the repository
```bash
   git clone https://github.com/orlandojmarin/research-connect.git
   cd research-connect
```

2. Create and activate virtual environment
```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

4. Configure environment variables

   Create `.streamlit/secrets.toml` with your Firebase, GCP, and Microsoft OIDC credentials. See `secrets.toml` structure in the repository for required fields.

   Create `gcp-credentials.json` with your GCP service account credentials.

5. Run the application
```bash
   streamlit run home.py
```

   The app will be available at `http://localhost:8501`

## Security

- Microsoft OIDC authentication restricts access to SCSU email addresses only
- Role-based permissions enforce appropriate access levels
- Firebase security rules protect sensitive data
- All secrets and credentials are stored in environment variables and excluded from version control

## License

This project is developed for academic purposes as part of the CSC 400 capstone project at Southern Connecticut State University.

## Contact

For questions or feedback about ResearchConnect SCSU, please contact the development team through Southern Connecticut State University.

---

**Built by Tatiana Eng, Orlando Marin, and Sana Muneer**  
**Southern Connecticut State University | Computer Science Project Seminar - CSC 400**