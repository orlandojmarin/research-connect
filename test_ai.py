import os
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel

load_dotenv()

project_id = os.getenv('GCP_PROJECT_ID')
print(f"Project ID: {project_id}")

try:
    vertexai.init(project=project_id, location="us-central1")
    model = GenerativeModel("gemini-2.5-flash")
    
    response = model.generate_content("What research opportunities are available at SCSU?")
    print("\nAI Response:")
    print(response.text)
    print("\nSUCCESS! Vertex AI is working!")
    
except Exception as e:
    print(f"\nERROR: {e}")