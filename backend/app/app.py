import streamlit as st
import requests
import json
import time

BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="LexCounsel AI Demo",
    page_icon="⚖️",
    layout="wide"
)

# Header
st.title("⚖️ LexCounsel AI")
st.markdown("### State-of-the-art legal reasoning system for the Hackathon")

# Function to call backend API
def call_api(endpoint, data):
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=60)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection Error: {str(e)}")
        return None

# Sidebar navigation
demo_option = st.sidebar.selectbox(
    "Select Demo Feature",
    ["Legal Reasoning", "Expert Consultation", "Legal Issue Identification", "Client Memo Generation"]
)

# Check if backend is available
try:
    requests.get(f"{BASE_URL}/")
    st.sidebar.success("✅ Backend is running")
except:
    st.sidebar.error("❌ Backend not detected. Run 'python -m app.main' in backend folder")
    st.stop()

# Demo 1: Legal Reasoning
if demo_option == "Legal Reasoning":
    st.header("Multi-methodology Legal Reasoning")
    st.markdown("Analyze legal text using multiple formal legal reasoning methodologies")
    
    with st.form("reasoning_form"):
        legal_text = st.text_area(
            "Legal Text to Analyze",
            "The parties agree that all intellectual property created during the term of this agreement shall be owned exclusively by the Client, and Contractor hereby assigns all rights to such intellectual property to Client."
        )
        
        question = st.text_input(
            "Legal Question",
            "Who owns the intellectual property created during this agreement?"
        )
        
        methods = st.multiselect(
            "Reasoning Methods",
            ["Textual Analysis", "Statutory Interpretation", "Legal Principles Analysis", 
             "Analogical Reasoning", "Consequentialist Analysis", "Intentionalist Analysis"],
            default=["Textual Analysis", "Statutory Interpretation"]
        )
        
        submit_button = st.form_submit_button("Analyze")
    
    if submit_button:
        with st.spinner("Analyzing with multiple legal reasoning methodologies..."):
            result = call_api(
                "/workflow/reasoning", 
                {
                    "legal_text": legal_text,
                    "question": question,
                    "methods": methods
                }
            )
            
            if result:
                st.success("Analysis complete!")
                
                # Show the synthesized answer
                st.subheader("Synthesized Legal Opinion")
                st.markdown(result.get("synthesis", {}).get("synthesized_answer", "No synthesis available"))
                
                # Show confidence
                confidence = result.get("synthesis", {}).get("final_confidence", 0)
                st.progress(confidence/100)
                st.caption(f"Confidence: {confidence}%")
                
                # Show individual methodology results
                st.subheader("Analysis by Methodology")
                for method, analysis in result.get("method_analyses", {}).items():
                    with st.expander(f"{method} Analysis"):
                        st.markdown("#### Conclusion")
                        st.markdown(analysis.get("conclusion", "No conclusion available"))
                        
                        st.markdown("#### Reasoning Steps")
                        steps = analysis.get("reasoning_steps", [])
                        for i, step in enumerate(steps):
                            st.markdown(f"**Step {i+1}:** {step}")

# Demo 2: Expert Consultation
elif demo_option == "Expert Consultation":
    st.header("Expert Legal Consultation")
    st.markdown("Consult multiple specialized legal experts on a document or question")
    
    with st.form("consultation_form"):
        document = st.text_area(
            "Legal Document",
            "The Contractor agrees not to engage in any competing business within the entire United States for a period of 5 years after termination of this Agreement."
        )
        
        question = st.text_input(
            "Question for Experts",
            "Is this non-compete clause enforceable?"
        )
        
        experts = st.multiselect(
            "Legal Experts to Consult",
            ["Contract Law Expert", "Employment Law Expert", "Litigation Expert", 
             "Regulatory Compliance Expert", "Corporate Law Expert"],
            default=["Contract Law Expert", "Employment Law Expert", "Litigation Expert"]
        )
        
        submit_button = st.form_submit_button("Consult Experts")
    
    if submit_button:
        with st.spinner("Consulting legal experts..."):
            result = call_api(
                "/workflow/consult", 
                {
                    "question": question,
                    "document": document,
                    "experts": experts
                }
            )
            
            if result:
                st.success("Expert consultation complete!")
                
                # Show synthesis
                st.subheader("Executive Summary")
                st.markdown(result.get("synthesis", {}).get("executive_summary", "No summary available"))
                
                # Show consensus and disagreements
                with st.expander("Areas of Consensus"):
                    consensus = result.get("synthesis", {}).get("areas_of_consensus", [])
                    if consensus:
                        for point in consensus:
                            st.markdown(f"• {point}")
                    else:
                        st.markdown("No consensus points identified")
                
                with st.expander("Significant Disagreements"):
                    disagreements = result.get("synthesis", {}).get("significant_disagreements", [])
                    if disagreements:
                        for point in disagreements:
                            st.markdown(f"• {point}")
                    else:
                        st.markdown("No significant disagreements identified")
                
                # Show individual expert opinions
                st.subheader("Expert Opinions")
                for expert, opinion in result.get("expert_consultations", {}).items():
                    with st.expander(f"{expert} Opinion"):
                        st.markdown("#### Initial Assessment")
                        st.markdown(opinion.get("initial_assessment", "No assessment available"))
                        
                        st.markdown("#### Key Recommendations")
                        recommendations = opinion.get("recommendations", [])
                        for rec in recommendations:
                            st.markdown(f"• {rec}")

# Demo 3: Legal Issue Identification
elif demo_option == "Legal Issue Identification":
    st.header("Legal Issue Identification")
    st.markdown("Identify potential legal issues in a contract or document")
    
    with st.form("issue_form"):
        document = st.text_area(
            "Legal Document",
            "This agreement shall commence on January 1, 2025 and continue until terminated by either party with 30 days notice. Payment terms are net 30. All disputes shall be resolved through binding arbitration."
        )
        
        submit_button = st.form_submit_button("Identify Issues")
    
    if submit_button:
        with st.spinner("Identifying legal issues..."):
            result = call_api(
                "/workflow/identify-issues", 
                {
                    "document": document
                }
            )
            
            if result:
                st.success("Issue identification complete!")
                
                # Display issues
                issues = result.get("issues", [])
                st.subheader(f"Identified {len(issues)} Potential Issues")
                
                # Sort issues by seriousness if available
                issues_sorted = sorted(issues, 
                                      key=lambda x: 0 if x.get("seriousness") == "Critical" else
                                                    1 if x.get("seriousness") == "Significant" else 2,
                                      reverse=False)
                
                for i, issue in enumerate(issues_sorted):
                    seriousness = issue.get("seriousness", "Unknown")
                    color = "🔴" if seriousness == "Critical" else "🟠" if seriousness == "Significant" else "🟡"
                    
                    with st.expander(f"{color} Issue {i+1}: {issue.get('description', 'Unnamed Issue')}"):
                        st.markdown(f"**Context:** {issue.get('context', 'No context provided')}")
                        st.markdown(f"**Implications:** {issue.get('implications', 'No implications provided')}")
                        st.markdown(f"**Seriousness:** {seriousness}")

# Demo 4: Client Memo Generation
elif demo_option == "Client Memo Generation":
    st.header("Client Memo Generation")
    st.markdown("Generate a client-ready memo based on legal analysis")
    
    with st.form("memo_form"):
        analysis_text = st.text_area(
            "Legal Analysis (JSON or text)",
            """{
              "issue": "Non-compete clause enforceability",
              "conclusion": "The non-compete clause is likely unenforceable due to its excessive geographic scope and duration.",
              "reasoning": "Courts typically require non-compete agreements to be reasonable in scope, geography, and duration. This clause's 5-year nationwide restriction would likely be deemed unreasonably broad in most jurisdictions.",
              "recommendations": ["Narrow the geographic scope to regions where business is conducted", "Reduce duration to 1-2 years", "Add severability clause to protect if portions are invalidated"]
            }"""
        )
        
        client_name = st.text_input("Client Name", "Acme Corporation")
        contact_name = st.text_input("Contact Person", "John Smith")
        matter = st.text_input("Matter", "Non-compete Review")
        
        submit_button = st.form_submit_button("Generate Memo")
    
    if submit_button:
        with st.spinner("Generating client memo..."):
            # Parse analysis if possible
            try:
                analysis = json.loads(analysis_text)
            except:
                analysis = {"text": analysis_text}
            
            result = call_api(
                "/workflow/client-memo", 
                {
                    "analysis": analysis,
                    "client_info": {
                        "name": client_name,
                        "contact": contact_name,
                        "matter": matter
                    }
                }
            )
            
            if result:
                st.success("Client memo generated!")
                
                # Display memo
                memo = result.get("memo", {})
                
                st.markdown(f"## MEMORANDUM")
                st.markdown(f"**TO:** {client_name}")
                st.markdown(f"**FROM:** LexCounsel AI")
                st.markdown(f"**DATE:** {result.get('date', 'Today')}")
                st.markdown(f"**RE:** {matter}")
                st.markdown("---")
                
                st.markdown("### Executive Summary")
                st.markdown(memo.get("executive_summary", "No summary available"))
                
                st.markdown("### Background")
                st.markdown(memo.get("background", "No background provided"))
                
                st.markdown("### Key Findings")
                findings = memo.get("key_findings", [])
                for finding in findings:
                    st.markdown(f"• {finding}")
                
                st.markdown("### Recommendations")
                recommendations = memo.get("recommendations", [])
                for rec in recommendations:
                    st.markdown(f"• {rec}")
                
                st.markdown("### Next Steps")
                next_steps = memo.get("next_steps", [])
                for step in next_steps:
                    st.markdown(f"• {step}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**LexCounsel AI Demo** | Hackathon Project")
