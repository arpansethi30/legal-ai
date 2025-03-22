import streamlit as st
import requests
import json
import io
from datetime import datetime
import base64

# App title and configuration
st.set_page_config(page_title="Legal AI Agent Demo", layout="wide")
st.title("Legal AI Agent - Hackathon Demo")
st.markdown("### Test your AI-powered legal negotiation and contract drafting assistant")

# Function to check if the backend is running
def check_backend():
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            return True
        return False
    except:
        return False

# Function to call the backend API
def call_api(endpoint, data):
    try:
        response = requests.post(f"http://localhost:8000{endpoint}", json=data, timeout=60)
        return response.status_code, response.json() if response.status_code == 200 else {"error": response.text}
    except requests.exceptions.ConnectionError:
        return 500, {"error": "Cannot connect to the backend. Make sure it's running on http://localhost:8000"}
    except Exception as e:
        return 500, {"error": f"Error: {str(e)}"}

# Check if backend is running
backend_running = check_backend()

if not backend_running:
    st.error("⚠️ Cannot connect to the backend server. Please make sure it's running on http://localhost:8000")
    st.info("Run this command in another terminal: `cd backend && python -m app.main`")
    st.stop()
else:
    st.success("✅ Successfully connected to the backend server")

# Simple navigation
page = st.sidebar.selectbox(
    "Select Feature to Test",
    ["Contract Generation", "Negotiation Analysis"]
)

# Contract Generation Page
if page == "Contract Generation":
    st.header("Contract Generation")
    st.write("Generate a legal contract based on specified terms and conditions.")
    
    # Form for contract generation
    with st.form("contract_form"):
        parties = st.text_input("Parties (comma separated)", "TechCorp Inc., DevServices LLC")
        contract_type = st.selectbox(
            "Contract Type",
            ["service_agreement", "nda", "employment", "licensing", "partnership"]
        )
        
        st.write("Contract Terms:")
        payment_term = st.text_input("Payment Term", "$10,000 monthly fee")
        duration_term = st.text_input("Duration", "12 months from signing")
        ip_term = st.text_input("Intellectual Property", "All IP remains with TechCorp")
        
        submit_button = st.form_submit_button("Generate Contract")
    
    if submit_button:
        with st.spinner("Generating contract..."):
            contract_data = {
                "negotiation_id": "test-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
                "parties": [p.strip() for p in parties.split(",")],
                "terms": [
                    {"type": "payment", "details": payment_term},
                    {"type": "duration", "details": duration_term},
                    {"type": "intellectual_property", "details": ip_term}
                ],
                "contract_type": contract_type
            }
            
            # Call the backend API
            status, response = call_api("/contracts/generate", contract_data)
            
            if status == 200:
                st.success("Contract generated successfully!")
                
                # Display contract content
                st.subheader("Generated Contract")
                st.text_area("Contract Content", response.get("content", ""), height=300)
            else:
                st.error(f"Failed to generate contract: {response.get('error', 'Unknown error')}")

# Negotiation Analysis Page
elif page == "Negotiation Analysis":
    st.header("Negotiation Analysis")
    st.write("Analyze a negotiation transcript to extract terms, risks, and suggestions.")
    
    transcript = st.text_area(
        "Enter Negotiation Transcript",
        "TechCorp agrees to pay $10,000 monthly for 12 months. All intellectual property developed during the project will remain with TechCorp. DevServices will provide 40 hours of consulting per month and guarantees response within 24 hours for critical issues.",
        height=200
    )
    
    if st.button("Analyze Negotiation"):
        with st.spinner("Analyzing negotiation..."):
            # Call the backend API
            status, response = call_api("/negotiations/analyze", {"transcript": transcript})
            
            if status == 200:
                st.success("Negotiation analyzed successfully!")
                
                # Display terms
                st.subheader("Extracted Terms")
                terms = response.get("terms", [])
                for i, term in enumerate(terms):
                    st.write(f"{i+1}. {term}")
                
                # Display risks
                st.subheader("Identified Risks")
                risks = response.get("risks", [])
                for i, risk in enumerate(risks):
                    st.write(f"{i+1}. **{risk.get('clause', 'Unknown')}**: {risk.get('risk', 'Unknown risk')}")
                
                # Display suggestions
                st.subheader("Suggestions")
                suggestions = response.get("suggestions", [])
                for i, suggestion in enumerate(suggestions):
                    st.write(f"{i+1}. {suggestion}")
            else:
                st.error(f"Failed to analyze negotiation: {response.get('error', 'Unknown error')}")

# Footer
st.markdown("---")
st.markdown("**Legal AI Agent** | Built for the AI Agents Hackathon")