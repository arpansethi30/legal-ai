from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Body
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import tempfile
import time
from datetime import datetime
import logging

from ..models.legal_ai_agent import LegalAIAgent, LegalCitation, LegalAgentResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router with prefix
router = APIRouter(
    prefix="/advanced",
    tags=["advanced legal ai"],
    responses={404: {"description": "Not found"}},
)

# Initialize AI agent
legal_agent = LegalAIAgent()

class AdvancedQueryRequest(BaseModel):
    query: str
    context: Optional[str] = None
    domain: Optional[str] = None

class DocumentAnalysisRequest(BaseModel):
    document_type: str = "general"

class DocumentComparisonRequest(BaseModel):
    document_type: str = "general"

@router.post("/query")
async def advanced_legal_query(request: AdvancedQueryRequest):
    """
    Perform an advanced legal query with specialized domain knowledge,
    legal reasoning chains, and relevant citations.
    """
    start_time = time.time()
    logger.info(f"Received advanced legal query: {request.query[:100]}...")
    
    try:
        response: LegalAgentResponse = legal_agent.legal_query(
            query=request.query,
            context=request.context,
            domain=request.domain
        )
        
        # Convert to dict for JSON serialization
        result = {
            "success": True,
            "answer": response.answer,
            "citations": [citation.dict() for citation in response.citations],
            "reasoning_steps": response.reasoning_steps,
            "confidence_score": response.confidence_score,
            "sources_used": response.sources_used,
            "processing_time": response.processing_time,
            "metadata": response.metadata
        }
        
        logger.info(f"Advanced legal query processed in {time.time() - start_time:.2f}s with confidence {response.confidence_score:.2f}")
        return result
    
    except Exception as e:
        logger.error(f"Error processing advanced legal query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/document/analyze")
async def analyze_document(
    document_type: str = Form("general"),
    file: UploadFile = File(...),
):
    """
    Analyze a legal document with specialized understanding of document structure
    and legal implications.
    """
    start_time = time.time()
    logger.info(f"Received document analysis request for document type: {document_type}")
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_path = temp_file.name
    
    try:
        # Save uploaded file
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        
        # Extract text from document (this would need to be implemented based on file type)
        document_text = await extract_text_from_document(temp_path, file.content_type)
        
        # Analyze document
        analysis_result = legal_agent.analyze_document(
            document_text=document_text,
            document_type=document_type
        )
        
        logger.info(f"Document analysis completed in {time.time() - start_time:.2f}s")
        return {
            "success": True,
            "analysis": analysis_result,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing document: {str(e)}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

@router.post("/document/compare")
async def compare_documents(
    document_type: str = Form("general"),
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    """
    Compare two legal documents with specialized legal comparison capabilities.
    """
    start_time = time.time()
    logger.info(f"Received document comparison request for document type: {document_type}")
    
    # Create temporary files
    temp_file1 = tempfile.NamedTemporaryFile(delete=False)
    temp_path1 = temp_file1.name
    temp_file2 = tempfile.NamedTemporaryFile(delete=False)
    temp_path2 = temp_file2.name
    
    try:
        # Save uploaded files
        content1 = await file1.read()
        content2 = await file2.read()
        
        with open(temp_path1, "wb") as f:
            f.write(content1)
        with open(temp_path2, "wb") as f:
            f.write(content2)
        
        # Extract text from documents
        doc1_text = await extract_text_from_document(temp_path1, file1.content_type)
        doc2_text = await extract_text_from_document(temp_path2, file2.content_type)
        
        # Compare documents
        comparison_result = legal_agent.compare_documents(
            doc1_text=doc1_text,
            doc2_text=doc2_text,
            comparison_type=document_type
        )
        
        logger.info(f"Document comparison completed in {time.time() - start_time:.2f}s")
        return {
            "success": True,
            "comparison": comparison_result,
            "processing_time": time.time() - start_time,
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error comparing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error comparing documents: {str(e)}")
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_path1):
            os.unlink(temp_path1)
        if os.path.exists(temp_path2):
            os.unlink(temp_path2)

async def extract_text_from_document(file_path: str, content_type: str) -> str:
    """
    Extract text from a document based on its content type.
    This would need to be expanded based on supported document types.
    """
    # This is a placeholder - in a real implementation, you would use libraries like
    # PyPDF2 for PDFs, docx for Word documents, etc.
    if "pdf" in content_type:
        # Extract text from PDF
        return "PDF text extraction placeholder"
    elif "docx" in content_type or "doc" in content_type:
        # Extract text from Word document
        return "Word document text extraction placeholder"
    elif "text" in content_type:
        # Read text file directly
        with open(file_path, "r") as f:
            return f.read()
    else:
        # Default fallback - just read as text
        try:
            with open(file_path, "r") as f:
                return f.read()
        except UnicodeDecodeError:
            logger.error(f"Could not decode file with content type {content_type}")
            return "Error: Unsupported file type" 