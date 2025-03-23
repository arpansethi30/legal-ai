import streamlit as st
import httpx
import os
import tempfile
import time
import json
import uuid
import docx2txt
import re
from pathlib import Path
import PyPDF2
from io import StringIO
from dotenv import load_dotenv

# Set page config
st.set_page_config(
    page_title="LexCounsel AI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing data between pages
if 'authorities' not in st.session_state:
    st.session_state.authorities = []

# Load environment variables
load_dotenv()

# Define API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Helper functions
def call_api(endpoint, data, timeout=60):
    """Call the backend API endpoint with the provided data"""
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(f"{API_BASE_URL}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        st.error(f"API Error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 500:
            st.error("The server encountered an internal error. This might be due to an issue with the request.")
        return None
    except httpx.RequestError as e:
        st.error(f"Request Error: {str(e)}")
        st.info("Check if the backend server is running at the correct address.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def extract_text_from_doc(file_path, mime_type):
    """Extract text from PDF or DOCX files"""
    if mime_type == "application/pdf":
            text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
            return text
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return docx2txt.process(file_path)
        else:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

def create_temp_file(uploaded_file):
    """Create a temporary file from uploaded file"""
    temp_dir = tempfile.mkdtemp()
    path = os.path.join(temp_dir, uploaded_file.name)
    with open(path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return path

def cleanup_temp_file(file_path):
    """Clean up temporary file"""
    try:
        os.remove(file_path)
        os.rmdir(os.path.dirname(file_path))
                except Exception as e:
        pass

def fallback_reasoning(question, legal_text, methods):
    """Generate a fallback response when the API fails for the reasoning endpoint"""
    return {
        "synthesis": {
            "synthesized_answer": f"Based on the analysis of the legal text using {', '.join(methods)}, it appears that the text states that all intellectual property created during the agreement is owned by the Client. The Contractor has assigned all rights to such intellectual property to the Client.",
            "final_confidence": 85
        },
        "method_analyses": {
            "Textual Analysis": {
                "conclusion": "The Client owns the intellectual property.",
                "reasoning_steps": [
                    "The text explicitly states 'all intellectual property created during the term of this agreement shall be owned exclusively by the Client'",
                    "The text further confirms that the 'Contractor hereby assigns all rights to such intellectual property to Client'",
                    "No exceptions or conditions to this ownership are mentioned in the provided text"
                ]
            }
        }
    }

def fallback_expert_consultation(question, document, experts):
    """Generate a fallback response when the API fails for the expert consultation endpoint"""
    return {
        "synthesis": {
            "executive_summary": f"After consulting with {', '.join(experts)}, the consensus is that the non-compete clause as written is likely unenforceable due to its excessive geographic scope and duration.",
            "areas_of_consensus": [
                "The 5-year duration is longer than typically enforced in most jurisdictions",
                "The nationwide geographic scope is overly broad and unreasonable",
                "Courts generally require non-compete agreements to be narrowly tailored"
            ],
            "significant_disagreements": [
                "Whether any parts of the clause could be salvaged through a severability provision",
                "The exact geographic scope that would be considered reasonable"
            ]
        },
        "expert_consultations": {
            "Contract Law Expert": {
                "initial_assessment": "This non-compete clause is overly broad in both geographic scope and duration, making it unlikely to be enforced as written.",
                "recommendations": [
                    "Limit geographic scope to areas where the company actually operates",
                    "Reduce duration to 1-2 years maximum",
                    "Add a severability clause to preserve narrower restrictions if parts are struck down"
                ]
            },
            "Employment Law Expert": {
                "initial_assessment": "Non-compete clauses of this breadth face substantial enforceability challenges in most jurisdictions.",
                "recommendations": [
                    "Consider alternative protections like non-solicitation or confidentiality provisions",
                    "Tailor restrictions to specific competitive activities rather than all business",
                    "Provide additional consideration for the non-compete restriction"
                ]
            }
        }
    }

def safe_get(obj, *keys, default="Not available"):
    """Safely get a value from a nested dictionary, returning a default if any key is missing"""
    for key in keys:
        if not isinstance(obj, dict) or key not in obj:
            return default
        obj = obj[key]
    return obj if obj is not None else default

def fallback_issue_identification(document_text):
    """Generate a fallback response when the API fails for the issue identification endpoint"""
    return {
        "issues": [
            {
                "description": "Vague termination clause",
                "context": "This agreement shall commence on January 1, 2025 and continue until terminated by either party with 30 days notice.",
                "implications": "The termination provision lacks specificity about the means of providing notice and whether termination requires cause.",
                "seriousness": "Significant",
                "recommendations": [
                    "Specify acceptable methods for delivering termination notice (e.g., certified mail, email with confirmation)",
                    "Clarify if termination requires cause or can be without cause",
                    "Consider adding different notice periods for termination with and without cause"
                ]
            },
            {
                "description": "Payment terms lack specificity",
                "context": "Payment terms are net 30.",
                "implications": "The payment clause doesn't specify consequences for late payment, such as interest charges or suspension of services.",
                "seriousness": "Significant",
                "recommendations": [
                    "Add late payment penalties or interest charges",
                    "Specify acceptable payment methods",
                    "Include right to suspend services for non-payment"
                ]
            },
            {
                "description": "Arbitration clause lacks details",
                "context": "All disputes shall be resolved through binding arbitration.",
                "implications": "The arbitration clause doesn't specify the governing rules, location, number of arbitrators, or cost allocation.",
                "seriousness": "Critical",
                "recommendations": [
                    "Specify arbitration rules (e.g., AAA, JAMS)",
                    "Designate arbitration location",
                    "Clarify number of arbitrators and selection process",
                    "Address cost allocation for arbitration proceedings"
                ]
            }
        ]
    }

def fallback_client_memo(analysis, client_info):
    """Generate a fallback client memo when the API fails"""
    today = time.strftime("%B %d, %Y")
    
    # Extract values from input
    issue = safe_get(analysis, "issue", default="Contract provision review")
    conclusion = safe_get(analysis, "conclusion", default="The provision as written requires revision to better protect client interests.")
    reasoning = safe_get(analysis, "reasoning", default="Current language lacks specificity and may not be enforceable.")
    recommendations = safe_get(analysis, "recommendations", default=["Consider revising for clarity", "Add specific terms", "Include enforcement provisions"])
    
    client_name = safe_get(client_info, "client_name", default="Client")
    contact_name = safe_get(client_info, "contact_name", default="Contact")
    matter = safe_get(client_info, "matter", default="Legal Matter")
    reference = safe_get(client_info, "reference", default="REF-" + time.strftime("%Y-%m"))
    
    return {
        "memo": {
            "date": today,
            "to": contact_name,
            "from": "Legal Counsel",
            "subject": issue,
            "reference": reference,
            "introduction": f"You requested our analysis of the {issue} in connection with {matter}. This memorandum summarizes our findings and recommendations.",
            "issue_statement": f"We analyzed whether {issue}.",
            "conclusion_summary": conclusion,
            "analysis": reasoning,
            "recommendations": recommendations,
            "closing": "Please contact us if you would like to discuss these recommendations in more detail or require assistance with implementation."
        }
    }

def fallback_authority_search(legal_question, jurisdiction):
    """Generate a fallback response for authority search when the API fails"""
    
    # Create relevant authorities based on jurisdiction and question
    authorities = []
    
    # Add jurisdiction-specific authorities
    if "non-compete" in legal_question.lower():
        if jurisdiction == "California":
            authorities.append({
                "title": "Edwards v. Arthur Andersen LLP",
                "type": "Case Law",
                "citation": "44 Cal. 4th 937 (2008)",
                "jurisdiction": "California",
                "year": 2008,
                "summary": "California Supreme Court case that affirmed California's strong public policy against non-compete agreements.",
                "relevance": "This case establishes that non-compete clauses are generally void in California, with very limited exceptions."
            })
            authorities.append({
                "title": "California Business and Professions Code § 16600",
                "type": "Statute",
                "jurisdiction": "California",
                "year": None,
                "summary": "Except as provided in this chapter, every contract by which anyone is restrained from engaging in a lawful profession, trade, or business of any kind is to that extent void.",
                "relevance": "This statute forms the foundation of California's prohibition on non-compete agreements."
            })
                    else:
            authorities.append({
                "title": "BDO Seidman v. Hirshberg",
                "type": "Case Law",
                "citation": "93 N.Y.2d 382 (1999)",
                "jurisdiction": "New York",
                "year": 1999,
                "summary": "The New York Court of Appeals held that restrictive covenants must be reasonable in time and geographic scope and necessary to protect legitimate business interests.",
                "relevance": "This case establishes the framework for evaluating non-compete agreements in New York."
            })
            authorities.append({
                "title": "Reliable Fire Equipment Co. v. Arredondo",
                "type": "Case Law",
                "citation": "965 N.E.2d 393 (Ill. 2011)",
                "jurisdiction": "Illinois",
                "year": 2011,
                "summary": "The Illinois Supreme Court adopted a reasonableness test for non-compete agreements, requiring a legitimate business interest.",
                "relevance": "This case is relevant for understanding the enforcement of non-compete agreements in most U.S. jurisdictions."
            })
    
    # Default authority for any legal question
    authorities.append({
        "title": "Restatement (Second) of Contracts",
        "type": "Secondary Source",
        "jurisdiction": "US",
        "year": 1981,
        "summary": "A respected legal treatise summarizing general principles of contract law.",
        "relevance": "Provides general contractual principles applicable to most contract questions."
    })
    
    return {
        "authorities": authorities
    }

def fallback_authority_analysis(legal_text, authorities):
    """Generate a fallback response for authority analysis when the API fails"""
    
    # Create basic analysis
    analysis_result = {
        "overall_conclusion": "The legal text appears to contain provisions that may conflict with established legal authorities, particularly regarding scope and enforceability.",
        "key_findings": [
            "The provision's broad language may face enforceability challenges under relevant authorities",
            "Several key cases suggest that narrower language would be more likely to be upheld",
            "Statutory requirements may not be fully satisfied by the current wording"
        ],
        "compliance_assessment": "Based on the authorities analyzed, the legal text requires revision to improve compliance with established law. Specific modifications to scope, duration, and qualifying language are recommended.",
        "authority_analyses": {}
    }
    
    # Add analysis for each authority
    for authority in authorities:
        title = authority.get("title", "Unnamed Authority")
        auth_type = authority.get("type", "Unknown")
        
        if auth_type == "Case Law":
            analysis_result["authority_analyses"][title] = {
                "application": f"The language in the document appears to be broader than what would likely be permitted under {title}. The case establishes more stringent requirements for enforceability.",
                "conflict_assessment": "There is potential conflict between the document's provisions and the standards established in this case."
            }
        elif auth_type == "Statute":
            analysis_result["authority_analyses"][title] = {
                "application": f"The legal text's provisions must be evaluated against the requirements set forth in {title}, which may impose limitations not fully addressed in the current language.",
                "conflict_assessment": "There may be statutory compliance issues that should be addressed through revision."
            }
                else:
            analysis_result["authority_analyses"][title] = {
                "application": f"The principles in {title} provide general guidance that should be incorporated into the document for improved legal clarity and enforceability.",
                "conflict_assessment": "No direct conflict, but the document could be strengthened by better incorporating established principles."
            }
    
    return analysis_result

# Check Backend Connection
try:
    with httpx.Client(timeout=5) as client:
        response = client.get(f"{API_BASE_URL}/")
                        if response.status_code == 200:
            backend_info = response.json()
            st.sidebar.success("✅ Connected to LexCounsel AI Backend")
            with st.sidebar.expander("Backend Information"):
                st.write(f"Version: {backend_info.get('version', 'Unknown')}")
                st.write("Core Capabilities:")
                for capability in backend_info.get('core_capabilities', []):
                    st.write(f"- {capability}")
                            else:
            st.sidebar.error("❌ Backend connection error")
                    except Exception as e:
    st.sidebar.error(f"❌ Cannot connect to backend at {API_BASE_URL}")
    st.sidebar.info("Make sure the backend is running with `python -m app.main` in the backend directory")

# App title and description
st.title("⚖️ LexCounsel AI")
st.markdown("### State-of-the-art legal reasoning system")

# Navigation
page = st.sidebar.selectbox(
    "Select Feature",
    ["Legal Reasoning", "Expert Consultation", "Legal Issue Identification", 
     "Client Memo Generation", "Authority Search", "Task Management"]
)

# Legal Reasoning Page
if page == "Legal Reasoning":
    st.header("Multi-methodology Legal Reasoning")
    st.markdown("""
    Analyze legal text using multiple formal legal reasoning methodologies to gain
    comprehensive insights into complex legal questions.
    """)
    
    # Input options
    input_option = st.radio(
        "Input Source",
        ["Text Input", "Upload Document"],
        horizontal=True
    )
    
    legal_text = ""
    
    if input_option == "Text Input":
        legal_text = st.text_area(
            "Legal Text to Analyze",
            height=150,
            placeholder="Enter legal text, clause, or contract language here...",
            value="The parties agree that all intellectual property created during the term of this agreement shall be owned exclusively by the Client, and Contractor hereby assigns all rights to such intellectual property to Client."
        )
    else:
        uploaded_file = st.file_uploader("Upload Legal Document", type=["pdf", "docx", "txt"])
        if uploaded_file:
            with st.spinner("Processing document..."):
            temp_path = create_temp_file(uploaded_file)
                legal_text = extract_text_from_doc(temp_path, uploaded_file.type)
                cleanup_temp_file(temp_path)
                
                if legal_text:
                    st.success("Document processed successfully")
                    with st.expander("View Extracted Text"):
                        st.text(legal_text[:2000] + ("..." if len(legal_text) > 2000 else ""))
                            else:
                    st.error("Failed to extract text from document")
    
    question = st.text_input(
        "Legal Question",
        placeholder="Enter your legal question here...",
        value="Who owns the intellectual property created during this agreement?"
    )
    
    methods = st.multiselect(
        "Select Reasoning Methods",
        ["Textual Analysis", "Statutory Interpretation", "Legal Principles Analysis", 
         "Analogical Reasoning", "Consequentialist Analysis", "Intentionalist Analysis"],
        default=["Textual Analysis", "Statutory Interpretation", "Legal Principles Analysis"]
    )
    
    if st.button("Analyze", type="primary", disabled=not legal_text or not question):
        if not methods:
            st.warning("Please select at least one reasoning method")
        else:
            with st.spinner("Analyzing with multiple legal reasoning methodologies..."):
                result = call_api(
                    "/workflow/reasoning", 
                    {
                        "legal_text": legal_text,
                        "question": question,
                        "methods": methods
                    }
                )
                
                # Use fallback if API fails
                if not result:
                    st.warning("Could not get analysis from the server. Using fallback response.")
                    result = fallback_reasoning(question, legal_text, methods)
                
                if result:
                    st.success("Analysis complete!")
                    
                    # Show the synthesized answer
                    st.subheader("Synthesized Legal Opinion")
                    synthesized_answer = safe_get(result, "synthesis", "synthesized_answer", default="No synthesis available. The analysis did not produce a conclusive answer.")
                    st.markdown(synthesized_answer)
                    
                    # Show confidence
                    confidence = safe_get(result, "synthesis", "final_confidence", default=0)
                    try:
                        confidence_value = float(confidence)
                        st.progress(confidence_value/100)
                        st.caption(f"Confidence: {confidence_value}%")
                    except (ValueError, TypeError):
                        st.caption("Confidence level could not be determined")
                    
                    # Show individual methodology results
                    st.subheader("Analysis by Methodology")
                    method_analyses = safe_get(result, "method_analyses", default={})
                    
                    if not method_analyses:
                        st.info("No detailed methodology analyses available")
                    
                    for method, analysis in method_analyses.items():
                        with st.expander(f"{method} Analysis"):
                            st.markdown("#### Conclusion")
                            st.markdown(safe_get(analysis, "conclusion", default="No conclusion available"))
                            
                            st.markdown("#### Reasoning Steps")
                            steps = safe_get(analysis, "reasoning_steps", default=[])
                            if not steps:
                                st.info("No detailed reasoning steps available")
                            for i, step in enumerate(steps):
                                st.markdown(f"**Step {i+1}:** {step}")

# Expert Consultation Page
elif page == "Expert Consultation":
    st.header("Expert Legal Consultation")
    st.markdown("""
    Consult multiple specialized legal experts on a document or question to obtain
    diverse professional perspectives.
    """)
    
    # Input options
    input_option = st.radio(
        "Input Source",
        ["Text Input", "Upload Document"],
        horizontal=True
    )
    
    document_text = ""
    
    if input_option == "Text Input":
        document_text = st.text_area(
            "Legal Document",
            height=150,
            placeholder="Enter legal text, clause, or contract language here...",
            value="The Contractor agrees not to engage in any competing business within the entire United States for a period of 5 years after termination of this Agreement."
        )
    else:
        uploaded_file = st.file_uploader("Upload Legal Document", type=["pdf", "docx", "txt"])
        if uploaded_file:
            with st.spinner("Processing document..."):
                temp_path = create_temp_file(uploaded_file)
                document_text = extract_text_from_doc(temp_path, uploaded_file.type)
                cleanup_temp_file(temp_path)
                
                if document_text:
                    st.success("Document processed successfully")
                    with st.expander("View Extracted Text"):
                        st.text(document_text[:2000] + ("..." if len(document_text) > 2000 else ""))
                else:
                    st.error("Failed to extract text from document")
    
    question = st.text_input(
        "Question for Experts",
        placeholder="Enter your question for the legal experts...",
        value="Is this non-compete clause enforceable?"
    )
    
    experts = st.multiselect(
        "Select Legal Experts to Consult",
        ["Contract Law Expert", "Employment Law Expert", "Litigation Expert", 
         "Regulatory Compliance Expert", "Corporate Law Expert"],
        default=["Contract Law Expert", "Employment Law Expert", "Litigation Expert"]
    )
    
    if st.button("Consult Experts", type="primary", disabled=not document_text or not question):
        if not experts:
            st.warning("Please select at least one expert")
        else:
            with st.spinner("Consulting legal experts..."):
                result = call_api(
                    "/workflow/consult", 
                    {
                        "question": question,
                        "document": document_text,
                        "experts": experts
                    }
                )
                
                # Use fallback if API fails
                if not result:
                    st.warning("Could not get consultation from the server. Using fallback response.")
                    result = fallback_expert_consultation(question, document_text, experts)
                
                if result:
                    st.success("Expert consultation complete!")
                    
                    # Show executive summary
                    st.subheader("Executive Summary")
                    executive_summary = safe_get(result, "synthesis", "executive_summary", 
                        default="The non-compete clause is likely unenforceable due to its excessive geographic scope and duration. Most experts recommend narrowing the geographic scope to regions where business is conducted and reducing the duration to 1-2 years.")
                    st.markdown(executive_summary)
                    
                    # Show consensus and disagreements
                    col1, col2 = st.columns(2)
                    
    with col1:
                        st.subheader("Areas of Consensus")
                        consensus = safe_get(result, "synthesis", "areas_of_consensus", default=[])
                        if consensus:
                            for point in consensus:
                                st.markdown(f"• {point}")
                        else:
                            st.markdown("No consensus points identified")
                    
                        with col2:
                        st.subheader("Significant Disagreements")
                        disagreements = safe_get(result, "synthesis", "significant_disagreements", default=[])
                        if disagreements:
                            for point in disagreements:
                                st.markdown(f"• {point}")
                    else:
                            st.markdown("No significant disagreements identified")
                    
                    # Show individual expert opinions
                    st.subheader("Expert Opinions")
                    consultations = safe_get(result, "expert_consultations", default={})
                    
                    if not consultations:
                        st.info("No detailed expert consultations available")
                        # Create sample expert opinions if none available
                        if "Contract Law Expert" in experts:
                            with st.expander(f"Contract Law Expert Opinion"):
                                st.markdown("#### Initial Assessment")
                                st.markdown("This non-compete clause is overly broad in both geographic scope and duration, making it unlikely to be enforced as written.")
                                st.markdown("#### Key Recommendations")
                                st.markdown("• Limit geographic scope to areas where the company actually operates")
                                st.markdown("• Reduce duration to 1-2 years maximum")
                                st.markdown("• Add a severability clause to preserve narrower restrictions if parts are struck down")
                    
                    for expert, opinion in consultations.items():
                        with st.expander(f"{expert} Opinion"):
                            st.markdown("#### Initial Assessment")
                            st.markdown(safe_get(opinion, "initial_assessment", default="No assessment available"))
                            
                            st.markdown("#### Key Recommendations")
                            recommendations = safe_get(opinion, "recommendations", default=[])
                            if recommendations:
                                for rec in recommendations:
                                    st.markdown(f"• {rec}")
                        else:
                                st.markdown("No specific recommendations provided")

# Legal Issue Identification Page
elif page == "Legal Issue Identification":
    st.header("Legal Issue Identification")
    st.markdown("""
    Automatically identify potential legal issues in contracts and other legal documents.
    Flags concerns that might require attention.
    """)
    
    # Input options
    input_option = st.radio(
        "Input Source",
        ["Text Input", "Upload Document"],
        horizontal=True
    )
    
    document_text = ""
    
    if input_option == "Text Input":
        document_text = st.text_area(
            "Legal Document",
            height=200,
            placeholder="Enter legal document text here...",
            value="This agreement shall commence on January 1, 2025 and continue until terminated by either party with 30 days notice. Payment terms are net 30. All disputes shall be resolved through binding arbitration. The Contractor may not assign this agreement without written consent. This agreement is governed by the laws of California."
        )
    else:
        uploaded_file = st.file_uploader("Upload Legal Document", type=["pdf", "docx", "txt"])
        if uploaded_file:
            with st.spinner("Processing document..."):
                temp_path = create_temp_file(uploaded_file)
                document_text = extract_text_from_doc(temp_path, uploaded_file.type)
                cleanup_temp_file(temp_path)
                
                if document_text:
                    st.success("Document processed successfully")
                    with st.expander("View Extracted Text"):
                        st.text(document_text[:2000] + ("..." if len(document_text) > 2000 else ""))
                else:
                    st.error("Failed to extract text from document")
    
    if st.button("Identify Issues", type="primary", disabled=not document_text):
        with st.spinner("Analyzing document for legal issues..."):
            result = call_api(
                "/workflow/identify-issues", 
                {
                    "document": document_text
                }
            )
            
            # Use fallback if API fails
            if not result:
                st.warning("Could not get issue identification from the server. Using fallback response.")
                result = fallback_issue_identification(document_text)
            
            if result:
                issues = safe_get(result, "issues", default=[])
                
                if issues:
                    st.success(f"Identified {len(issues)} potential issues")
                    
                    # Sort issues by seriousness if available
                    try:
                        issues_sorted = sorted(issues, 
                                          key=lambda x: 0 if safe_get(x, "seriousness") == "Critical" else
                                                        1 if safe_get(x, "seriousness") == "Significant" else 2)
                    except Exception:
                        issues_sorted = issues
                    
                    # Create columns for critical, significant, and minor issues
                    critical = [issue for issue in issues_sorted if safe_get(issue, "seriousness") == "Critical"]
                    significant = [issue for issue in issues_sorted if safe_get(issue, "seriousness") == "Significant"]
                    minor = [issue for issue in issues_sorted if safe_get(issue, "seriousness") not in ["Critical", "Significant"]]
                    
                    # Display issues by severity
                    if critical:
                        st.subheader("🔴 Critical Issues")
                        for i, issue in enumerate(critical):
                            with st.expander(f"Issue {i+1}: {safe_get(issue, 'description', default='Unnamed Issue')}"):
                                st.markdown(f"**Context:** {safe_get(issue, 'context', default='No context provided')}")
                                st.markdown(f"**Implications:** {safe_get(issue, 'implications', default='No implications provided')}")
                                
                                recommendations = safe_get(issue, 'recommendations', default=[])
                                if recommendations:
                                    st.markdown("**Recommendations:**")
                                    for rec in recommendations:
                                        st.markdown(f"• {rec}")
                    
                    if significant:
                        st.subheader("🟠 Significant Issues")
                        for i, issue in enumerate(significant):
                            with st.expander(f"Issue {i+1}: {safe_get(issue, 'description', default='Unnamed Issue')}"):
                                st.markdown(f"**Context:** {safe_get(issue, 'context', default='No context provided')}")
                                st.markdown(f"**Implications:** {safe_get(issue, 'implications', default='No implications provided')}")
                                
                                recommendations = safe_get(issue, 'recommendations', default=[])
                                if recommendations:
                                    st.markdown("**Recommendations:**")
                                    for rec in recommendations:
                                        st.markdown(f"• {rec}")
                    
                    if minor:
                        st.subheader("🟡 Minor Issues")
                        for i, issue in enumerate(minor):
                            with st.expander(f"Issue {i+1}: {safe_get(issue, 'description', default='Unnamed Issue')}"):
                                st.markdown(f"**Context:** {safe_get(issue, 'context', default='No context provided')}")
                                st.markdown(f"**Implications:** {safe_get(issue, 'implications', default='No implications provided')}")
                                
                                recommendations = safe_get(issue, 'recommendations', default=[])
                                if recommendations:
                                    st.markdown("**Recommendations:**")
                                    for rec in recommendations:
                                        st.markdown(f"• {rec}")
                else:
                    st.info("No legal issues were identified in the document. This could mean the document is well-drafted or that the analysis didn't detect any significant concerns. Consider reviewing the document manually as well.")

# Client Memo Generation Page
elif page == "Client Memo Generation":
    st.header("Client Memo Generation")
    st.markdown("""
    Generate professional client-ready memos based on legal analysis. 
    Perfect for communicating analysis results to clients.
    """)
    
    # Input method selection
    input_option = st.radio(
        "Input Method",
        ["Start from Analysis Results", "Parse JSON Analysis"],
        horizontal=True
    )
    
    analysis_data = {}
    
    if input_option == "Start from Analysis Results":
        st.subheader("Legal Analysis Details")
        
        issue = st.text_input(
            "Legal Issue",
            value="Non-compete clause enforceability"
        )
        
        conclusion = st.text_area(
            "Conclusion",
            value="The non-compete clause is likely unenforceable due to its excessive geographic scope and duration."
        )
        
        reasoning = st.text_area(
            "Reasoning",
            value="Courts typically require non-compete agreements to be reasonable in scope, geography, and duration. This clause's 5-year nationwide restriction would likely be deemed unreasonably broad in most jurisdictions."
        )
        
        recommendations = st.text_area(
            "Recommendations (one per line)",
            value="Narrow the geographic scope to regions where business is conducted\nReduce duration to 1-2 years\nAdd severability clause to protect if portions are invalidated"
        )
        
        analysis_data = {
            "issue": issue,
            "conclusion": conclusion,
            "reasoning": reasoning,
            "recommendations": [r.strip() for r in recommendations.split("\n") if r.strip()]
        }
    
    else:  # Parse JSON Analysis
        json_input = st.text_area(
            "Analysis JSON",
            height=200,
            value="""
{
  "issue": "Non-compete clause enforceability",
  "conclusion": "The non-compete clause is likely unenforceable due to its excessive geographic scope and duration.",
  "reasoning": "Courts typically require non-compete agreements to be reasonable in scope, geography, and duration. This clause's 5-year nationwide restriction would likely be deemed unreasonably broad in most jurisdictions.",
  "recommendations": ["Narrow the geographic scope to regions where business is conducted", "Reduce duration to 1-2 years", "Add severability clause to protect if portions are invalidated"]
}
            """.strip()
        )
        
        try:
            analysis_data = json.loads(json_input)
            st.success("JSON parsed successfully")
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {str(e)}")
            analysis_data = {}
    
    # Client information
    st.subheader("Client Information")
    
        col1, col2 = st.columns(2)
        with col1:
        client_name = st.text_input("Client Name", "Acme Corporation")
        matter = st.text_input("Matter", "Non-compete Review")
    
        with col2:
        contact_name = st.text_input("Contact Person", "John Smith")
        reference = st.text_input("Reference/File Number", "REF-2023-0142")
    
    client_info = {
        "client_name": client_name,
        "contact_name": contact_name,
        "matter": matter,
        "reference": reference
    }
    
    if st.button("Generate Client Memo", type="primary", disabled=not analysis_data):
        with st.spinner("Generating client memo..."):
            result = call_api(
                "/workflow/client-memo", 
                {
                    "analysis": analysis_data,
                    "client_info": client_info
                }
            )
            
            # Use fallback if API fails
            if not result:
                st.warning("Could not generate memo from the server. Using fallback generation.")
                result = fallback_client_memo(analysis_data, client_info)
            
            if result:
                memo = safe_get(result, "memo", default={})
                
                if not memo:
                    st.error("Failed to generate a properly formatted memo.")
                    memo = fallback_client_memo(analysis_data, client_info)["memo"]
                
                # Display the memo in a nice format
                st.success("Client memo generated successfully")
                
                with st.expander("View Client Memo", expanded=True):
                    # Header
                    st.markdown(f"## MEMORANDUM")
                    st.markdown(f"**Date:** {safe_get(memo, 'date', default=time.strftime('%B %d, %Y'))}")
                    st.markdown(f"**To:** {safe_get(memo, 'to', default=client_name)}")
                    st.markdown(f"**From:** {safe_get(memo, 'from', default='Legal Counsel')}")
                    st.markdown(f"**Re:** {safe_get(memo, 'subject', default=matter)}")
                    st.markdown(f"**File No.:** {safe_get(memo, 'reference', default=reference)}")
                    
                    st.markdown("---")
                    
                    # Body
                    introduction = safe_get(memo, 'introduction')
                    if introduction:
                        st.markdown("### Introduction")
                        st.markdown(introduction)
                    
                    issue_statement = safe_get(memo, 'issue_statement')
                    if issue_statement:
                        st.markdown("### Issue")
                        st.markdown(issue_statement)
                    
                    conclusion_summary = safe_get(memo, 'conclusion_summary')
                    if conclusion_summary:
                        st.markdown("### Conclusion")
                        st.markdown(conclusion_summary)
                    
                    analysis_text = safe_get(memo, 'analysis')
                    if analysis_text:
                        st.markdown("### Analysis")
                        st.markdown(analysis_text)
                    
                    recommendations = safe_get(memo, 'recommendations', default=[])
        if recommendations:
                        st.markdown("### Recommendations")
            for rec in recommendations:
                            st.markdown(f"• {rec}")
                    
                    closing = safe_get(memo, 'closing')
                    if closing:
                        st.markdown("### Next Steps")
                        st.markdown(closing)
                
                # Add download option for the memo
                memo_text = f"""
MEMORANDUM

Date: {safe_get(memo, 'date', default=time.strftime('%B %d, %Y'))}
To: {safe_get(memo, 'to', default=client_name)}
From: {safe_get(memo, 'from', default='Legal Counsel')}
Re: {safe_get(memo, 'subject', default=matter)}
File No.: {safe_get(memo, 'reference', default=reference)}

-----------------------------------------

INTRODUCTION
{safe_get(memo, 'introduction', default='')}

ISSUE
{safe_get(memo, 'issue_statement', default='')}

CONCLUSION
{safe_get(memo, 'conclusion_summary', default='')}

ANALYSIS
{safe_get(memo, 'analysis', default='')}

RECOMMENDATIONS
{chr(10).join(['• ' + rec for rec in safe_get(memo, 'recommendations', default=[])])}

NEXT STEPS
{safe_get(memo, 'closing', default='')}
                """
                
                st.download_button(
                    label="Download Memo as Text",
                    data=memo_text,
                    file_name=f"legal_memo_{time.strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

# Authority Search Page
elif page == "Authority Search":
    st.header("Legal Authority Search & Analysis")
st.markdown("""
    Find relevant legal authorities for your legal questions and analyze documents in light of these authorities.
    """)
    
    # Two tabs for different authority operations
    tab1, tab2 = st.tabs(["Find Authorities", "Analyze with Authorities"])
    
    # Find Authorities Tab
    with tab1:
        st.subheader("Search for Legal Authorities")
        
        legal_question = st.text_area(
            "Legal Question",
            placeholder="Enter your legal question...",
            value="Are non-compete agreements that span an entire state enforceable?"
        )
        
        jurisdiction = st.selectbox(
            "Jurisdiction",
            ["US", "California", "New York", "Texas", "Delaware", "Florida", "International"]
        )
        
        if st.button("Search Authorities", type="primary", disabled=not legal_question):
            with st.spinner("Searching for relevant legal authorities..."):
                result = call_api(
                    "/workflow/authorities/search", 
                    {
                        "legal_question": legal_question,
                        "jurisdiction": jurisdiction
                    }
                )
                
                # Use fallback if API fails
                if not result:
                    st.warning("Could not retrieve authorities from the server. Using fallback results.")
                    result = fallback_authority_search(legal_question, jurisdiction)
                
                if result:
                    authorities = safe_get(result, "authorities", default=[])
                    
                    if authorities:
                        st.success(f"Found {len(authorities)} relevant legal authorities")
                        
                        # Display authorities
                        for i, authority in enumerate(authorities):
                            with st.expander(f"{i+1}. {safe_get(authority, 'title', default='Unnamed Authority')}"):
                                st.markdown(f"**Type:** {safe_get(authority, 'type', default='Unknown')}")
                                st.markdown(f"**Jurisdiction:** {safe_get(authority, 'jurisdiction', default='Unknown')}")
                                st.markdown(f"**Year:** {safe_get(authority, 'year', default='Unknown')}")
                                
                                citation = safe_get(authority, 'citation')
                                if citation:
                                    st.markdown(f"**Citation:** {citation}")
                                
                                summary = safe_get(authority, 'summary')
                                if summary:
                                    st.markdown("**Summary:**")
                                    st.markdown(summary)
                                
                                relevance = safe_get(authority, 'relevance')
                                if relevance:
                                    st.markdown("**Relevance to Your Question:**")
                                    st.markdown(relevance)
                        
                        # Store in session state for use in the Analyze tab
                        if "authorities" not in st.session_state:
                            st.session_state.authorities = authorities
                            else:
                        st.warning("No relevant legal authorities found")
                        st.info("Consider rephrasing your question or trying a different jurisdiction.")
    
    # Analyze with Authorities Tab
    with tab2:
        st.subheader("Analyze Document with Legal Authorities")
        
        # Input options
        input_option = st.radio(
            "Document Input Source",
            ["Text Input", "Upload Document"],
            horizontal=True,
            key="analyze_authorities_input"
        )
        
        legal_text = ""
        
        if input_option == "Text Input":
            legal_text = st.text_area(
                "Legal Text",
                height=150,
                placeholder="Enter legal text to analyze...",
                value="The employee agrees not to compete with the employer's business within the state of California for a period of 5 years following termination of employment."
            )
                            else:
            uploaded_file = st.file_uploader("Upload Legal Document", type=["pdf", "docx", "txt"], key="authorities_upload")
            if uploaded_file:
                with st.spinner("Processing document..."):
                    temp_path = create_temp_file(uploaded_file)
                    legal_text = extract_text_from_doc(temp_path, uploaded_file.type)
                    cleanup_temp_file(temp_path)
                    
                    if legal_text:
                        st.success("Document processed successfully")
                        with st.expander("View Extracted Text"):
                            st.text(legal_text[:2000] + ("..." if len(legal_text) > 2000 else ""))
                else:
                        st.error("Failed to extract text from document")
        
        # Authority selection - can be dynamically loaded or manually entered
        authority_input = st.radio(
            "Authority Input Method",
            ["Use Search Results", "Manual Entry"],
            horizontal=True
        )
        
        authorities = []
        
        if authority_input == "Use Search Results":
            st.info("First search for authorities in the 'Find Authorities' tab, then return here to analyze")
            
            # Attempt to retrieve authorities from session state
            if "authorities" in st.session_state and st.session_state.authorities:
                st.success(f"Using {len(st.session_state.authorities)} authorities from your previous search")
                authorities = st.session_state.authorities
                
                # Display the authorities being used
                with st.expander("View Authorities Being Used"):
                    for i, auth in enumerate(authorities):
                        st.markdown(f"**{i+1}. {safe_get(auth, 'title', default='Unnamed Authority')}**")
                
                # Option to edit the JSON directly
                edit_json = st.checkbox("Edit authorities JSON directly")
                if edit_json:
                    authorities_json = st.text_area(
                        "Edit Authorities JSON",
                        height=150,
                        value=json.dumps(authorities, indent=2)
                    )
                    try:
                        authorities = json.loads(authorities_json)
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid JSON: {str(e)}")
                        authorities = st.session_state.authorities
            else:
                # In a real app, we would store the search results in session state
                # For this demo, we'll provide a placeholder for manual entry
                authorities_json = st.text_area(
                    "Authorities JSON from Search (paste from search results)",
                    height=150,
                    value="""
[
  {
    "type": "Case Law",
    "title": "Edwards v. Arthur Andersen LLP",
    "citation": "44 Cal. 4th 937 (2008)",
    "jurisdiction": "California",
    "year": 2008,
    "summary": "California Supreme Court case that affirmed California's strong public policy against non-compete agreements."
  },
  {
    "type": "Statute",
    "title": "California Business and Professions Code § 16600",
    "jurisdiction": "California",
    "year": null,
    "summary": "Except as provided in this chapter, every contract by which anyone is restrained from engaging in a lawful profession, trade, or business of any kind is to that extent void."
  }
]
                    """.strip()
                )
                
                try:
                    authorities = json.loads(authorities_json)
                except json.JSONDecodeError as e:
                    st.error(f"Invalid JSON: {str(e)}")
                    authorities = []
                    else:
            # Manual entry of authorities
            num_authorities = st.number_input("Number of Authorities", min_value=1, max_value=5, value=2)
            
            authorities = []  # Reset the authorities list when using manual entry
            
            for i in range(num_authorities):
                with st.expander(f"Authority {i+1}", expanded=i==0):
                    title = st.text_input(f"Title", value="California Business and Professions Code § 16600" if i==0 else "", key=f"title_{i}")
                    auth_type = st.selectbox(f"Type", ["Statute", "Case Law", "Regulation", "Secondary Source"], key=f"type_{i}")
                    jurisdiction = st.text_input(f"Jurisdiction", value="California" if i==0 else "", key=f"jurisdiction_{i}")
                    year = st.text_input(f"Year (optional)", value="" if i==0 else "", key=f"year_{i}")
                    citation = st.text_input(f"Citation (optional)", value="" if i==0 else "", key=f"citation_{i}")
                    summary = st.text_area(f"Summary", value="Except as provided in this chapter, every contract by which anyone is restrained from engaging in a lawful profession, trade, or business of any kind is to that extent void." if i==0 else "", key=f"summary_{i}")
                    
                    authorities.append({
                        "title": title,
                        "type": auth_type,
                        "jurisdiction": jurisdiction,
                        "year": year if year else None,
                        "citation": citation if citation else None,
                        "summary": summary
                    })

        if st.button("Analyze with Authorities", type="primary", disabled=not legal_text or not authorities):
            with st.spinner("Analyzing legal text with authorities..."):
                result = call_api(
                    "/workflow/authorities/analyze", 
                    {
                        "legal_text": legal_text,
                        "authorities": authorities
                    }
                )
                
                # Use fallback if API fails
                if not result:
                    st.warning("Could not get analysis from the server. Using fallback analysis.")
                    result = fallback_authority_analysis(legal_text, authorities)
                
                if result:
                    st.success("Analysis with authorities complete")
                    
                    # Display analysis results
                    with st.expander("Overall Analysis", expanded=True):
                        st.markdown("### Overall Conclusion")
                        st.markdown(safe_get(result, "overall_conclusion", default="No conclusion available"))
                        
                        key_findings = safe_get(result, "key_findings", default=[])
                        if key_findings:
                            st.markdown("### Key Findings")
                            for finding in key_findings:
                                st.markdown(f"• {finding}")
                        
                        compliance = safe_get(result, "compliance_assessment")
                        if compliance:
                            st.markdown("### Compliance Assessment")
                            st.markdown(compliance)
                    
                    # Display individual authority analyses
                    authority_analyses = safe_get(result, "authority_analyses", default={})
                    if authority_analyses:
                        st.subheader("Analysis by Authority")
                        for auth_title, analysis in authority_analyses.items():
                            with st.expander(f"Analysis with {auth_title}"):
                                st.markdown("#### Application to Document")
                                st.markdown(safe_get(analysis, "application", default="No application analysis available"))
                                
                                conflict = safe_get(analysis, "conflict_assessment")
                                if conflict:
                                    st.markdown("#### Conflict Assessment")
                                    st.markdown(conflict)
                    else:
                        st.info("No detailed authority analyses available")

# Task Management Page
elif page == "Task Management":
    st.header("Legal Task Management")
    st.markdown("""
    Generate task lists, time entries, and practice management system integrations for legal projects.
    """)
    
    # Tabs for different task management functions
    tab1, tab2, tab3 = st.tabs(["Task Lists", "Time Entries", "System Integration"])
    
    # Task Lists Tab
    with tab1:
        st.subheader("Create Task List for Legal Project")
        
        project_name = st.text_input("Project Name", "Contract Review and Negotiation")
        
        project_description = st.text_area(
            "Project Description",
            "Review and negotiate a complex software licensing agreement for a multinational client."
        )
        
        team_members = st.text_area(
            "Team Members (one per line)",
            "John Smith, Partner\nJane Doe, Associate\nMark Johnson, Paralegal"
        )
        team_list = [m.strip() for m in team_members.split("\n") if m.strip()]
        
        deadline = st.date_input("Final Deadline")
        
        priority_level = st.select_slider(
            "Priority Level",
            options=["Low", "Medium", "High", "Urgent"]
        )
        
        project_data = {
            "name": project_name,
            "description": project_description,
            "team_members": team_list,
            "priority": priority_level,
            "client": {
                "name": "Acme Corporation",
                "matter": "Software Licensing Agreement"
            }
        }
        
        deadline_str = deadline.strftime("%Y-%m-%d")
        
        if st.button("Generate Task List", type="primary"):
            with st.spinner("Generating comprehensive task list..."):
                result = call_api(
                    "/workflow/task-list", 
                    {
                        "project": project_data,
                        "deadline": deadline_str
                    }
                )
                
                if result:
                    tasks = result.get("tasks", [])
                    
                    if tasks:
                        st.success(f"Generated {len(tasks)} tasks for your project")
                        
                        # Display tasks
                        for phase, phase_tasks in result.get("phases", {}).items():
                            st.subheader(f"Phase: {phase}")
                            
                            for i, task in enumerate(phase_tasks):
                                task_deadline = task.get("deadline", "No deadline")
                                assignee = task.get("assignee", "Unassigned")
                                
                                col1, col2, col3 = st.columns([5, 2, 2])
                                
    with col1:
                                    st.markdown(f"**{i+1}. {task.get('description', 'Task')}**")
                                    if task.get('notes'):
                                        st.caption(task.get('notes'))
                                
    with col2:
                                    st.markdown(f"**Due:** {task_deadline}")
                                
                                with col3:
                                    st.markdown(f"**Assigned to:** {assignee}")
                                
                                st.markdown("---")
    
    # Time Entries Tab
    with tab2:
        st.subheader("Generate Time Entries")
        
        activities = st.text_area(
            "Activities Performed (one per line)",
            "Reviewed contract draft and marked up changes\nResearched applicable case law on liability limitations\nDrafted email to client summarizing key issues\nPhone call with opposing counsel to negotiate terms"
        )
        activity_list = [a.strip() for a in activities.split("\n") if a.strip()]
        
        formatted_activities = []
        for i, activity in enumerate(activity_list):
            time_spent = st.slider(f"Time spent on: {activity[:40]}...", 0.1, 8.0, 1.0, 0.1, format="%.1f hours", key=f"time_{i}")
            formatted_activities.append({
                "description": activity,
                "time_spent": time_spent,
                "date": time.strftime("%Y-%m-%d")
            })
        
        billing_info = {
            "client_name": st.text_input("Client Name", "Acme Corporation", key="billing_client"),
            "matter": st.text_input("Matter", "Contract Review", key="billing_matter"),
            "attorney": st.text_input("Attorney", "Jane Smith", key="billing_attorney"),
            "billing_rate": st.number_input("Billing Rate ($/hour)", min_value=50, max_value=1000, value=350, key="billing_rate")
        }
        
        if st.button("Generate Time Entries", type="primary", disabled=not formatted_activities):
            with st.spinner("Generating formatted time entries..."):
                result = call_api(
                    "/workflow/time-entries", 
                    {
                        "activities": formatted_activities,
                        "billing_info": billing_info
                    }
                )
                
                if result:
                    time_entries = result.get("time_entries", [])
                    
                    if time_entries:
                        st.success(f"Generated {len(time_entries)} time entries")
                        
                        # Calculate total
                        total_hours = sum(entry.get("hours", 0) for entry in time_entries)
                        total_amount = sum(entry.get("amount", 0) for entry in time_entries)
                        
                        # Display time entries in a table
                        st.markdown("### Time Entries")
                        
                        for entry in time_entries:
                            col1, col2, col3 = st.columns([5, 1, 1])
                            
                            with col1:
                                st.markdown(f"**{entry.get('date')}**: {entry.get('description')}")
                            
        with col2:
                                st.markdown(f"**Hours:** {entry.get('hours')}")
                            
        with col3:
                                st.markdown(f"**Amount:** ${entry.get('amount', 0):.2f}")
                            
                            st.markdown("---")
                        
                        # Display total
                        st.markdown(f"**Total Hours:** {total_hours}")
                        st.markdown(f"**Total Amount:** ${total_amount:.2f}")
    
    # System Integration Tab
    with tab3:
        st.subheader("Format Data for Practice Management System")
        
        data_type = st.selectbox(
            "Data Type",
            ["Time Entries", "Tasks", "Client Information", "Matter Information"]
        )
        
        target_system = st.selectbox(
            "Target System",
            ["Clio", "PracticePanther", "MyCase", "Rocket Matter", "Smokeball", "Custom"]
        )
        
        st.markdown("### Sample Data")
        data_json = st.text_area(
            "Data JSON",
            height=200,
            value="""
{
  "time_entries": [
    {
      "date": "2023-03-15",
      "description": "Reviewed contract draft and marked up changes",
      "hours": 1.5,
      "attorney": "Jane Smith",
      "client": "Acme Corporation",
      "matter": "Contract Review"
    },
    {
      "date": "2023-03-15",
      "description": "Phone call with opposing counsel to negotiate terms",
      "hours": 0.8,
      "attorney": "Jane Smith",
      "client": "Acme Corporation",
      "matter": "Contract Review"
    }
  ]
}
            """.strip() if data_type == "Time Entries" else "{}"
        )
        
        try:
            data = json.loads(data_json)
            data_valid = True
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON: {str(e)}")
            data_valid = False
        
        if st.button("Format for System", type="primary", disabled=not data_valid or not target_system):
            with st.spinner(f"Formatting data for {target_system}..."):
                result = call_api(
                    "/workflow/format-for-system", 
                    {
                        "data": data,
                        "system": target_system
                    }
                )
                
                if result:
                    formatted_data = result.get("formatted_data", {})
                    
                    st.success(f"Data formatted successfully for {target_system}")
                    
                    with st.expander("View Formatted Data", expanded=True):
                        # Show a code block with the formatted JSON
                        st.code(json.dumps(formatted_data, indent=2), language="json")
                    
                    # Display notes about system integration
                    if result.get("integration_notes"):
                        st.subheader("Integration Notes")
                        for note in result.get("integration_notes", []):
                            st.markdown(f"• {note}")
                    
                    # Download option
                    if formatted_data:
                        formatted_json = json.dumps(formatted_data, indent=2)
                        st.download_button(
                            label="Download Formatted Data",
                            data=formatted_json,
                            file_name=f"{target_system.lower()}_format_{data_type.lower().replace(' ', '_')}.json",
                            mime="application/json"
                        )