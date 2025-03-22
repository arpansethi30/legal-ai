import streamlit as st
import httpx
import os
import tempfile
import time
import google.generativeai as genai
from dotenv import load_dotenv
import json
import uuid
import docx2txt
import re
from pathlib import Path
import PyPDF2
from io import StringIO

# Set page config (must be the first Streamlit command)
st.set_page_config(
    page_title="Legal AI Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables for API keys
load_dotenv()

# Configure Gemini (as fallback)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Configuration
API_URL = "http://127.0.0.1:8000"  # FastAPI backend URL

# Initialize session state
if 'response_text' not in st.session_state:
    st.session_state.response_text = None
if 'document_content' not in st.session_state:
    st.session_state.document_content = None
if 'processing_time' not in st.session_state:
    st.session_state.processing_time = None

# Sidebar with app modes
st.sidebar.header("Legal AI Tools")
app_modes = ["Document Analysis", "Legal Queries", "Contract Comparison", "Legal Risk Assessment", "Contract Generator", "Legal Precedent Analysis"]
app_mode = st.sidebar.selectbox("Choose Mode", app_modes)

# Helper functions for file handling
def create_temp_file(uploaded_file):
    """Create a temporary file from an uploaded file"""
    try:
        # Create a temporary file
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            # Write the uploaded file to the temporary file
            tmp.write(uploaded_file.getvalue())
            return tmp.name
    except Exception as e:
        st.error(f"Error creating temporary file: {str(e)}")
        return None

def cleanup_temp_file(file_path):
    """Delete a temporary file"""
    try:
        if file_path and os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        st.warning(f"Error cleaning up temporary file: {str(e)}")

def extract_text_from_doc(file_path, mime_type):
    """Extract text from different document types"""
    try:
        if mime_type == 'application/pdf' or file_path.endswith('.pdf'):
            # Extract text from PDF
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text() + "\n\n"
            return text
        
        elif mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file_path.endswith('.docx'):
            # Extract text from DOCX
            return docx2txt.process(file_path)
        
        elif mime_type == 'text/plain' or file_path.endswith('.txt'):
            # Extract text from plain text file
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        
        else:
            st.warning(f"Unsupported file type: {mime_type}")
            return None
    except Exception as e:
        st.error(f"Error extracting text from document: {str(e)}")
        return None

def preprocess_text(text):
    """Preprocess text for analysis"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters and formatting specific to PDFs
    text = re.sub(r'[^\w\s\.\,\;\:\(\)\[\]\{\}\"\'\-\–\—\/\&\%\$\#\@\!\?\*\+\=\_\|\\]', '', text)
    
    return text.strip()

# About section
if app_mode == "About":
    st.markdown("## About Legal AI")
    
    st.markdown("""
    **Legal AI** is a multimodal AI assistant built for legal professionals, students, and anyone who needs help with legal documents or questions.
    """)
    
    # Features section
    st.markdown("### Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="feature-box"><h4>📄 Document Analysis</h4><p>Upload legal documents (PDFs or images) and get AI-powered analysis including summaries, key points, and risk identification.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-box"><h4>🧠 Advanced AI Models</h4><p>Powered by Google\'s Gemini models for state-of-the-art natural language understanding and document comprehension.</p></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="feature-box"><h4>❓ Legal Queries</h4><p>Ask questions about legal concepts, regulations, or document interpretation with optional context.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-box"><h4>🖼️ Multimodal Input</h4><p>Support for both text and image inputs to handle various document formats.</p></div>', unsafe_allow_html=True)
    
    # Technology section
    st.markdown("### Technology Stack")
    st.markdown("""
    - **Backend**: FastAPI with Python
    - **AI Models**: Google Gemini 1.5 (Flash for quick queries, Pro for complex analysis)
    - **Document Processing**: OCR with Tesseract, PDF processing
    
    ### Disclaimer
    
    This is a demo application built for a hackathon. The AI provides informational assistance only and is not a substitute for professional legal advice.
    """)
    
    # Usage examples
    st.markdown("### Example Use Cases")
    
    st.markdown("""
    1. **Contract Review**: Upload a contract to identify key terms, potential risks, and suggested modifications.
    
    2. **Legal Research**: Ask specific questions about legal concepts, precedents, or regulations.
    
    3. **Document Summarization**: Get concise summaries of lengthy legal documents.
    
    4. **Risk Assessment**: Identify potential legal issues in agreements or other documents.
    """)

# Document Analysis
elif app_mode == "Document Analysis":
    st.markdown("## Document Analysis")
    st.markdown('<div class="info-box">Upload a legal document (PDF or image) for AI analysis. The system will extract key information, summarize the document, and identify potential legal issues.</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload a legal document", type=["pdf", "png", "jpg", "jpeg"])
    
    custom_query = st.text_input("Ask a specific question about the document (optional)")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_button = st.button("Analyze Document", type="primary", disabled=uploaded_file is None)
    with col2:
        if st.button("View Example", disabled=uploaded_file is not None):
            st.session_state.response_text = """
# Document Analysis

## DOCUMENT SUMMARY
This Non-Disclosure Agreement (NDA) is between ABC Corp and XYZ Inc. dated January 15, 2023. It establishes a framework for the exchange of confidential information related to a potential business partnership. The agreement has a term of 3 years and includes standard provisions for protecting confidential information.

## KEY LEGAL POINTS
- **Definition of Confidential Information**: Broadly defines confidential information to include all non-public information shared between parties.
- **Exclusions**: Standard exclusions for information that becomes public, was already known, independently developed, or received from third parties.
- **Obligations**: Both parties must maintain confidentiality for 3 years and use information only for evaluating the potential business relationship.
- **Return of Materials**: Upon request, all confidential materials must be returned or destroyed.
- **Governing Law**: Agreement is governed by the laws of Delaware.

## POTENTIAL RISKS OR ISSUES
- The definition of "Confidential Information" is very broad and may include information that wasn't intended to be covered.
- There is no clear process for designating information as confidential (e.g., no marking requirements).
- The agreement lacks specific security measures for protecting electronic information.
- No provision addressing accidental disclosure or data breaches.
- No specific remedy provisions (such as injunctive relief) in case of breach.

## RECOMMENDATIONS
- Add specific requirements for marking or designating information as confidential
- Include provisions addressing data security requirements
- Add specific remedies for breach (e.g., injunctive relief)
- Consider adding a notification requirement for potential or actual data breaches
- Review the 3-year confidentiality period to ensure it's sufficient for your needs

---

**Disclaimer**: This analysis was generated by an AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel.
            """
            st.session_state.processing_time = 2.5
    
    if analyze_button and uploaded_file is not None:
        # Display loading state
        with st.spinner("Processing document and generating analysis..."):
            start_time = time.time()
            
            # Save to temp file
            temp_path = create_temp_file(uploaded_file)
            
            if temp_path:
                try:
                    # Prepare form data
                    files = {"file": (uploaded_file.name, open(temp_path, "rb"), uploaded_file.type)}
                    data = {}
                    
                    if custom_query:
                        data["query"] = custom_query
                    
                    # Send request to API
                    response = httpx.post(f"{API_URL}/api/document/analyze", files=files, data=data)
                    
                    # Clean up temp file
                    cleanup_temp_file(temp_path)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Calculate processing time
                        end_time = time.time()
                        st.session_state.processing_time = end_time - start_time
                        
                        # Display raw response for debugging
                        st.info(f"Raw response: {result}")
                        
                        # Store the response text
                        if result.get("analysis", {}).get("success", False):
                            st.session_state.response_text = result["analysis"]["analysis"]
                            
                            # Display some metadata
                            st.success(f"Successfully analyzed {uploaded_file.name}")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric(label="File Size", value=f"{uploaded_file.size / 1024:.1f} KB")
                            with col2:
                                st.metric(label="Text Extracted", value=f"{result.get('document', {}).get('text_length', 0)} chars")
                            with col3:
                                st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                            
                            # Display analysis
                            st.markdown('<div class="response-area">', unsafe_allow_html=True)
                            st.markdown(st.session_state.response_text)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Display model info
                            st.info(f"Model used: {result['analysis']['model_used']}")
                        else:
                            st.error(f"Analysis failed: {result.get('analysis', {}).get('error', 'Unknown error')}")
                    else:
                        st.error(f"Request failed with status code {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    cleanup_temp_file(temp_path)
    
    # Display previous analysis if available
    elif st.session_state.response_text and not analyze_button:
        # Display metadata
        if uploaded_file:
            st.success(f"Ready to analyze {uploaded_file.name}")
        elif st.session_state.processing_time:
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Example Document", value="NDA Contract")
            with col2:
                st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
        
        # Display analysis
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)

# Legal Queries
elif app_mode == "Legal Queries":
    st.markdown("## Legal Queries")
    st.markdown('<div class="info-box">Ask legal questions and get AI-powered answers. You can provide additional context or upload a document for more specific responses.</div>', unsafe_allow_html=True)
    
    # Initialize query in session state if not present
    if 'query' not in st.session_state:
        st.session_state.query = ""
    
    # Query input area
    query = st.text_area("Enter your legal question", 
                        height=100, 
                        placeholder="e.g., What are the key elements of a valid contract?",
                        value=st.session_state.query)
    
    # Update session state
    st.session_state.query = query
    
    # Context area
    col1, col2 = st.columns([2, 1])
    with col1:
        context = st.text_area("Provide additional context (optional)", height=100, placeholder="Any specific details or context for your question...")
    
    with col2:
        context_file = st.file_uploader("Upload a related document (optional)", type=["pdf", "png", "jpg", "jpeg"])
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query_button = st.button("Submit Query", type="primary", disabled=not query)
    with col2:
        # Use session state for the example query feature
        example_button = st.button("Example Query", disabled=bool(query))
        if example_button:
            st.session_state.query = "What are the key elements of a valid contract?"
            st.session_state.response_text = """
# Key Elements of a Valid Contract

A valid contract requires several essential elements to be legally enforceable:

## 1. Offer and Acceptance
There must be a clear offer from one party and an unambiguous acceptance by the other party, creating a "meeting of the minds" (mutual assent). The acceptance must mirror the terms of the offer.

## 2. Consideration
Each party must provide something of value (consideration) to the other. This could be money, goods, services, or even a promise to do or not do something. Consideration distinguishes a contract from a gift.

## 3. Legal Capacity
All parties must have the legal ability to enter the contract. This typically means they must:
- Be of legal age (usually 18+)
- Be of sound mind (mentally competent)
- Not be under the influence of substances that impair judgment
- Not be under duress or undue influence

## 4. Legal Purpose
The contract must be for a legal purpose. Contracts for illegal activities are void and unenforceable.

## 5. Mutual Intent
The parties must intend to create a legally binding relationship. Some agreements, like social arrangements, may not be intended as contracts.

## 6. Certainty of Terms
The contract must be clear and specific enough that its essential terms can be determined. Vague or ambiguous agreements may be unenforceable.

Some contracts must also be in writing to be enforceable under the Statute of Frauds, including contracts:
- Involving real estate
- That cannot be performed within one year
- For the sale of goods over a certain value (usually $500)
- To pay someone else's debt

---

**Disclaimer**: This response was generated by an AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel.
            """
            st.experimental_rerun()
    
    if query_button and query:
        # Display loading state
        with st.spinner("Processing your query..."):
            start_time = time.time()
            
            # Prepare form data
            data = {"query": query}
            files = {}
            temp_path = None
            
            if context:
                data["context"] = context
                
            # Handle optional document upload
            if context_file:
                temp_path = create_temp_file(context_file)
                if temp_path:
                    files = {"file": (context_file.name, open(temp_path, "rb"), context_file.type)}
            
            try:
                # Check API availability first
                try:
                    st.info(f"Checking API availability at {API_URL}/healthcheck...")
                    health_check = httpx.get(f"{API_URL}/healthcheck", timeout=3.0)
                    api_available = health_check.status_code == 200
                    st.success(f"API check result: {health_check.status_code} - {'Available' if api_available else 'Unavailable'}")
                except Exception as e:
                    # Also try alternative endpoint
                    try:
                        st.info(f"Trying alternative endpoint at {API_URL}/")
                        health_check = httpx.get(f"{API_URL}/", timeout=3.0)
                        api_available = health_check.status_code == 200
                        st.success(f"API check result: {health_check.status_code} - {'Available' if api_available else 'Unavailable'}")
                    except Exception as e2:
                        api_available = False
                        st.error(f"API check error: {str(e2)}")
                
                if not api_available:
                    st.error("API service is not available. Please check the backend server status.")
                    st.info("Trying direct Gemini fallback...")
                    
                    # Try using Gemini directly as fallback
                    answer, error = query_gemini_directly(query, context)
                    
                    if answer:
                        st.success("Successfully used direct Gemini fallback!")
                        st.session_state.response_text = answer
                        
                        # Calculate mock processing time
                        end_time = time.time()
                        st.session_state.processing_time = end_time - start_time
                        
                        # Clean up temp file if created
                        if temp_path:
                            cleanup_temp_file(temp_path)
                        
                        # Display fallback response
                        st.markdown('<div class="response-area">', unsafe_allow_html=True)
                        st.markdown(st.session_state.response_text)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"Gemini fallback also failed: {error}")
                        st.info("Using example response since all attempts failed.")
                        
                        # Provide a fallback example response if all else fails
                        st.session_state.response_text = f"""
# Response to: {query}

I'm sorry, but I cannot provide a real-time response as the Legal AI backend service is currently unavailable. 

## Troubleshooting Steps
1. Make sure the FastAPI backend is running at {API_URL}
2. Check if the correct endpoint is configured (/api/query)
3. Ensure network connectivity between the Streamlit app and the API server

Please try again later or contact the system administrator for assistance.

---

**Note**: This is an automatically generated fallback response.
                        """
                        
                        # Calculate mock processing time
                        end_time = time.time()
                        st.session_state.processing_time = end_time - start_time
                        
                        # Clean up temp file if created
                        if temp_path:
                            cleanup_temp_file(temp_path)
                        
                        # Display fallback response
                        st.markdown('<div class="response-area">', unsafe_allow_html=True)
                        st.markdown(st.session_state.response_text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        continue_execution = False
                else:
                    continue_execution = True
                
                if continue_execution:
                    # Send request to API - update endpoint to match backend
                    st.info(f"Sending query to {API_URL}/api/query")
                    response = httpx.post(f"{API_URL}/api/query", data=data, files=files, timeout=30.0)
                    
                    # Log response details for debugging
                    st.info(f"Response status: {response.status_code}")
                    st.info(f"Response headers: {dict(response.headers)}")
                    
                    # Clean up temp file if created
                    if temp_path:
                        cleanup_temp_file(temp_path)
                    
                    # Calculate processing time
                    end_time = time.time()
                    st.session_state.processing_time = end_time - start_time
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            # Display raw response for debugging
                            st.info(f"Raw response: {result}")
                            
                            # Handle different possible response formats
                            if "response" in result and result["response"].get("success", False):
                                # Format 1: {"response": {"success": true, "answer": "..."}}
                                st.session_state.response_text = result["response"]["answer"]
                                model_used = result["response"].get("model_used", "unknown")
                            elif "success" in result and result.get("success", False):
                                # Format 2: {"success": true, "answer": "..."}
                                st.session_state.response_text = result.get("answer", "")
                                model_used = result.get("model_used", "unknown")
                            elif "data" in result and result.get("data", {}).get("success", False):
                                # Format 3: {"data": {"success": true, "answer": "..."}}
                                st.session_state.response_text = result["data"].get("answer", "")
                                model_used = result["data"].get("model_used", "unknown")
                            else:
                                st.error(f"Unexpected response format: {result}")
                                # Try to extract any text we can find
                                for key in ["answer", "text", "response", "result", "content"]:
                                    if key in result:
                                        st.session_state.response_text = result[key]
                                        break
                                else:
                                    st.session_state.response_text = "Received response in unknown format. Please check server logs."
                                model_used = "unknown"
                            
                            # Display metadata
                            st.success("Query processed successfully")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(label="Model Used", value=model_used.split("-")[-1].capitalize() if "-" in model_used else model_used)
                            with col2:
                                st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                            
                            # Display analysis
                            st.markdown('<div class="response-area">', unsafe_allow_html=True)
                            st.markdown(st.session_state.response_text)
                            st.markdown('</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"An error occurred: {str(e)}")
                    elif response.status_code == 404:
                        st.error("API endpoint not found. Please check if the correct endpoint is configured.")
                        st.info(f"The request was sent to: {API_URL}/api/query")
                        st.info("You may need to update the API configuration or ensure the backend has the correct routes.")
                    else:
                        st.error(f"Request failed with status code {response.status_code}")
                        try:
                            error_details = response.json()
                            st.error(f"Error details: {error_details}")
                        except:
                            st.error(f"Response text: {response.text}")
            except httpx.TimeoutException:
                st.error("Request timed out. The API server may be overloaded or unavailable.")
                if temp_path:
                    cleanup_temp_file(temp_path)
            except httpx.ConnectError:
                st.error(f"Could not connect to the API server at {API_URL}.")
                st.info("Please check if the backend server is running and accessible.")
                if temp_path:
                    cleanup_temp_file(temp_path)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if temp_path:
                    cleanup_temp_file(temp_path)
    
    # Display previous response if available
    elif st.session_state.response_text and not query_button:
        # Display analysis
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)

# Contract Comparison
elif app_mode == "Contract Comparison":
    st.markdown("## Contract Comparison")
    st.markdown('<div class="info-box">Upload two legal documents to compare their clauses, identify differences, and understand the legal implications of those differences.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Document 1")
        doc1 = st.file_uploader("Upload first document", type=["pdf", "docx", "txt"], key="doc1")
    
    with col2:
        st.markdown("### Document 2")
        doc2 = st.file_uploader("Upload second document", type=["pdf", "docx", "txt"], key="doc2")
    
    comparison_focus = st.multiselect(
        "Focus comparison on specific aspects (optional)",
        ["Liability Clauses", "Payment Terms", "Termination Conditions", "Intellectual Property", "Confidentiality", "Jurisdiction", "All Clauses"],
        default=["All Clauses"]
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        compare_button = st.button("Compare Documents", type="primary", disabled=not (doc1 and doc2))
    with col2:
        if st.button("View Example", disabled=(doc1 is not None or doc2 is not None)):
            st.session_state.response_text = """
# Contract Comparison Analysis

## SUMMARY OF DIFFERENCES
This analysis compares two versions of a consulting agreement. The updated version (Document 2) contains several significant modifications that shift more risk to the consultant and provide additional protections for the client.

## KEY DIFFERENCES

### 1. Liability Clauses
- **Document 1**: Consultant's liability was capped at the total fees paid.
- **Document 2**: Liability cap has been removed, creating unlimited liability for the consultant.
- **Legal Impact**: Significantly increases consultant's risk exposure.

### 2. Payment Terms
- **Document 1**: Payment due within 30 days of invoice.
- **Document 2**: Payment due within 45 days of invoice with 15-day client review period.
- **Legal Impact**: Extends payment timeline and adds potential for payment delays.

### 3. Intellectual Property
- **Document 1**: Client owns deliverables; consultant retains pre-existing IP.
- **Document 2**: Client owns all IP created during the engagement including methodologies.
- **Legal Impact**: Consultant loses rights to techniques and approaches developed during the project.

### 4. Termination
- **Document 1**: Either party may terminate with 30 days' notice.
- **Document 2**: Client may terminate immediately; consultant requires 60 days' notice.
- **Legal Impact**: Creates unbalanced termination rights favoring the client.

## RISK ASSESSMENT
- The revised agreement (Document 2) increases consultant risk exposure by approximately 65%.
- The unlimited liability provision presents the most significant risk factor.
- The expanded IP assignment could impact consultant's future business opportunities.

## RECOMMENDATIONS
1. Negotiate reinstatement of a reasonable liability cap
2. Modify IP clause to clearly exclude consultant's methodologies and tools
3. Seek more balanced termination provisions
4. Consider requesting higher compensation given the increased risk profile

---

**Disclaimer**: This comparison was generated by an AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel.
            """
            st.session_state.processing_time = 3.2
    
    if compare_button and doc1 is not None and doc2 is not None:
        # Display loading state
        with st.spinner("Analyzing and comparing documents..."):
            start_time = time.time()
            
            # Save to temp files
            temp_path1 = create_temp_file(doc1)
            temp_path2 = create_temp_file(doc2)
            
            if temp_path1 and temp_path2:
                try:
                    # Prepare form data
                    files = {
                        "file1": (doc1.name, open(temp_path1, "rb"), doc1.type),
                        "file2": (doc2.name, open(temp_path2, "rb"), doc2.type)
                    }
                    
                    data = {"focus_areas": ",".join(comparison_focus) if "All Clauses" not in comparison_focus else ""}
                    
                    # Send request to API
                    st.info(f"Sending comparison request to {API_URL}/api/document/compare")
                    try:
                        response = httpx.post(f"{API_URL}/api/document/compare", files=files, data=data, timeout=60.0)
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Calculate processing time
                            end_time = time.time()
                            st.session_state.processing_time = end_time - start_time
                            
                            if result.get("success", False):
                                st.session_state.response_text = result.get("comparison", {}).get("analysis", "")
                                
                                # Display metadata
                                st.success("Comparison completed successfully")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric(label="Documents Analyzed", value="2")
                                with col2:
                                    st.metric(label="Differences Found", value=result.get("comparison", {}).get("diff_count", "N/A"))
                                with col3:
                                    st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                                
                                # Display analysis
                                st.markdown('<div class="response-area">', unsafe_allow_html=True)
                                st.markdown(st.session_state.response_text)
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.error(f"Comparison failed: {result.get('error', 'Unknown error')}")
                        else:
                            # Fallback to direct Gemini comparison if API fails
                            st.warning("API endpoint not available. Using direct Gemini comparison as fallback.")
                            st.session_state.response_text = """
# Contract Comparison Analysis

## SUMMARY OF DIFFERENCES
The comparison found several differences between the documents that may have legal significance. 

## KEY DIFFERENCES
(Differences would be displayed here in a real comparison)

## RISK ASSESSMENT
A thorough risk assessment would be provided here.

## RECOMMENDATIONS
Specific recommendations would be provided here.

---

**Note**: This is a fallback response as the detailed comparison service is currently unavailable.
**Disclaimer**: This comparison was generated by an AI assistant and should not be considered legal advice.
                            """
                            # Calculate processing time
                            end_time = time.time()
                            st.session_state.processing_time = end_time - start_time
                            
                            # Display analysis
                            st.markdown('<div class="response-area">', unsafe_allow_html=True)
                            st.markdown(st.session_state.response_text)
                            st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error during comparison: {str(e)}")
                        
                        # Calculate processing time
                        end_time = time.time()
                        st.session_state.processing_time = end_time - start_time
                        
                        # Try direct Gemini comparison
                        st.warning("Using Gemini fallback for document comparison")
                        st.session_state.response_text = """
# Contract Comparison Analysis

## SUMMARY OF DIFFERENCES
The AI attempted to compare your documents but encountered an issue with the comparison service.

## RECOMMENDATIONS
1. Try uploading the documents in a different format (e.g., PDF or plain text)
2. Ensure documents are properly formatted and readable
3. Try again later when the service is fully operational

---

**Note**: This is a fallback response as the comparison service encountered an error.
                        """
                        # Display analysis
                        st.markdown('<div class="response-area">', unsafe_allow_html=True)
                        st.markdown(st.session_state.response_text)
                        st.markdown('</div>', unsafe_allow_html=True)
                finally:
                    # Clean up temp files
                    cleanup_temp_file(temp_path1)
                    cleanup_temp_file(temp_path2)
    
    # Display previous analysis if available
    elif st.session_state.response_text and not compare_button:
        # Display metadata from example
        if st.session_state.processing_time:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Documents Analyzed", value="2")
            with col2:
                st.metric(label="Differences Found", value="4 major, 8 minor")
            with col3:
                st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
        
        # Display analysis
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)

# Legal Risk Assessment
elif app_mode == "Legal Risk Assessment":
    st.markdown("## Legal Risk Assessment")
    st.markdown('<div class="info-box">Upload a legal document to receive a comprehensive risk assessment with risk scores and recommendations for improvement.</div>', unsafe_allow_html=True)
    
    # File upload
    uploaded_file = st.file_uploader("Upload a legal document", type=["pdf", "docx", "txt"])
    
    # Risk categories
    st.markdown("### Assessment Focus (Optional)")
    col1, col2 = st.columns(2)
    with col1:
        risk_categories = [
            "Liability & Indemnification",
            "Intellectual Property",
            "Payment Terms",
            "Termination Clauses",
            "Confidentiality",
            "Regulatory Compliance"
        ]
        selected_categories = st.multiselect(
            "Select specific risk areas to focus on",
            risk_categories,
            default=[]
        )
    
    with col2:
        assessment_depth = st.slider("Assessment Depth", min_value=1, max_value=5, value=3, 
                                   help="Higher values provide more thorough analysis but may take longer")
        jurisdiction = st.selectbox(
            "Primary Jurisdiction (Optional)",
            ["", "United States", "European Union", "United Kingdom", "Canada", "Australia", "Other"]
        )
    
    # Analysis button
    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_button = st.button("Analyze Document", type="primary", disabled=not uploaded_file)
    with col2:
        if st.button("View Example", disabled=uploaded_file is not None):
            st.session_state.response_text = """
# Legal Risk Assessment Report

## EXECUTIVE SUMMARY
This NDA contains **moderate to high risk** elements that could expose the company to potential legal vulnerabilities. The agreement scored **68/100** on our risk scale, with several critical provisions requiring attention.

## RISK SCORES BY CATEGORY

| Category | Risk Score | Risk Level |
|----------|------------|------------|
| Liability & Indemnification | 76/100 | 🔴 High |
| Intellectual Property | 45/100 | 🟢 Low |
| Confidentiality Terms | 62/100 | 🟡 Medium |
| Term & Termination | 83/100 | 🔴 High |
| Enforceability | 58/100 | 🟡 Medium |
| Jurisdiction & Venue | 70/100 | 🟡 Medium |

## KEY RISK FACTORS

### 1. Unlimited Liability (High Risk)
- The agreement imposes unlimited liability without any cap or limitation.
- **Recommendation**: Add a liability cap proportional to contract value.

### 2. One-Sided Termination Rights (High Risk)
- Only the disclosing party can terminate the agreement.
- **Recommendation**: Incorporate mutual termination rights with reasonable notice periods.

### 3. Overly Broad Confidentiality Provisions (Medium Risk)
- The definition of confidential information lacks sufficient clarity.
- **Recommendation**: Narrow the definition with specific exclusions for public information.

### 4. Jurisdiction Issues (Medium Risk)
- The governing law provision specifies California law but your primary operations are in Texas.
- **Recommendation**: Align jurisdiction with your primary place of business.

## RISK MITIGATION RECOMMENDATIONS
1. Incorporate a liability cap of no more than 2x the value of the business relationship
2. Add mutual termination rights with 30-day notice period
3. Refine confidentiality provisions with standard exclusions
4. Update jurisdiction to Texas or add multi-jurisdiction provisions
5. Include a formal dispute resolution process prior to litigation

## REGULATORY COMPLIANCE CHECK
- This agreement would likely be enforceable but may create unnecessary risk exposure
- No major regulatory conflicts found with selected jurisdiction (United States)

---

**Disclaimer**: This risk assessment was generated by an AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel.
            """
            st.session_state.processing_time = 2.6
    
    if analyze_button and uploaded_file is not None:
        # Display loading state
        with st.spinner("Analyzing document for legal risks..."):
            start_time = time.time()
            
            # Save to temp file
            temp_path = create_temp_file(uploaded_file)
            
            if temp_path:
                try:
                    # Prepare form data
                    files = {
                        "file": (uploaded_file.name, open(temp_path, "rb"), uploaded_file.type)
                    }
                    
                    data = {
                        "categories": ",".join(selected_categories) if selected_categories else "all",
                        "depth": assessment_depth,
                        "jurisdiction": jurisdiction
                    }
                    
                    # Send request to API
                    st.info(f"Sending risk assessment request to {API_URL}/api/document/risk-assessment")
                    try:
                        response = httpx.post(f"{API_URL}/api/document/risk-assessment", files=files, data=data, timeout=60.0)
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Calculate processing time
                            end_time = time.time()
                            st.session_state.processing_time = end_time - start_time
                            
                            if result.get("success", False):
                                assessment = result.get("assessment", {})
                                st.session_state.response_text = assessment.get("report", "")
                                
                                # Display metrics
                                st.success("Risk assessment completed successfully")
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric(label="Overall Risk Score", value=f"{assessment.get('overall_score', 'N/A')}/100")
                                with col2:
                                    st.metric(label="Risk Level", value=assessment.get("risk_level", "N/A"))
                                with col3:
                                    st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                                
                                # Display full report
                                st.markdown('<div class="response-area">', unsafe_allow_html=True)
                                st.markdown(st.session_state.response_text)
                                st.markdown('</div>', unsafe_allow_html=True)
                            else:
                                st.error(f"Assessment failed: {result.get('error', 'Unknown error')}")
                        else:
                            # Fallback to direct Gemini analysis if API fails
                            st.warning("API endpoint not available. Using direct Gemini analysis as fallback.")
                            
                            # Try direct Gemini risk assessment
                            text_content = extract_text_from_doc(temp_path, uploaded_file.type)
                            if text_content:
                                prompt = f"""
You are a legal risk assessment expert. Analyze the following legal document and provide:
1. An overall risk score out of 100
2. Risk scores by category (Liability, IP, Confidentiality, Termination, etc.)
3. Key risk factors identified
4. Specific recommendations to mitigate each risk
5. Format your response in markdown with clear sections

Document text:
{text_content[:5000]}  # Limiting text length for prompt size
"""
                                try:
                                    if GEMINI_API_KEY:
                                        genai.configure(api_key=GEMINI_API_KEY)
                                        model = genai.GenerativeModel('gemini-pro')
                                        response = model.generate_content(prompt)
                                        
                                        # Calculate processing time
                                        end_time = time.time()
                                        st.session_state.processing_time = end_time - start_time
                                        
                                        st.session_state.response_text = response.text
                                        
                                        # Display metrics
                                        st.success("Risk assessment completed successfully (via Gemini)")
                                        st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                                        
                                        # Display full report
                                        st.markdown('<div class="response-area">', unsafe_allow_html=True)
                                        st.markdown(st.session_state.response_text)
                                        st.markdown('</div>', unsafe_allow_html=True)
                                    else:
                                        # If no API key for Gemini, provide generic response
                                        st.error("Unable to access direct model. Displaying generic risk assessment.")
                                        st.session_state.response_text = """
# Legal Risk Assessment Report

## EXECUTIVE SUMMARY
The risk assessment service encountered an issue analyzing your document.

## RISK FACTORS
The system was unable to complete a detailed risk analysis of your document.

## RECOMMENDATIONS
1. Try uploading the document in a different format (e.g., PDF or plain text)
2. Ensure the document is properly formatted and readable
3. Try again later when the service is fully operational

---

**Note**: This is a fallback response as the risk assessment service is currently unavailable.
                                        """
                                        # Display full report
                                        st.markdown('<div class="response-area">', unsafe_allow_html=True)
                                        st.markdown(st.session_state.response_text)
                                        st.markdown('</div>', unsafe_allow_html=True)
                                except Exception as e:
                                    st.error(f"Error with fallback assessment: {str(e)}")
                            else:
                                st.error("Could not extract text from document for fallback assessment.")
                    except Exception as e:
                        st.error(f"Error during risk assessment: {str(e)}")
                finally:
                    # Clean up temp file
                    cleanup_temp_file(temp_path)
    
    # Display previous assessment if available
    elif st.session_state.response_text and not analyze_button:
        # Display metrics from example
        if st.session_state.processing_time:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Overall Risk Score", value="68/100")
            with col2:
                st.metric(label="Risk Level", value="Moderate-High")
            with col3:
                st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
        
        # Display analysis
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)

# Contract Generator
elif app_mode == "Contract Generator":
    st.markdown("## Contract Generator")
    st.markdown('<div class="info-box">Generate customized legal contracts by answering a few simple questions. The AI will create a tailored document based on your specific needs.</div>', unsafe_allow_html=True)
    
    # Contract type selection
    contract_type = st.selectbox(
        "Select Contract Type",
        [
            "Non-Disclosure Agreement (NDA)",
            "Consulting Agreement",
            "Employment Agreement",
            "Services Agreement",
            "Software License Agreement",
            "Partnership Agreement",
            "Sales Contract"
        ]
    )
    
    # Create form for contract details
    with st.form("contract_form"):
        st.markdown("### Contract Details")
        
        # Common fields for all contracts
        col1, col2 = st.columns(2)
        with col1:
            party1_name = st.text_input("First Party Name", placeholder="Company XYZ, Inc.")
            party1_address = st.text_input("First Party Address", placeholder="123 Business Ave, City, State, ZIP")
        
        with col2:
            party2_name = st.text_input("Second Party Name", placeholder="ABC Corporation")
            party2_address = st.text_input("Second Party Address", placeholder="456 Corporate Blvd, City, State, ZIP")
        
        effective_date = st.date_input("Effective Date")
        governing_law = st.selectbox("Governing Law (Jurisdiction)", 
                                  ["California", "New York", "Texas", "Delaware", "Florida", "Other US State", 
                                   "United Kingdom", "Canada", "Australia", "European Union"])
        
        # Contract-specific fields
        st.markdown("### Contract-Specific Details")
        
        if contract_type == "Non-Disclosure Agreement (NDA)":
            col1, col2 = st.columns(2)
            with col1:
                nda_type = st.radio("NDA Type", ["One-way (Unilateral)", "Two-way (Mutual)"])
                purpose = st.text_input("Purpose of Disclosure", placeholder="Evaluating potential business relationship")
            
            with col2:
                term_length = st.slider("Term Length (Years)", min_value=1, max_value=10, value=3)
                survival_period = st.slider("Survival Period (Years)", min_value=1, max_value=10, value=2,
                                          help="How long confidentiality obligations last after termination")
        
        elif contract_type == "Consulting Agreement":
            col1, col2 = st.columns(2)
            with col1:
                services = st.text_area("Services Description", placeholder="Provide technical consulting services related to...")
                start_date = st.date_input("Start Date", value=effective_date)
            
            with col2:
                payment_terms = st.selectbox("Payment Terms", ["Hourly Rate", "Fixed Fee", "Monthly Retainer"])
                payment_amount = st.number_input("Payment Amount ($)", min_value=0, value=150)
                term_length = st.slider("Term Length (Months)", min_value=1, max_value=24, value=6)
        
        elif contract_type == "Employment Agreement":
            col1, col2 = st.columns(2)
            with col1:
                position = st.text_input("Position/Title", placeholder="Software Engineer")
                employment_type = st.selectbox("Employment Type", ["Full-time", "Part-time", "Contract"])
                salary = st.number_input("Annual Salary ($)", min_value=0, value=85000, step=5000)
            
            with col2:
                start_date = st.date_input("Start Date", value=effective_date)
                at_will = st.checkbox("At-will Employment", value=True)
                probation = st.slider("Probation Period (Months)", min_value=0, max_value=12, value=3)
        
        # Add more complex options
        st.markdown("### Additional Options")
        col1, col2 = st.columns(2)
        with col1:
            complexity_level = st.select_slider(
                "Complexity Level",
                options=["Basic", "Standard", "Comprehensive", "Enterprise-grade"],
                value="Standard",
                help="Higher complexity includes more detailed provisions"
            )
            
            include_exhibits = st.checkbox("Include Exhibits/Attachments", value=False)
        
        with col2:
            risk_profile = st.select_slider(
                "Risk Profile",
                options=["Conservative", "Balanced", "Progressive"],
                value="Balanced",
                help="Conservative is more protective, Progressive is more business-friendly"
            )
            
            special_clauses = st.multiselect(
                "Special Clauses",
                ["Force Majeure", "Alternative Dispute Resolution", "Non-compete", "Non-solicitation", 
                 "Third-party Beneficiaries", "Assignment Rights", "Limitation of Liability"],
                default=[]
            )
        
        # Custom input
        custom_requests = st.text_area("Custom Requirements or Notes", 
                                     placeholder="Add any specific requirements or notes for this contract...",
                                     help="This information will be used to further customize your contract")
        
        # Submit button
        submit_button = st.form_submit_button("Generate Contract", type="primary")
    
    # Example button
    if st.button("View Example", disabled=submit_button):
        st.session_state.response_text = """
# NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement (this "**Agreement**") is made and entered into as of **June 1, 2023** (the "**Effective Date**"), by and between **Acme Corporation**, a Delaware corporation, with offices located at 123 Main Street, San Francisco, CA 94105 ("**Disclosing Party**"), and **XYZ Ventures LLC**, a California limited liability company, with offices located at 456 Market Street, San Francisco, CA 94105 ("**Recipient**").

## 1. PURPOSE
The parties wish to explore a potential business relationship in connection with a potential investment or strategic partnership (the "**Purpose**"). In connection with the Purpose, Disclosing Party may disclose Confidential Information to Recipient, and the parties wish to protect such Confidential Information in accordance with this Agreement.

## 2. DEFINITION OF CONFIDENTIAL INFORMATION
For purposes of this Agreement, "**Confidential Information**" means any information disclosed by Disclosing Party to Recipient, either directly or indirectly, in writing, orally or by inspection of tangible objects, which is designated as "Confidential" or "Proprietary" or which reasonably should be understood to be confidential given the nature of the information and the circumstances of disclosure. Confidential Information may include, without limitation, technical data, trade secrets, research, product plans, products, services, customer lists, markets, software, developments, inventions, processes, formulas, technology, designs, drawings, engineering, hardware configuration information, marketing or finance documents, and other business information.

## 3. EXCEPTIONS TO CONFIDENTIAL INFORMATION
The obligations and restrictions set forth herein shall not apply to any information that: (a) was in Recipient's possession prior to receipt from Disclosing Party; (b) is or becomes a matter of public knowledge through no fault of Recipient; (c) is rightfully received by Recipient from a third party without a duty of confidentiality; (d) is independently developed by Recipient without use of Disclosing Party's Confidential Information; (e) is disclosed by Recipient with Disclosing Party's prior written approval; or (f) is required to be disclosed by operation of law, court order or other governmental demand.

## 4. OBLIGATIONS OF RECIPIENT
Recipient shall: (a) use the Confidential Information only for the Purpose; (b) hold the Confidential Information in strict confidence and take reasonable precautions to protect such Confidential Information (including, without limitation, all precautions the Recipient employs with respect to its own confidential materials); (c) not divulge any such Confidential Information to any third party; and (d) not copy or reverse engineer any materials disclosed under this Agreement or remove any proprietary markings from any Confidential Information.

## 5. TERM AND TERMINATION
This Agreement shall commence on the Effective Date and continue for a period of three (3) years. The Recipient's obligations with respect to Confidential Information shall survive for a period of two (2) years following termination or expiration of this Agreement.

## 6. REMEDIES
Recipient acknowledges that unauthorized disclosure or use of Confidential Information could cause irreparable harm and significant injury to Disclosing Party that may be difficult to ascertain. Accordingly, Recipient agrees that Disclosing Party shall have the right to seek and obtain immediate injunctive relief to enforce Recipient's obligations under this Agreement, in addition to any other rights and remedies it may have.

## 7. GOVERNING LAW
This Agreement shall be governed by and construed in accordance with the laws of the State of California without reference to its conflicts of law provisions. The parties hereby consent to the exclusive jurisdiction and venue in the state and federal courts in San Francisco County, California.

## 8. MISCELLANEOUS
This Agreement constitutes the entire understanding between the parties concerning the subject matter hereof. This Agreement may not be amended or modified except by a written instrument signed by both parties. If any provision of this Agreement is found to be unenforceable, the remainder shall be enforced as fully as possible and the unenforceable provision shall be deemed modified to the limited extent required to permit its enforcement in a manner most closely representing the intention of the parties as expressed herein.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the Effective Date.

DISCLOSING PARTY:
Acme Corporation

By: ________________________
Name: John Smith
Title: Chief Executive Officer

RECIPIENT:
XYZ Ventures LLC

By: ________________________
Name: Jane Doe
Title: Managing Partner
        """
        st.session_state.processing_time = 2.1
    
    # Generate contract if form submitted
    if submit_button:
        # Display loading state
        with st.spinner("Generating your customized contract..."):
            start_time = time.time()
            
            # Prepare request data
            contract_data = {
                "contract_type": contract_type,
                "party1_name": party1_name,
                "party1_address": party1_address,
                "party2_name": party2_name,
                "party2_address": party2_address,
                "effective_date": effective_date.strftime("%Y-%m-%d"),
                "governing_law": governing_law,
                "complexity_level": complexity_level,
                "risk_profile": risk_profile,
                "special_clauses": ",".join(special_clauses) if special_clauses else "",
                "custom_requests": custom_requests
            }
            
            # Add contract-specific data
            if contract_type == "Non-Disclosure Agreement (NDA)":
                contract_data.update({
                    "nda_type": nda_type,
                    "purpose": purpose,
                    "term_length": term_length,
                    "survival_period": survival_period
                })
            elif contract_type == "Consulting Agreement":
                contract_data.update({
                    "services": services,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "payment_terms": payment_terms,
                    "payment_amount": payment_amount,
                    "term_length": term_length
                })
            elif contract_type == "Employment Agreement":
                contract_data.update({
                    "position": position,
                    "employment_type": employment_type,
                    "salary": salary,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "at_will": at_will,
                    "probation": probation
                })
            
            # Send request to API
            st.info(f"Sending contract generation request to {API_URL}/api/document/generate-contract")
            try:
                response = httpx.post(f"{API_URL}/api/document/generate-contract", json=contract_data, timeout=60.0)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Calculate processing time
                    end_time = time.time()
                    st.session_state.processing_time = end_time - start_time
                    
                    if result.get("success", False):
                        st.session_state.response_text = result.get("contract", {}).get("content", "")
                        
                        # Display success and download option
                        st.success("Contract generated successfully!")
                        
                        # Create download button
                        st.download_button(
                            label="Download Contract as Markdown",
                            data=st.session_state.response_text,
                            file_name=f"{contract_type.replace(' ', '_').lower()}_{effective_date.strftime('%Y%m%d')}.md",
                            mime="text/markdown"
                        )
                        
                        # Display contract preview
                        st.markdown("### Contract Preview")
                        st.markdown('<div class="response-area">', unsafe_allow_html=True)
                        st.markdown(st.session_state.response_text)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error(f"Contract generation failed: {result.get('error', 'Unknown error')}")
                else:
                    # Fallback to direct Gemini generation if API fails
                    st.warning("API endpoint not available. Using direct Gemini generation as fallback.")
                    
                    # Try direct Gemini contract generation
                    prompt = f"""
You are a legal contract drafting expert. Generate a professional and legally sound {contract_type} with the following details:

Party 1: {party1_name}, located at {party1_address}
Party 2: {party2_name}, located at {party2_address}
Effective Date: {effective_date.strftime("%B %d, %Y")}
Governing Law: {governing_law}
Complexity Level: {complexity_level}
Risk Profile: {risk_profile}
Special Clauses to Include: {', '.join(special_clauses) if special_clauses else 'None specified'}

{"NDA Type: " + nda_type if contract_type == "Non-Disclosure Agreement (NDA)" else ""}
{"Purpose: " + purpose if contract_type == "Non-Disclosure Agreement (NDA)" and purpose else ""}
{"Services: " + services if contract_type == "Consulting Agreement" and services else ""}
{"Position: " + position if contract_type == "Employment Agreement" and position else ""}

Additional Notes: {custom_requests if custom_requests else 'None provided'}

Format the contract in Markdown format with proper sections, clear numbering, and standard legal provisions appropriate for this contract type. The contract should be detailed enough to be legally enforceable while being easy to understand.
"""
                    try:
                        if GEMINI_API_KEY:
                            genai.configure(api_key=GEMINI_API_KEY)
                            model = genai.GenerativeModel('gemini-pro')
                            response = model.generate_content(prompt)
                            
                            # Calculate processing time
                            end_time = time.time()
                            st.session_state.processing_time = end_time - start_time
                            
                            st.session_state.response_text = response.text
                            
                            # Display success and download option
                            st.success("Contract generated successfully (via Gemini)!")
                            
                            # Create download button
                            st.download_button(
                                label="Download Contract as Markdown",
                                data=st.session_state.response_text,
                                file_name=f"{contract_type.replace(' ', '_').lower()}_{effective_date.strftime('%Y%m%d')}.md",
                                mime="text/markdown"
                            )
                            
                            # Display contract preview
                            st.markdown("### Contract Preview")
                            st.markdown('<div class="response-area">', unsafe_allow_html=True)
                            st.markdown(st.session_state.response_text)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.error("Unable to access direct model. Please try again later.")
                    except Exception as e:
                        st.error(f"Error with fallback generation: {str(e)}")
            except Exception as e:
                st.error(f"Error during contract generation: {str(e)}")
    
    # Display previous contract if available
    elif st.session_state.response_text and not submit_button:
        # Display download button for example
        st.download_button(
            label="Download Example Contract as Markdown",
            data=st.session_state.response_text,
            file_name="example_nda.md",
            mime="text/markdown"
        )
        
        # Display contract preview
        st.markdown("### Contract Preview")
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)

# Legal Research Assistant
elif app_mode == "Legal Research Assistant":
    st.markdown("## Legal Research Assistant")
    st.markdown('<div class="info-box">Conduct comprehensive legal research with AI assistance. Search through case law, statutes, regulations, and legal commentary to find relevant information for your legal questions.</div>', unsafe_allow_html=True)
    
    # Research sidebar
    with st.sidebar:
        st.subheader("Research Sources")
        sources = st.multiselect(
            "Select sources to include",
            ["Case Law", "Federal Statutes", "State Statutes", "Legal Commentary", "Law Reviews", "International Law"],
            default=["Case Law", "Federal Statutes"]
        )
        
        jurisdiction = st.selectbox(
            "Jurisdiction",
            ["All US Jurisdictions", "Federal", "California", "New York", "Texas", "Delaware", "Other US State", "International"]
        )
        
        time_period = st.slider(
            "Time Period (Years)",
            min_value=1,
            max_value=50,
            value=(1, 20),
            help="Limit results to cases within this time period"
        )
        
        st.write("#### Advanced Filters")
        relevance_threshold = st.slider(
            "Relevance Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Higher values return more relevant but fewer results"
        )
        
        include_dissenting = st.checkbox("Include Dissenting Opinions", value=False)
        include_overruled = st.checkbox("Include Overruled Cases", value=False)
    
    # Main research interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        research_query = st.text_area(
            "Enter your legal research question",
            height=100,
            placeholder="e.g., What is the standard for proving copyright infringement in digital media cases?"
        )
        
        context = st.text_area(
            "Additional context (optional)",
            height=100,
            placeholder="Provide any specific details or context for your research..."
        )
    
    with col2:
        st.write("##### Research Format")
        result_format = st.radio(
            "Choose output format",
            ["Comprehensive", "Summary", "Case Citations Only"]
        )
        
        max_results = st.slider(
            "Max Results",
            min_value=5,
            max_value=50,
            value=20
        )
    
    # Create expandable section for example query
    with st.expander("See example research question"):
        st.write("""
        **Question**: What is the current legal standard for determining fair use in copyright cases involving AI-generated content?
        
        **Context**: I'm researching how courts have applied fair use doctrine to AI systems that are trained on copyrighted materials, particularly focusing on transformative use and market impact factors.
        """)
    
    # Research buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        search_button = st.button("Conduct Research", type="primary", disabled=not research_query)
    with col2:
        example_button = st.button("Load Example", disabled=research_query != "")
        if example_button:
            st.session_state.response_text = """
# Legal Research: Fair Use in AI-Generated Content

## EXECUTIVE SUMMARY
The legal standard for determining fair use in copyright cases involving AI-generated content is evolving, but courts generally apply the traditional four-factor test established in 17 U.S.C. § 107, with special emphasis on transformative use and market impact when AI systems are involved.

## RELEVANT LEGAL FRAMEWORK

### Statutory Framework
- **17 U.S.C. § 107 (Fair Use)** establishes four factors:
  1. Purpose and character of the use
  2. Nature of the copyrighted work
  3. Amount and substantiality of the portion used
  4. Effect on the potential market

### Key Cases

#### AI Training and Fair Use
- **Authors Guild v. Google, Inc.**, 804 F.3d 202 (2d Cir. 2015)
  - **Holding**: Google's digitization of books for search functionality was transformative fair use
  - **Relevance**: Established that using copyrighted works to "train" a system for a new purpose can be transformative

- **Authors Guild v. HathiTrust**, 755 F.3d 87 (2d Cir. 2014)
  - **Holding**: Creation of a searchable database was transformative and fair use
  - **Relevance**: Processing copyrighted works for computational analysis can qualify as fair use

#### Recent Developments
- **Andy Warhol Foundation v. Goldsmith**, 598 U.S. ___ (2023)
  - **Holding**: Commercial use of a photograph as a basis for artwork requires licensing
  - **Relevance**: Narrowed the scope of "transformative use," potentially affecting AI systems that create derivative works

- **Thaler v. Perlmutter**, No. 22-cv-01564 (D.D.C. 2023)
  - **Holding**: AI-generated works are not eligible for copyright protection without human authorship
  - **Relevance**: Distinguishes between AI as a tool used by humans (potentially eligible) and autonomous AI creation (not eligible)

## ANALYSIS OF FACTORS IN AI CONTEXT

### 1. Purpose and Character of Use
Courts are likely to consider:
- Whether the AI use is transformative (creates something with new meaning or purpose)
- Commercial nature of the AI system
- Whether the AI is being used for research, education, or commercial purposes

### 2. Nature of Copyrighted Work
- More protection is given to creative works than factual compilations
- Published works receive less protection than unpublished works

### 3. Amount and Substantiality Used
- AI systems often require large datasets for training, which may weigh against fair use
- However, courts have recognized that comprehensive copying may be necessary for certain transformative uses (see Google Books)

### 4. Market Impact
- Key consideration: Does the AI-generated output serve as a market substitute for the original?
- Courts examine whether the use threatens the potential market for or value of the copyrighted work

## EMERGING TRENDS
1. **Technical Differentiation**: Courts increasingly consider technical aspects of how AI systems process and transform copyrighted works
2. **"Text and Data Mining" Exception**: Growing recognition of a need for specific exceptions for computational analysis
3. **Licensing Solutions**: Development of licensing frameworks for AI training data

## CONCLUSION
While no court has established a definitive standard specifically for AI-generated content, the trend indicates that:
1. Training AI on copyrighted works may qualify as fair use if sufficiently transformative
2. Generating outputs that compete with or replace original works likely falls outside fair use
3. Commercial uses face greater scrutiny
4. The amount of copyrighted material necessary for training is balanced against the purpose

Given the nascent state of law in this area, companies developing AI systems should consider:
- Implementing attribution mechanisms
- Developing licensing frameworks
- Ensuring generated outputs are sufficiently transformative

---

**Disclaimer**: This research was generated by a legal AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel.
            """
            st.session_state.processing_time = 4.2
            st.experimental_rerun()
    
    if search_button and research_query:
        # Display loading state
        with st.spinner("Conducting legal research..."):
            start_time = time.time()
            
            # Prepare request data
            research_data = {
                "query": research_query,
                "context": context if context else "",
                "sources": ",".join(sources),
                "jurisdiction": jurisdiction,
                "time_period_start": str(time_period[0]),
                "time_period_end": str(time_period[1]),
                "relevance_threshold": str(relevance_threshold),
                "include_dissenting": "true" if include_dissenting else "false",
                "include_overruled": "true" if include_overruled else "false",
                "result_format": result_format,
                "max_results": str(max_results)
            }
            
            # Send request to API
            st.info(f"Sending research request to {API_URL}/api/research")
            try:
                response = httpx.post(f"{API_URL}/api/research", json=research_data, timeout=60.0)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Calculate processing time
                    end_time = time.time()
                    st.session_state.processing_time = end_time - start_time
                    
                    if result.get("success", False):
                        st.session_state.response_text = result.get("research", {}).get("content", "")
                        
                        # Display success
                        st.success("Research completed successfully")
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Sources Searched", value=result.get("research", {}).get("sources_searched", "Multiple"))
                        with col2:
                            st.metric(label="Relevance Score", value=f"{result.get('research', {}).get('relevance_score', 0.85):.2f}")
                        with col3:
                            st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                        
                        # Display research results
                        st.markdown('<div class="response-area">', unsafe_allow_html=True)
                        st.markdown(st.session_state.response_text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Citation download
                        if result.get("research", {}).get("citations"):
                            citations = result.get("research", {}).get("citations")
                            st.download_button(
                                label="Download Citations",
                                data=citations,
                                file_name="legal_citations.txt",
                                mime="text/plain"
                            )
                    else:
                        st.error(f"Research failed: {result.get('error', 'Unknown error')}")
                else:
                    # Fallback to direct Gemini research if API fails
                    st.warning("API endpoint not available. Using direct Gemini research as fallback.")
                    
                    # Try direct Gemini legal research
                    prompt = f"""
You are an AI legal research assistant with expertise in legal analysis and case law research. Conduct comprehensive legal research on the following question:

RESEARCH QUESTION: {research_query}

ADDITIONAL CONTEXT: {context}

REQUESTED SOURCES: {', '.join(sources)}
JURISDICTION: {jurisdiction}
TIME PERIOD: Past {time_period[1]} years

Please provide a well-structured legal research report that includes:
1. An executive summary of the findings
2. The relevant legal framework (statutes, regulations)
3. Analysis of key cases and their holdings
4. Synthesis of the current legal standard
5. Emerging trends or developments in this area
6. A conclusion with practical implications

Format your response in Markdown with clear headings and sections. Cite specific cases using proper legal citation format.
"""

                    try:
                        if GEMINI_API_KEY:
                            genai.configure(api_key=GEMINI_API_KEY)
                            model = genai.GenerativeModel('gemini-pro')
                            response = model.generate_content(prompt)
                            
                            # Calculate processing time
                            end_time = time.time()
                            st.session_state.processing_time = end_time - start_time
                            
                            st.session_state.response_text = response.text
                            
                            # Display metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(label="Research Method", value="AI Synthesis")
                            with col2:
                                st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                            
                            # Display research results
                            st.markdown('<div class="response-area">', unsafe_allow_html=True)
                            st.markdown(st.session_state.response_text)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.error("Unable to access direct model. Please try again later.")
                    except Exception as e:
                        st.error(f"Error with fallback research: {str(e)}")
            except Exception as e:
                st.error(f"Error conducting legal research: {str(e)}")
    
    # Display previous research if available
    elif st.session_state.response_text and not search_button:
        # Display metrics from example
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Sources Searched", value="Federal Cases, Statutes")
        with col2:
            st.metric(label="Relevance Score", value="0.92")
        with col3:
            st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
        
        # Display analysis
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add citation download example
        st.download_button(
            label="Download Citations",
            data="""Authors Guild v. Google, Inc., 804 F.3d 202 (2d Cir. 2015)
Authors Guild v. HathiTrust, 755 F.3d 87 (2d Cir. 2014)
Andy Warhol Foundation v. Goldsmith, 598 U.S. ___ (2023)
Thaler v. Perlmutter, No. 22-cv-01564 (D.D.C. 2023)
Campbell v. Acuff-Rose Music, Inc., 510 U.S. 569 (1994)
Google LLC v. Oracle America, Inc., 593 U.S. ___ (2021)""",
            file_name="legal_citations.txt",
            mime="text/plain"
        )

# Legal Precedent Analysis
elif app_mode == "Legal Precedent Analysis":
    st.markdown("## Legal Precedent Analysis")
    st.markdown('<div class="info-box">Discover similar legal cases and analyze precedents relevant to your case. Upload case details or brief to find matching precedents, understand their implications, and build stronger legal arguments.</div>', unsafe_allow_html=True)
    
    # Case input methods
    input_method = st.radio(
        "Input Method",
        ["Upload Case Brief/Filing", "Enter Case Details Manually", "Use Case Citation"]
    )
    
    if input_method == "Upload Case Brief/Filing":
        uploaded_file = st.file_uploader("Upload case brief or filing", type=["pdf", "docx", "txt"])
        
        if uploaded_file:
            st.success(f"Uploaded: {uploaded_file.name}")
    
    elif input_method == "Enter Case Details Manually":
        col1, col2 = st.columns(2)
        with col1:
            case_name = st.text_input("Case Name (optional)", placeholder="Smith v. Jones")
            jurisdiction = st.selectbox(
                "Jurisdiction",
                ["Federal", "California", "New York", "Texas", "Delaware", "Florida", "Other US State", "International"]
            )
        
        with col2:
            case_type = st.selectbox(
                "Case Type",
                ["Civil", "Criminal", "Administrative", "Constitutional", "International", "Other"]
            )
            area_of_law = st.selectbox(
                "Area of Law",
                ["Contract", "Tort", "Property", "Criminal", "Constitutional", "Administrative", "International", 
                 "Intellectual Property", "Corporate", "Tax", "Family", "Labor/Employment", "Environmental", "Other"]
            )
        
        case_facts = st.text_area(
            "Key Facts and Legal Issues",
            height=150,
            placeholder="Describe the essential facts and legal questions in your case..."
        )
    
    elif input_method == "Use Case Citation":
        case_citation = st.text_input(
            "Enter Case Citation",
            placeholder="e.g., 410 U.S. 113 (1973) or 304 F.3d 964 (9th Cir. 2002)"
        )
    
    # Analysis options
    st.markdown("### Analysis Options")
    
    col1, col2 = st.columns(2)
    with col1:
        search_depth = st.slider(
            "Search Depth",
            min_value=1,
            max_value=5,
            value=3,
            help="Higher values provide more thorough but slower analysis"
        )
        
        relevance_threshold = st.slider(
            "Minimum Relevance Score",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.05
        )
    
    with col2:
        max_cases = st.slider(
            "Maximum Number of Cases",
            min_value=3,
            max_value=25,
            value=10
        )
        
        recency_weight = st.slider(
            "Recency Importance",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Higher values prioritize recent cases"
        )
    
    # Analysis focus
    st.markdown("### Analysis Focus")
    
    focus_areas = st.multiselect(
        "Select areas to focus on",
        ["Factual Similarities", "Legal Reasoning", "Court's Analysis", "Statutory Interpretation", 
         "Constitutional Analysis", "Procedural History", "Dissenting Opinions"],
        default=["Factual Similarities", "Legal Reasoning"]
    )
    
    # Analysis buttons
    col1, col2 = st.columns([3, 1])
    
    case_data_ready = (
        (input_method == "Upload Case Brief/Filing" and uploaded_file is not None) or
        (input_method == "Enter Case Details Manually" and case_facts.strip() != "") or
        (input_method == "Use Case Citation" and case_citation.strip() != "")
    )
    
    with col1:
        analyze_button = st.button("Find Similar Cases", type="primary", disabled=not case_data_ready)
    
    with col2:
        example_button = st.button("Load Example", disabled=case_data_ready)
        if example_button:
            st.session_state.response_text = """
# Precedent Analysis Report

## SIMILAR CASES OVERVIEW

We identified 7 cases with significant similarity to your case facts, with relevance scores ranging from 83% to 96%.

## TOP MATCHING PRECEDENTS

### 1. **Microsoft Corp. v. i4i Ltd. Partnership**
**566 U.S. 91 (2011)** | **Relevance: 96%**

**Key Holdings:**
- When challenging patent validity in infringement litigation, the challenger must prove invalidity by clear and convincing evidence
- The standard of proof doesn't change when prior art wasn't considered by the Patent Office

**Factual Similarities:**
- Involves software patent infringement claims
- Defendant challenging validity of software-implementation patents
- Questions regarding standard of proof for patent invalidity

**Legal Reasoning Applied:**
The Supreme Court affirmed that §282 of the Patent Act requires invalidity defenses to be proven by clear and convincing evidence. The Court rejected Microsoft's argument that a preponderance standard should apply when the PTO didn't consider the prior art being asserted.

**Case Distinction:**
Your case involves algorithm patents rather than markup language patents, which may create different technical considerations, though the legal standards remain applicable.

### 2. **Alice Corp. v. CLS Bank International**
**573 U.S. 208 (2014)** | **Relevance: 92%**

**Key Holdings:**
- Abstract ideas implemented using computers are not patent-eligible under §101
- To be patent-eligible, claims must add "something extra" beyond an abstract idea

**Factual Similarities:**
- Centers on software implementation patents
- Questions of patent eligibility for computer-implemented business methods
- Similar technological domain (financial technology)

**Legal Reasoning Applied:**
The Court established a two-step framework: (1) determine if claims are directed to a patent-ineligible concept; (2) if yes, examine if elements transform the nature of the claim into patent-eligible application.

**Potential Impact:**
Highly relevant to your claims regarding algorithm patentability. Your case must distinguish how the technology improves computer functionality rather than merely implementing abstract ideas on computers.

### 3. **Bilski v. Kappos**
**561 U.S. 593 (2010)** | **Relevance: 88%**

**Key Holdings:**
- The "machine-or-transformation" test is not the sole test for patent eligibility
- Business methods are not categorically excluded from patentability

**Factual Similarities:**
- Involves process/method claims implemented in software
- Questions regarding patentable subject matter
- Similar concerns about abstract ideas

**Case Distinction:**
Your case involves more specific technological implementations than the business method in Bilski, potentially strengthening patentability arguments.

## LEGAL TREND ANALYSIS

### Current Trend in Software Patent Cases
Courts are increasingly requiring software patents to demonstrate:
1. Specific improvements to computer functionality
2. Technical solutions to technical problems
3. Claims that go beyond mere automation of known processes

### Recent Developments
The Federal Circuit has refined Alice analysis in cases like:
- **Enfish, LLC v. Microsoft Corp.** (2016): Recognizing patents that improve computer functionality
- **McRO, Inc. v. Bandai Namco Games America** (2016): Upholding patents with specific technical rules
- **Finjan, Inc. v. Blue Coat Systems** (2018): Recognizing behavior-based virus scanning as non-abstract

## STRATEGIC RECOMMENDATIONS

Based on precedent analysis:

1. **Focus on Technical Improvements**
   Emphasize how your client's patents improve computer functionality itself, not merely using computers to implement abstract ideas.

2. **Differentiate from Alice**
   Articulate how the claimed algorithms solve a technical problem in a specific, non-conventional way.

3. **Leverage Enfish Precedent**
   Align arguments with Enfish by demonstrating that your client's innovation is directed to a specific improvement to computer capabilities.

4. **Address Clear and Convincing Standard**
   Prepare to meet the heightened evidentiary standard for any invalidity claims from Microsoft Corp. v. i4i.

## CRITICAL CASES TO CITE

1. Microsoft Corp. v. i4i Ltd. Partnership, 566 U.S. 91 (2011)
2. Alice Corp. v. CLS Bank International, 573 U.S. 208 (2014) 
3. Enfish, LLC v. Microsoft Corp., 822 F.3d 1327 (Fed. Cir. 2016)
4. McRO, Inc. v. Bandai Namco Games America Inc., 837 F.3d 1299 (Fed. Cir. 2016)
5. Bilski v. Kappos, 561 U.S. 593 (2010)

---

**Disclaimer**: This precedent analysis was generated by an AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel.
            """
            st.session_state.processing_time = 4.5
            st.experimental_rerun()
    
    if analyze_button:
        # Display loading state
        with st.spinner("Analyzing legal precedents..."):
            start_time = time.time()
            
            # Prepare request data
            case_data = {
                "search_depth": search_depth,
                "relevance_threshold": relevance_threshold,
                "max_cases": max_cases,
                "recency_weight": recency_weight,
                "focus_areas": ",".join(focus_areas)
            }
            
            # Add input method specific data
            if input_method == "Upload Case Brief/Filing" and uploaded_file is not None:
                # Save to temp file
                temp_path = create_temp_file(uploaded_file)
                
                if temp_path:
                    try:
                        # Prepare form data
                        files = {"file": (uploaded_file.name, open(temp_path, "rb"), uploaded_file.type)}
                        
                        # Send request to API
                        st.info(f"Sending precedent analysis request to {API_URL}/api/precedent/analyze")
                        try:
                            response = httpx.post(
                                f"{API_URL}/api/precedent/analyze", 
                                files=files, 
                                data=case_data,
                                timeout=60.0
                            )
                            
                            # Process response
                            process_precedent_response(response, start_time)
                        except Exception as e:
                            st.error(f"Error during precedent analysis: {str(e)}")
                            
                            # Try fallback
                            try_fallback_precedent_analysis(
                                extract_text_from_doc(temp_path, uploaded_file.type) or "Case brief text extraction failed",
                                "",
                                focus_areas,
                                start_time
                            )
                    finally:
                        # Clean up temp file
                        cleanup_temp_file(temp_path)
            
            elif input_method == "Enter Case Details Manually" and case_facts.strip() != "":
                # Prepare case details
                case_details = {
                    "case_name": case_name if 'case_name' in locals() else "",
                    "jurisdiction": jurisdiction if 'jurisdiction' in locals() else "",
                    "case_type": case_type if 'case_type' in locals() else "",
                    "area_of_law": area_of_law if 'area_of_law' in locals() else "",
                    "case_facts": case_facts
                }
                case_data.update(case_details)
                
                # Send request to API
                st.info(f"Sending precedent analysis request to {API_URL}/api/precedent/analyze-text")
                try:
                    response = httpx.post(
                        f"{API_URL}/api/precedent/analyze-text", 
                        json=case_data,
                        timeout=60.0
                    )
                    
                    # Process response
                    process_precedent_response(response, start_time)
                except Exception as e:
                    st.error(f"Error during precedent analysis: {str(e)}")
                    
                    # Try fallback
                    try_fallback_precedent_analysis(
                        case_facts,
                        f"Case Type: {case_type}, Area of Law: {area_of_law}, Jurisdiction: {jurisdiction}",
                        focus_areas,
                        start_time
                    )
            
            elif input_method == "Use Case Citation" and case_citation.strip() != "":
                # Prepare citation data
                citation_data = {"citation": case_citation}
                case_data.update(citation_data)
                
                # Send request to API
                st.info(f"Sending precedent analysis request to {API_URL}/api/precedent/analyze-citation")
                try:
                    response = httpx.post(
                        f"{API_URL}/api/precedent/analyze-citation", 
                        json=case_data,
                        timeout=60.0
                    )
                    
                    # Process response
                    process_precedent_response(response, start_time)
                except Exception as e:
                    st.error(f"Error during precedent analysis: {str(e)}")
                    
                    # Try fallback
                    try_fallback_precedent_analysis(
                        f"Citation: {case_citation}",
                        f"Focus on: {', '.join(focus_areas)}",
                        focus_areas,
                        start_time
                    )
    
    # Display previous analysis if available
    elif st.session_state.response_text and not analyze_button:
        # Display metrics from example
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Similar Cases Found", value="7")
        with col2:
            st.metric(label="Top Match Relevance", value="96%")
        with col3:
            st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
        
        # Display analysis
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add case export option
        st.download_button(
            label="Export Case Analysis as PDF",
            data="This would be the PDF export of the precedent analysis",
            file_name="precedent_analysis_report.pdf",
            mime="application/pdf",
            disabled=True
        )
        
        # Display similarity visualization
        st.markdown("### Case Similarity Visualization")
        st.info("Interactive visualization would appear here in the full version")

# Helper functions for precedent analysis
def process_precedent_response(response, start_time):
    """Process the response from the precedent analysis API"""
    if response.status_code == 200:
        result = response.json()
        
        # Calculate processing time
        end_time = time.time()
        st.session_state.processing_time = end_time - start_time
        
        if result.get("success", False):
            st.session_state.response_text = result.get("analysis", {}).get("content", "")
            
            # Display success
            st.success("Precedent analysis completed successfully")
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Similar Cases Found", value=result.get("analysis", {}).get("case_count", "N/A"))
            with col2:
                st.metric(label="Top Match Relevance", value=f"{result.get('analysis', {}).get('top_relevance', 0) * 100:.0f}%")
            with col3:
                st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
            
            # Display research results
            st.markdown('<div class="response-area">', unsafe_allow_html=True)
            st.markdown(st.session_state.response_text)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error(f"Analysis failed: {result.get('error', 'Unknown error')}")
    else:
        st.error(f"Request failed with status code {response.status_code}")
        
        # Calculate processing time
        end_time = time.time()
        st.session_state.processing_time = end_time - start_time
        
        # Try fallback
        st.warning("Using Gemini fallback for precedent analysis")

def try_fallback_precedent_analysis(case_text, additional_context, focus_areas, start_time):
    """Try to use Gemini as a fallback for precedent analysis"""
    if not GEMINI_API_KEY:
        st.error("No Gemini API key available for fallback analysis")
        return
    
    prompt = f"""
You are an AI legal assistant specializing in precedent analysis. Analyze the following case details and identify similar legal precedents, their relevance, and how they might impact this case:

CASE DETAILS:
{case_text}

ADDITIONAL CONTEXT:
{additional_context}

FOCUS AREAS:
{', '.join(focus_areas)}

Provide a well-structured precedent analysis report that includes:
1. A list of the most relevant similar cases with their citations and relevance scores
2. For each key precedent, include:
   - Key holdings
   - Factual similarities to the current case
   - Legal reasoning applied
   - How the precedent might impact the current case
3. An analysis of current legal trends in this area
4. Strategic recommendations based on the precedent analysis
5. A list of critical cases to cite

Format your response in Markdown using clear headings and subheadings. Ensure proper legal citation format.
"""

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Calculate processing time
        end_time = time.time()
        st.session_state.processing_time = end_time - start_time
        
        st.session_state.response_text = response.text
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Analysis Method", value="AI Synthesis")
        with col2:
            st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
        
        # Display analysis
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error with fallback analysis: {str(e)}")

# Footer
st.markdown("""
<div class="disclaimer">
    <p><strong>Disclaimer:</strong> Legal AI is a hackathon project and provides informational assistance only. 
    It does not provide legal advice, and its responses should not be considered a substitute for consultation with a qualified legal professional.</p>
</div>
""", unsafe_allow_html=True)

# Gemini fallback function
def query_gemini_directly(query, context=None):
    """
    Direct fallback to Gemini when API is down
    """
    try:
        if not GEMINI_API_KEY:
            return None, "No Gemini API key found in environment variables"
            
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        You are a legal assistant specialized in document analysis and legal queries.
        Please provide a clear and concise response to the following question:
        
        {query}
        """
        
        if context:
            prompt += f"\n\nAdditional context:\n{context}"
            
        response = model.generate_content(prompt)
        return response.text + "\n\n---\n\n**Disclaimer**: This response was generated by an AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel.", None
    except Exception as e:
        return None, f"Error using Gemini API directly: {str(e)}"

def process_precedent_response(result, start_time):
    """Process and display the precedent analysis response"""
    # Calculate processing time
    processing_time = time.time() - start_time
    
    # Get the analysis data
    analysis = result.get("analysis", {})
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Similar Cases", str(len(analysis.get("matching_precedents", []))))
    with col2:
        top_match = max([p.get("relevance_score", 0) for p in analysis.get("matching_precedents", [])], default=0)
        st.metric("Top Match Relevance", f"{top_match*100:.0f}%")
    with col3:
        avg_relevance = sum([p.get("relevance_score", 0) for p in analysis.get("matching_precedents", [])]) / max(1, len(analysis.get("matching_precedents", [])))
        st.metric("Avg. Relevance", f"{avg_relevance*100:.0f}%")
    with col4:
        st.metric("Processing Time", f"{processing_time:.2f}s")
    
    # Display matching precedents
    st.subheader("Matching Precedents")
    
    matching_precedents = analysis.get("matching_precedents", [])
    if matching_precedents:
        for precedent in matching_precedents:
            case_name = precedent.get("case_name", "Unnamed Case")
            citation = precedent.get("citation", "")
            relevance = precedent.get("relevance_score", 0)
            year = precedent.get("year", "")
            
            with st.expander(f"{case_name} ({citation}) - {relevance*100:.0f}% Match", expanded=(relevance > 0.9)):
                st.markdown(f"**Court:** {precedent.get('court', 'Unknown')}")
                st.markdown(f"**Year:** {year}")
                
                st.markdown("**Key Holdings:**")
                for holding in precedent.get("key_holdings", []):
                    st.markdown(f"- {holding}")
                
                if precedent.get("relevant_passages"):
                    st.markdown("**Relevant Passages:**")
                    for passage in precedent.get("relevant_passages", []):
                        st.markdown(f"> {passage}")
                
                st.markdown("**Analysis:**")
                st.markdown(precedent.get("analysis", "No analysis provided"))
    else:
        st.info("No matching precedents found.")
    
    # Display legal trends
    legal_trends = analysis.get("legal_trends", {})
    with st.expander("Legal Trends Analysis", expanded=True):
        st.markdown(f"**Trend Direction:** {legal_trends.get('trend_direction', 'No trend information available')}")
        
        if legal_trends.get("historical_progression"):
            st.markdown("**Historical Progression:**")
            for stage in legal_trends.get("historical_progression", []):
                st.markdown(f"- {stage}")
        
        if legal_trends.get("current_position"):
            st.markdown(f"**Current Position:** {legal_trends.get('current_position')}")
    
    # Display strategic recommendations
    with st.expander("Strategic Recommendations", expanded=True):
        recommendations = analysis.get("strategic_recommendations", [])
        if recommendations:
            for rec in recommendations:
                st.markdown(f"- {rec}")
        else:
            st.info("No strategic recommendations available.")
    
    # Display critical citations
    with st.expander("Critical Cases to Cite"):
        citations = analysis.get("critical_citations", [])
        if citations:
            for citation in citations:
                st.markdown(f"- {citation}")
        else:
            st.info("No critical citations identified.")
    
    # Display summary
    if analysis.get("summary"):
        with st.expander("Summary", expanded=True):
            st.markdown(analysis.get("summary"))

def try_fallback_precedent_analysis(case_text, additional_context, focus_areas, start_time):
    """Attempt to analyze precedents directly with Gemini if API fails"""
    try:
        if not GEMINI_API_KEY:
            st.error("Unable to use fallback method: No Gemini API key available")
            return
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Build focus areas string
        focus_areas_str = ', '.join(focus_areas) if focus_areas else "general legal analysis"
        
        # Create precedent analysis prompt
        prompt = f"""
        You are a specialized legal precedent research AI with expertise in case law analysis.
        
        ANALYZE THE FOLLOWING CASE TEXT AND IDENTIFY RELEVANT PRECEDENTS:
        
        CASE TEXT:
        {case_text[:8000]}  # Limit text length
        
        ADDITIONAL CONTEXT:
        {additional_context or "No additional context provided."}
        
        FOCUS AREAS:
        {focus_areas_str}
        
        PROVIDE A COMPREHENSIVE ANALYSIS OF PRECEDENTS INCLUDING:
        1. A list of the most relevant precedent cases with proper citations and relevance scores
        2. Key holdings from each precedent case that relate to the current case
        3. Analysis of how each precedent applies to the current case
        4. Legal trends analysis based on the precedent timeline
        5. Strategic recommendations based on the precedents
        6. Critical cases to cite in legal arguments
        
        Format your response as JSON with the following structure:
        {{
            "matching_precedents": [
                {{
                    "case_name": "CASE NAME",
                    "citation": "FULL CITATION",
                    "court": "COURT",
                    "year": YEAR,
                    "relevance_score": SCORE (0.0-1.0),
                    "key_holdings": ["HOLDING 1", "HOLDING 2", ...],
                    "relevant_passages": ["PASSAGE 1", "PASSAGE 2", ...],
                    "analysis": "HOW THIS CASE APPLIES"
                }}
            ],
            "legal_trends": {{
                "trend_direction": "TREND DIRECTION",
                "historical_progression": ["STAGE 1", "STAGE 2", ...],
                "current_position": "CURRENT POSITION"
            }},
            "strategic_recommendations": ["RECOMMENDATION 1", "RECOMMENDATION 2", ...],
            "critical_citations": ["CITATION 1", "CITATION 2", ...],
            "summary": "OVERALL SUMMARY OF FINDINGS"
        }}
        """
        
        # Generate precedent analysis
        response = model.generate_content(prompt)
        response_text = response.text
        
        # Try to parse JSON response
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            analysis = json.loads(json_str)
            
            # Process and display the analysis
            process_precedent_response({"analysis": analysis}, start_time)
        else:
            st.error("Unable to parse fallback analysis response")
            st.code(response_text, language="json")
    
    except Exception as e:
        st.error(f"Error with fallback precedent analysis: {str(e)}")
        st.info("Showing example analysis instead")
        
        # Example analysis for demonstration
        example_analysis = {
            "matching_precedents": [
                {
                    "case_name": "Smith v. Johnson",
                    "citation": "234 F.3d 1234 (9th Cir. 2020)",
                    "court": "9th Circuit Court of Appeals",
                    "year": 2020,
                    "relevance_score": 0.92,
                    "key_holdings": [
                        "Court established a four-part test for determining validity of AI-generated legal documents",
                        "Recognized limited IP protection for AI-assisted legal work"
                    ],
                    "relevant_passages": [
                        "When determining the validity of AI-assisted legal work, courts must consider: (1) level of human oversight, (2) nature of the legal task, (3) disclosure to relevant parties, and (4) adherence to professional standards."
                    ],
                    "analysis": "This case directly addresses the standards for evaluating AI-generated legal content, which is central to the current case. The four-part test provides a framework for assessing the acceptability of using AI tools in legal practice."
                }
            ],
            "legal_trends": {
                "trend_direction": "Courts are increasingly accepting AI-assisted legal work with proper oversight",
                "historical_progression": [
                    "2018-2020: Initial skepticism and rejection of AI-generated work products",
                    "2020-2022: Acceptance with strict human review requirements",
                    "2022-Present: Nuanced framework allowing for varying levels of AI assistance based on task complexity"
                ],
                "current_position": "Cautious acceptance with emphasis on human oversight"
            },
            "strategic_recommendations": [
                "Emphasize the level of human review and oversight in the AI-assisted process",
                "Focus on how AI was used as a tool rather than the primary creator",
                "Highlight adherence to ethical standards and professional responsibilities"
            ],
            "critical_citations": [
                "Smith v. Johnson, 234 F.3d 1234 (9th Cir. 2020)",
                "Legal Ethics Opinion 2023-5, California Bar Association (2023)"
            ],
            "summary": "The analysis of relevant precedents indicates a cautious but increasingly accepting approach to AI-assisted legal work. Courts have established clear standards for acceptable use, with human oversight being the critical factor. Strategic arguments should focus on demonstrating compliance with these standards."
        }
        
        process_precedent_response({"analysis": example_analysis}, start_time)

# Define CSS styling
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #2E3A59;
        --secondary-color: #1C54B2;
        --accent-color: #2196F3;
        --background-color: #F8F9FA;
        --text-color: #333;
        --light-gray: #E9ECEF;
        --dark-gray: #6C757D;
    }

    /* General styling */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
        font-family: 'Roboto', sans-serif;
    }
    
    h1, h2, h3 {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    /* Header and main title */
    .main-title {
        color: var(--primary-color);
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* App mode sidebar */
    .sidebar .sidebar-content {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Info boxes */
    .info-box {
        background-color: var(--light-gray);
        border-left: 5px solid var(--accent-color);
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
    }
    
    /* Response area styling */
    .response-area {
        background-color: white;
        border: 1px solid var(--light-gray);
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        overflow-wrap: break-word;
    }
    
    /* Markdown styling */
    .response-area h1 {
        font-size: 1.8rem;
        margin-top: 0;
        color: var(--primary-color);
        border-bottom: 1px solid var(--light-gray);
        padding-bottom: 0.5rem;
    }
    
    .response-area h2 {
        font-size: 1.5rem;
        color: var(--secondary-color);
        margin-top: 1.5rem;
    }
    
    .response-area h3 {
        font-size: 1.2rem;
        color: var(--primary-color);
        margin-top: 1.2rem;
    }
    
    .response-area table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    
    .response-area th {
        background-color: var(--light-gray);
        padding: 0.5rem;
        text-align: left;
        border: 1px solid #DDD;
    }
    
    .response-area td {
        padding: 0.5rem;
        border: 1px solid #DDD;
    }
    
    .response-area tr:nth-child(even) {
        background-color: #F9F9F9;
    }
    
    /* Form styling */
    .stButton>button {
        background-color: var(--accent-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary-color);
    }
    
    /* File uploader */
    .uploadedFile {
        border: 1px dashed var(--light-gray);
        border-radius: 0.25rem;
        padding: 1rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--secondary-color);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: var(--dark-gray);
    }
    
    /* Footer */
    footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid var(--light-gray);
        font-size: 0.8rem;
        color: var(--dark-gray);
    }
    
    /* Risk levels */
    .risk-high {
        color: #DC3545;
        font-weight: bold;
    }
    
    .risk-medium {
        color: #FFC107;
        font-weight: bold;
    }
    
    .risk-low {
        color: #28A745;
        font-weight: bold;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: var(--accent-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown('<h1 class="main-title">Legal AI Assistant</h1>', unsafe_allow_html=True)

# Advanced Contract Comparison
if app_mode == "Contract Comparison":
    st.title("Advanced Contract Comparison")
    st.write("Upload two contracts to compare their differences with specialized legal analysis.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("First Contract")
        file1 = st.file_uploader("Upload original contract", type=["pdf", "docx", "txt"], key="contract1")
    
    with col2:
        st.subheader("Second Contract")
        file2 = st.file_uploader("Upload revised contract", type=["pdf", "docx", "txt"], key="contract2")
    
    document_type = st.selectbox(
        "Contract Type",
        options=["general", "service_agreement", "employment", "nda", "licensing", "real_estate", "partnership"]
    )
    
    if st.button("Compare Contracts") and file1 is not None and file2 is not None:
        with st.spinner("Analyzing contracts..."):
            start_time = time.time()
            
            try:
                # Create form data
                files = {
                    "file1": (file1.name, file1.getvalue(), file1.type),
                    "file2": (file2.name, file2.getvalue(), file2.type)
                }
                
                data = {"document_type": document_type}
                
                # Send request to API
                response = httpx.post(
                    f"{API_URL}/api/advanced/document/compare",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display result
                    st.success(f"Analysis completed in {time.time() - start_time:.2f} seconds")
                    
                    with st.expander("Summary of Changes", expanded=True):
                        st.markdown(result["comparison"].get("summary", "No summary available"))
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Additions")
                        st.markdown(result["comparison"].get("additions", "No significant additions detected"))
                    
                    with col2:
                        st.subheader("Deletions")
                        st.markdown(result["comparison"].get("deletions", "No significant deletions detected"))
                    
                    st.subheader("Modified Terms")
                    st.markdown(result["comparison"].get("modifications", "No significant modifications detected"))
                    
                    if "risk_shift" in result["comparison"]:
                        st.subheader("Risk Analysis")
                        risk_shift = result["comparison"]["risk_shift"]
                        
                        # Create risk visualization
                        if "risk_shift_direction" in risk_shift and "risk_shift_magnitude" in risk_shift:
                            direction = risk_shift["risk_shift_direction"]
                            magnitude = risk_shift["risk_shift_magnitude"]
                            
                            if direction == "toward_party_1":
                                st.warning(f"⚠️ Risk has shifted toward first party (Original) by {magnitude*100:.1f}%")
                            elif direction == "toward_party_2":
                                st.warning(f"⚠️ Risk has shifted toward second party (Revised) by {magnitude*100:.1f}%")
                            else:
                                st.info("Risk allocation remains relatively balanced between parties")
                            
                            # Display key risk clauses
                            if "key_risk_clauses" in risk_shift and risk_shift["key_risk_clauses"]:
                                st.subheader("Key Risk-Shifting Clauses")
                                for clause in risk_shift["key_risk_clauses"]:
                                    st.markdown(f"**{clause}**")
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"Error comparing documents: {str(e)}")

# Advanced Legal Risk Assessment
if app_mode == "Legal Risk Assessment":
    st.title("Legal Risk Assessment")
    st.write("Analyze the risks in your legal documents with an advanced AI assessment.")
    
    uploaded_file = st.file_uploader("Upload legal document", type=["pdf", "docx", "txt"])
    
    document_type = st.selectbox(
        "Document Type",
        options=["contract", "terms_of_service", "privacy_policy", "employment_agreement", "court_filing", "legislation"]
    )
    
    if st.button("Analyze Risks") and uploaded_file is not None:
        with st.spinner("Analyzing document risks..."):
            start_time = time.time()
            
            try:
                # Create form data
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"document_type": document_type}
                
                # Send request to API
                response = httpx.post(
                    f"{API_URL}/api/advanced/document/analyze",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    analysis = result["analysis"]
                    
                    # Display summary
                    st.success(f"Analysis completed in {time.time() - start_time:.2f} seconds")
                    
                    with st.expander("Document Summary", expanded=True):
                        st.markdown(analysis.get("summary", "No summary available"))
                    
                    # Display risks
                    st.subheader("Risk Assessment")
                    st.markdown(analysis.get("risks", "No risks identified"))
                    
                    # Display key clauses with risk levels if available
                    if "key_clauses" in analysis and analysis["key_clauses"]:
                        st.subheader("Key Clauses by Risk Level")
                        
                        high_risk = []
                        medium_risk = []
                        low_risk = []
                        
                        for clause in analysis["key_clauses"]:
                            if clause.get("risk_level", "").lower() == "high":
                                high_risk.append(clause)
                            elif clause.get("risk_level", "").lower() == "medium":
                                medium_risk.append(clause)
                            else:
                                low_risk.append(clause)
                        
                        if high_risk:
                            st.error("High Risk Clauses")
                            for clause in high_risk:
                                st.markdown(f"**{clause.get('name', 'Unnamed Clause')}**")
                                st.markdown(f"*{clause.get('text', '')}*")
                                st.markdown(f"Significance: {clause.get('significance', 'No information')}")
                                st.markdown("---")
                        
                        if medium_risk:
                            st.warning("Medium Risk Clauses")
                            for clause in medium_risk:
                                st.markdown(f"**{clause.get('name', 'Unnamed Clause')}**")
                                st.markdown(f"*{clause.get('text', '')}*")
                                st.markdown(f"Significance: {clause.get('significance', 'No information')}")
                                st.markdown("---")
                        
                        if low_risk:
                            st.info("Low Risk Clauses")
                            for clause in low_risk:
                                st.markdown(f"**{clause.get('name', 'Unnamed Clause')}**")
                                st.markdown(f"*{clause.get('text', '')}*")
                                st.markdown(f"Significance: {clause.get('significance', 'No information')}")
                                st.markdown("---")
                    
                    # Display obligations
                    with st.expander("Legal Obligations"):
                        st.markdown(analysis.get("obligations", "No obligations identified"))
                    
                    # Display parties
                    with st.expander("Parties Involved"):
                        st.markdown(analysis.get("parties", "No parties identified"))
                else:
                    st.error(f"Error: {response.status_code} - {response.text}")
            
            except Exception as e:
                st.error(f"Error analyzing document: {str(e)}")

# Intelligent Contract Generator
if app_mode == "Contract Generator":
    st.title("Intelligent Contract Generator")
    st.write("Generate legally sound contracts tailored to your specific needs.")
    
    contract_type = st.selectbox(
        "Contract Type",
        options=[
            "Non-Disclosure Agreement (NDA)",
            "Service Agreement",
            "Employment Contract",
            "Consulting Agreement",
            "Software License Agreement",
            "Partnership Agreement",
            "Real Estate Lease"
        ]
    )
    
    # Common fields for all contracts
    st.subheader("Parties")
    col1, col2 = st.columns(2)
    with col1:
        party1_name = st.text_input("First Party Name")
        party1_address = st.text_input("First Party Address")
    with col2:
        party2_name = st.text_input("Second Party Name")
        party2_address = st.text_input("Second Party Address")
    
    # Contract-specific fields
    if contract_type == "Non-Disclosure Agreement (NDA)":
        st.subheader("NDA Details")
        
        confidential_info = st.text_area("Description of Confidential Information")
        purpose = st.text_input("Purpose of Disclosure")
        duration = st.number_input("Duration (years)", min_value=1, max_value=10, value=2)
        jurisdiction = st.text_input("Governing Law (State/Country)")
        
        # Additional options
        st.subheader("Additional Provisions")
        include_noncompete = st.checkbox("Include Non-Compete Clause")
        include_nonsolicitation = st.checkbox("Include Non-Solicitation Clause")
        mutual = st.checkbox("Mutual NDA (both parties disclose)")
    
    elif contract_type == "Service Agreement":
        st.subheader("Service Details")
        
        services = st.text_area("Description of Services")
        compensation = st.text_input("Compensation")
        payment_terms = st.selectbox("Payment Terms", ["Net 30", "Net 15", "Upon Completion", "Monthly", "Custom"])
        
        if payment_terms == "Custom":
            custom_payment_terms = st.text_input("Specify Custom Payment Terms")
        
        term = st.number_input("Term (months)", min_value=1, max_value=60, value=12)
        
        # Additional options
        st.subheader("Additional Provisions")
        include_confidentiality = st.checkbox("Include Confidentiality Clause")
        include_ip_assignment = st.checkbox("Include IP Assignment")
        include_termination = st.checkbox("Include Early Termination Clause")
    
    # Add similar sections for other contract types
    
    # Common fields for all contracts
    st.subheader("Final Details")
    effective_date = st.date_input("Effective Date")
    special_provisions = st.text_area("Special Provisions or Notes")
    
    if st.button("Generate Contract"):
        with st.spinner("Generating your contract..."):
            try:
                # Prepare data based on contract type
                contract_data = {
                    "contract_type": contract_type,
                    "party1_name": party1_name,
                    "party1_address": party1_address,
                    "party2_name": party2_name,
                    "party2_address": party2_address,
                    "effective_date": str(effective_date),
                    "special_provisions": special_provisions
                }
                
                # Add contract-specific fields
                if contract_type == "Non-Disclosure Agreement (NDA)":
                    contract_data.update({
                        "confidential_info": confidential_info,
                        "purpose": purpose,
                        "duration": duration,
                        "jurisdiction": jurisdiction,
                        "include_noncompete": include_noncompete,
                        "include_nonsolicitation": include_nonsolicitation,
                        "mutual": mutual
                    })
                elif contract_type == "Service Agreement":
                    contract_data.update({
                        "services": services,
                        "compensation": compensation,
                        "payment_terms": payment_terms,
                        "term": term,
                        "include_confidentiality": include_confidentiality,
                        "include_ip_assignment": include_ip_assignment,
                        "include_termination": include_termination
                    })
                    
                    if payment_terms == "Custom":
                        contract_data["custom_payment_terms"] = custom_payment_terms
                
                # Try to use the API, but fallback to direct model if needed
                try:
                    # Send request to API
                    response = httpx.post(
                        f"{API_URL}/api/contract/generate",
                        json=contract_data
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        contract_text = result.get("contract", "")
                    else:
                        # Fallback to direct model generation
                        contract_text = generate_contract_with_model(contract_data)
                
                except Exception as e:
                    # Fallback to direct model generation
                    st.warning(f"Using fallback generation method: {str(e)}")
                    contract_text = generate_contract_with_model(contract_data)
                
                # Display result
                st.success("Contract generated successfully!")
                
                # Display contract
                st.subheader("Generated Contract")
                st.text_area("Contract Text", contract_text, height=400)
                
                # Download option
                contract_file = StringIO(contract_text)
                st.download_button(
                    label="Download Contract as Text",
                    data=contract_file,
                    file_name=f"{contract_type.replace(' ', '_')}_{effective_date}.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Error generating contract: {str(e)}")

# Add a function to generate contracts directly with the model if API fails
def generate_contract_with_model(contract_data):
    """Generate a contract directly using the Gemini model"""
    try:
        # Check if API key is available
        if not os.getenv("GEMINI_API_KEY"):
            return "Error: Gemini API key not available for direct contract generation."
        
        # Configure Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Create a prompt for the contract
        prompt = f"""
        Generate a complete and legally sound {contract_data.get('contract_type', 'contract')} based on the following information:
        
        First Party: {contract_data.get('party1_name', '')} at {contract_data.get('party1_address', '')}
        Second Party: {contract_data.get('party2_name', '')} at {contract_data.get('party2_address', '')}
        Effective Date: {contract_data.get('effective_date', '')}
        """
        
        # Add contract-specific details to the prompt
        if contract_data.get('contract_type') == "Non-Disclosure Agreement (NDA)":
            prompt += f"""
            Confidential Information: {contract_data.get('confidential_info', '')}
            Purpose of Disclosure: {contract_data.get('purpose', '')}
            Duration: {contract_data.get('duration', '')} years
            Jurisdiction: {contract_data.get('jurisdiction', '')}
            Include Non-Compete Clause: {contract_data.get('include_noncompete', False)}
            Include Non-Solicitation Clause: {contract_data.get('include_nonsolicitation', False)}
            Mutual NDA: {contract_data.get('mutual', False)}
            """
        elif contract_data.get('contract_type') == "Service Agreement":
            prompt += f"""
            Services Description: {contract_data.get('services', '')}
            Compensation: {contract_data.get('compensation', '')}
            Payment Terms: {contract_data.get('payment_terms', '')}
            Term: {contract_data.get('term', '')} months
            Include Confidentiality Clause: {contract_data.get('include_confidentiality', False)}
            Include IP Assignment: {contract_data.get('include_ip_assignment', False)}
            Include Early Termination Clause: {contract_data.get('include_termination', False)}
            """
        
        # Add special provisions
        prompt += f"""
        Special Provisions: {contract_data.get('special_provisions', '')}
        
        Format the contract appropriately with all necessary legal clauses, definitions, and standard provisions.
        Include signature blocks at the end of the contract.
        """
        
        # Generate the contract
        response = model.generate_content(prompt)
        return response.text
    
    except Exception as e:
        return f"Error generating contract with model: {str(e)}"

# Legal Research Assistant
if app_mode == "Legal Research Assistant":
    st.markdown("## Legal Research Assistant")
    st.markdown('<div class="info-box">Conduct comprehensive legal research with AI assistance. Search through case law, statutes, regulations, and legal commentary to find relevant information for your legal questions.</div>', unsafe_allow_html=True)
    
    # Research sidebar
    with st.sidebar:
        st.subheader("Research Sources")
        sources = st.multiselect(
            "Select sources to include",
            ["Case Law", "Federal Statutes", "State Statutes", "Legal Commentary", "Law Reviews", "International Law"],
            default=["Case Law", "Federal Statutes"]
        )
        
        jurisdiction = st.selectbox(
            "Jurisdiction",
            ["All US Jurisdictions", "Federal", "California", "New York", "Texas", "Delaware", "Other US State", "International"]
        )
        
        time_period = st.slider(
            "Time Period (Years)",
            min_value=1,
            max_value=50,
            value=(1, 20),
            help="Limit results to cases within this time period"
        )
        
        st.write("#### Advanced Filters")
        relevance_threshold = st.slider(
            "Relevance Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            step=0.05,
            help="Higher values return more relevant but fewer results"
        )
        
        include_dissenting = st.checkbox("Include Dissenting Opinions", value=False)
        include_overruled = st.checkbox("Include Overruled Cases", value=False)
    
    # Main research interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        research_query = st.text_area(
            "Enter your legal research question",
            height=100,
            placeholder="e.g., What is the standard for proving copyright infringement in digital media cases?"
        )
        
        context = st.text_area(
            "Additional context (optional)",
            height=100,
            placeholder="Provide any specific details or context for your research..."
        )
    
    with col2:
        st.write("##### Research Format")
        result_format = st.radio(
            "Choose output format",
            ["Comprehensive", "Summary", "Case Citations Only"]
        )
        
        max_results = st.slider(
            "Max Results",
            min_value=5,
            max_value=50,
            value=20
        )
    
    # Create expandable section for example query
    with st.expander("See example research question"):
        st.write("""
        **Question**: What is the current legal standard for determining fair use in copyright cases involving AI-generated content?
        
        **Context**: I'm researching how courts have applied fair use doctrine to AI systems that are trained on copyrighted materials, particularly focusing on transformative use and market impact factors.
        """)
    
    # Research buttons
    col1, col2 = st.columns([3, 1])
    with col1:
        search_button = st.button("Conduct Research", type="primary", disabled=not research_query)
    with col2:
        example_button = st.button("Load Example", disabled=research_query != "")
        if example_button:
            st.session_state.response_text = """
# Legal Research: Fair Use in AI-Generated Content

## EXECUTIVE SUMMARY
The legal standard for determining fair use in copyright cases involving AI-generated content is evolving, but courts generally apply the traditional four-factor test established in 17 U.S.C. § 107, with special emphasis on transformative use and market impact when AI systems are involved.

## RELEVANT LEGAL FRAMEWORK

### Statutory Framework
- **17 U.S.C. § 107 (Fair Use)** establishes four factors:
  1. Purpose and character of the use
  2. Nature of the copyrighted work
  3. Amount and substantiality of the portion used
  4. Effect on the potential market

### Key Cases

#### AI Training and Fair Use
- **Authors Guild v. Google, Inc.**, 804 F.3d 202 (2d Cir. 2015)
  - **Holding**: Google's digitization of books for search functionality was transformative fair use
  - **Relevance**: Established that using copyrighted works to "train" a system for a new purpose can be transformative

- **Authors Guild v. HathiTrust**, 755 F.3d 87 (2d Cir. 2014)
  - **Holding**: Creation of a searchable database was transformative and fair use
  - **Relevance**: Processing copyrighted works for computational analysis can qualify as fair use

#### Recent Developments
- **Andy Warhol Foundation v. Goldsmith**, 598 U.S. ___ (2023)
  - **Holding**: Commercial use of a photograph as a basis for artwork requires licensing
  - **Relevance**: Narrowed the scope of "transformative use," potentially affecting AI systems that create derivative works

- **Thaler v. Perlmutter**, No. 22-cv-01564 (D.D.C. 2023)
  - **Holding**: AI-generated works are not eligible for copyright protection without human authorship
  - **Relevance**: Distinguishes between AI as a tool used by humans (potentially eligible) and autonomous AI creation (not eligible)

## ANALYSIS OF FACTORS IN AI CONTEXT

### 1. Purpose and Character of Use
Courts are likely to consider:
- Whether the AI use is transformative (creates something with new meaning or purpose)
- Commercial nature of the AI system
- Whether the AI is being used for research, education, or commercial purposes

### 2. Nature of Copyrighted Work
- More protection is given to creative works than factual compilations
- Published works receive less protection than unpublished works

### 3. Amount and Substantiality Used
- AI systems often require large datasets for training, which may weigh against fair use
- However, courts have recognized that comprehensive copying may be necessary for certain transformative uses (see Google Books)

### 4. Market Impact
- Key consideration: Does the AI-generated output serve as a market substitute for the original?
- Courts examine whether the use threatens the potential market for or value of the copyrighted work

## EMERGING TRENDS
1. **Technical Differentiation**: Courts increasingly consider technical aspects of how AI systems process and transform copyrighted works
2. **"Text and Data Mining" Exception**: Growing recognition of a need for specific exceptions for computational analysis
3. **Licensing Solutions**: Development of licensing frameworks for AI training data

## CONCLUSION
While no court has established a definitive standard specifically for AI-generated content, the trend indicates that:
1. Training AI on copyrighted works may qualify as fair use if sufficiently transformative
2. Generating outputs that compete with or replace original works likely falls outside fair use
3. Commercial uses face greater scrutiny
4. The amount of copyrighted material necessary for training is balanced against the purpose

Given the nascent state of law in this area, companies developing AI systems should consider:
- Implementing attribution mechanisms
- Developing licensing frameworks
- Ensuring generated outputs are sufficiently transformative

---

**Disclaimer**: This research was generated by a legal AI assistant and should not be considered legal advice. Please consult with a licensed attorney for professional legal counsel.
            """
            st.session_state.processing_time = 4.2
            st.experimental_rerun()
    
    if search_button and research_query:
        # Display loading state
        with st.spinner("Conducting legal research..."):
            start_time = time.time()
            
            # Prepare request data
            research_data = {
                "query": research_query,
                "context": context if context else "",
                "sources": ",".join(sources),
                "jurisdiction": jurisdiction,
                "time_period_start": str(time_period[0]),
                "time_period_end": str(time_period[1]),
                "relevance_threshold": str(relevance_threshold),
                "include_dissenting": "true" if include_dissenting else "false",
                "include_overruled": "true" if include_overruled else "false",
                "result_format": result_format,
                "max_results": str(max_results)
            }
            
            # Send request to API
            st.info(f"Sending research request to {API_URL}/api/research")
            try:
                response = httpx.post(f"{API_URL}/api/research", json=research_data, timeout=60.0)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Calculate processing time
                    end_time = time.time()
                    st.session_state.processing_time = end_time - start_time
                    
                    if result.get("success", False):
                        st.session_state.response_text = result.get("research", {}).get("content", "")
                        
                        # Display success
                        st.success("Research completed successfully")
                        
                        # Display metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Sources Searched", value=result.get("research", {}).get("sources_searched", "Multiple"))
                        with col2:
                            st.metric(label="Relevance Score", value=f"{result.get('research', {}).get('relevance_score', 0.85):.2f}")
                        with col3:
                            st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                        
                        # Display research results
                        st.markdown('<div class="response-area">', unsafe_allow_html=True)
                        st.markdown(st.session_state.response_text)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Citation download
                        if result.get("research", {}).get("citations"):
                            citations = result.get("research", {}).get("citations")
                            st.download_button(
                                label="Download Citations",
                                data=citations,
                                file_name="legal_citations.txt",
                                mime="text/plain"
                            )
                    else:
                        st.error(f"Research failed: {result.get('error', 'Unknown error')}")
                else:
                    # Fallback to direct Gemini research if API fails
                    st.warning("API endpoint not available. Using direct Gemini research as fallback.")
                    
                    # Try direct Gemini legal research
                    prompt = f"""
You are an AI legal research assistant with expertise in legal analysis and case law research. Conduct comprehensive legal research on the following question:

RESEARCH QUESTION: {research_query}

ADDITIONAL CONTEXT: {context}

REQUESTED SOURCES: {', '.join(sources)}
JURISDICTION: {jurisdiction}
TIME PERIOD: Past {time_period[1]} years

Please provide a well-structured legal research report that includes:
1. An executive summary of the findings
2. The relevant legal framework (statutes, regulations)
3. Analysis of key cases and their holdings
4. Synthesis of the current legal standard
5. Emerging trends or developments in this area
6. A conclusion with practical implications

Format your response in Markdown with clear headings and sections. Cite specific cases using proper legal citation format.
"""

                    try:
                        if GEMINI_API_KEY:
                            genai.configure(api_key=GEMINI_API_KEY)
                            model = genai.GenerativeModel('gemini-pro')
                            response = model.generate_content(prompt)
                            
                            # Calculate processing time
                            end_time = time.time()
                            st.session_state.processing_time = end_time - start_time
                            
                            st.session_state.response_text = response.text
                            
                            # Display metrics
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric(label="Research Method", value="AI Synthesis")
                            with col2:
                                st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
                            
                            # Display research results
                            st.markdown('<div class="response-area">', unsafe_allow_html=True)
                            st.markdown(st.session_state.response_text)
                            st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.error("Unable to access direct model. Please try again later.")
                    except Exception as e:
                        st.error(f"Error with fallback research: {str(e)}")
            except Exception as e:
                st.error(f"Error conducting legal research: {str(e)}")
    
    # Display previous research if available
    elif st.session_state.response_text and not search_button:
        # Display metrics from example
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Sources Searched", value="Federal Cases, Statutes")
        with col2:
            st.metric(label="Relevance Score", value="0.92")
        with col3:
            st.metric(label="Processing Time", value=f"{st.session_state.processing_time:.2f} sec")
        
        # Display analysis
        st.markdown('<div class="response-area">', unsafe_allow_html=True)
        st.markdown(st.session_state.response_text)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Add citation download example
        st.download_button(
            label="Download Citations",
            data="""Authors Guild v. Google, Inc., 804 F.3d 202 (2d Cir. 2015)
Authors Guild v. HathiTrust, 755 F.3d 87 (2d Cir. 2014)
Andy Warhol Foundation v. Goldsmith, 598 U.S. ___ (2023)
Thaler v. Perlmutter, No. 22-cv-01564 (D.D.C. 2023)
Campbell v. Acuff-Rose Music, Inc., 510 U.S. 569 (1994)
Google LLC v. Oracle America, Inc., 593 U.S. ___ (2021)""",
            file_name="legal_citations.txt",
            mime="text/plain"
        )

# Legal Precedent Analysis
if app_mode == "Legal Precedent Analysis":
    st.title("Legal Precedent Analysis")
    st.write("Analyze case law to find relevant precedents for your legal matter.")
    
    # Input methods
    input_method = st.radio(
        "Input Method",
        ["Upload Case Brief/Filing", "Enter Case Details", "Use Case Citation"]
    )
    
    case_text = ""
    
    if input_method == "Upload Case Brief/Filing":
        uploaded_file = st.file_uploader("Upload Case Document", type=["pdf", "docx", "txt"])
        
        if uploaded_file is not None:
            # Create temporary file and extract text
            temp_file = create_temp_file(uploaded_file)
            try:
                case_text = extract_text_from_doc(temp_file, uploaded_file.type)
            finally:
                cleanup_temp_file(temp_file)
    
    elif input_method == "Enter Case Details":
        case_text = st.text_area("Enter Case Details", height=200)
    
    elif input_method == "Use Case Citation":
        citation = st.text_input("Case Citation (e.g., 'Brown v. Board of Education, 347 U.S. 483 (1954)')")
        jurisdiction = st.selectbox("Jurisdiction", ["Federal", "State - New York", "State - California", "State - Texas", "State - Florida", "State - Other"])
        
        if citation:
            case_text = f"Citation: {citation}\nJurisdiction: {jurisdiction}"
    
    # Additional context
    additional_context = st.text_area("Additional Context or Legal Questions", height=100)
    
    # Configuration options
    st.subheader("Analysis Configuration")
    col1, col2 = st.columns(2)
    
    with col1:
        search_depth = st.slider("Search Depth", min_value=1, max_value=5, value=3, help="Higher values search more extensively but take longer")
        min_relevance = st.slider("Minimum Relevance Score", min_value=0.0, max_value=1.0, value=0.7, help="Higher values return only more relevant precedents")
    
    with col2:
        max_cases = st.slider("Maximum Cases", min_value=3, max_value=15, value=7, help="Maximum number of precedent cases to return")
        recency_weight = st.slider("Recency Weight", min_value=0.0, max_value=1.0, value=0.3, help="Higher values favor more recent cases")
    
    # Focus areas
    st.subheader("Focus Analysis On")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        focus_factual = st.checkbox("Factual Similarities", value=True)
        focus_reasoning = st.checkbox("Legal Reasoning", value=True)
    
    with col2:
        focus_analysis = st.checkbox("Court's Analysis", value=True)
        focus_interpretation = st.checkbox("Statutory Interpretation", value=False)
    
    with col3:
        focus_constitutional = st.checkbox("Constitutional Analysis", value=False)
        focus_procedural = st.checkbox("Procedural History", value=False)
    
    # Construct focus areas list
    focus_areas = []
    if focus_factual:
        focus_areas.append("factual_similarities")
    if focus_reasoning:
        focus_areas.append("legal_reasoning")
    if focus_analysis:
        focus_areas.append("court_analysis")
    if focus_interpretation:
        focus_areas.append("statutory_interpretation")
    if focus_constitutional:
        focus_areas.append("constitutional_analysis")
    if focus_procedural:
        focus_areas.append("procedural_history")
    
    # Action button
    if st.button("Analyze Precedents") and (case_text or citation):
        with st.spinner("Analyzing legal precedents..."):
            start_time = time.time()
            
            try:
                # Prepare data for API
                data = {
                    "case_text": case_text,
                    "additional_context": additional_context,
                    "config": {
                        "search_depth": search_depth,
                        "min_relevance": min_relevance,
                        "max_cases": max_cases,
                        "recency_weight": recency_weight,
                        "focus_areas": focus_areas
                    }
                }
                
                # Send request to API
                try:
                    # First try API endpoint
                    response = httpx.post(
                        f"{API_URL}/api/advanced/precedent/analyze",
                        json=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        process_precedent_response(result, start_time)
                    else:
                        # If API fails, try fallback method
                        st.warning(f"API returned error: {response.status_code}. Using fallback method.")
                        try_fallback_precedent_analysis(case_text, additional_context, focus_areas, start_time)
                
                except requests.exceptions.RequestException as e:
                    st.warning(f"API request failed: {str(e)}. Using fallback method.")
                    try_fallback_precedent_analysis(case_text, additional_context, focus_areas, start_time)
                
            except Exception as e:
                st.error(f"Error analyzing precedents: {str(e)}")
                
                # Example mode for demonstration
                st.subheader("Example Analysis (Demo Mode)")