# backend/src/api/routers/advanced_legal.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.services.advanced_legal import AdvancedLegalService
from src.utils.helpers import format_error_response

# Initialize router with prefix
router = APIRouter(
    prefix="/advanced",
    tags=["advanced legal ai"],
    responses={404: {"description": "Not found"}},
)

# Initialize service
advanced_legal_service = AdvancedLegalService()

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
    Process an advanced legal query using AI
    
    - **query**: The legal question to answer
    - **context**: Optional additional context text
    - **domain**: Optional legal domain for specialized processing
    """
    try:
        result = await advanced_legal_service.process_query(
            query=request.query, 
            context=request.context, 
            domain=request.domain
        )
        
        if not result["success"]:
            return JSONResponse(
                status_code=result.get("status_code", 500),
                content=format_error_response(result.get("error", "Unknown error"), result.get("status_code", 500))
            )
        
        return result["data"]
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=format_error_response(f"An error occurred: {str(e)}", 500)
        )

@router.post("/document/analyze")
async def analyze_document(
    document_type: str = Form("general"),
    file: UploadFile = File(...),
):
    """
    Analyze a legal document using advanced AI techniques
    
    - **document_type**: Type of document for specialized processing
    - **file**: The document to analyze
    """
    try:
        result = await advanced_legal_service.analyze_document(
            file=file,
            document_type=document_type
        )
        
        if not result["success"]:
            return JSONResponse(
                status_code=result.get("status_code", 500),
                content=format_error_response(result.get("error", "Unknown error"), result.get("status_code", 500))
            )
        
        return result["data"]
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=format_error_response(f"An error occurred: {str(e)}", 500)
        )

@router.post("/document/compare")
async def compare_documents(
    document_type: str = Form("general"),
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
):
    """
    Compare two legal documents and identify differences
    
    - **document_type**: Type of documents for specialized processing
    - **file1**: First document to compare
    - **file2**: Second document to compare
    """
    try:
        result = await advanced_legal_service.compare_documents(
            file1=file1,
            file2=file2,
            document_type=document_type
        )
        
        if not result["success"]:
            return JSONResponse(
                status_code=result.get("status_code", 500),
                content=format_error_response(result.get("error", "Unknown error"), result.get("status_code", 500))
            )
        
        return result["data"]
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=format_error_response(f"An error occurred: {str(e)}", 500)
        ) 