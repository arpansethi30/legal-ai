# backend/app/routers/document.py
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import sys
import os

# Fix imports to be relative to the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from models.document_processor import DocumentProcessor
from models.gemini import GeminiModel
from utils.helpers import format_error_response, get_file_extensions, validate_file_type

router = APIRouter(
    prefix="/document",
    tags=["document"],
    responses={404: {"description": "Not found"}},
)

# Initialize components
gemini_model = GeminiModel()
document_processor = DocumentProcessor()

@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: Optional[str] = Form(None)
):
    """
    Analyze a legal document and extract key information
    
    - **file**: The document to analyze (PDF or image)
    - **query**: Optional specific question about the document
    """
    try:
        # Validate file type
        allowed_types = get_file_extensions("all")
        if not validate_file_type(file.filename, allowed_types):
            return JSONResponse(
                status_code=400,
                content=format_error_response(f"Unsupported file type. Allowed types: {', '.join(allowed_types)}", 400)
            )
        
        # Process the document
        content = await file.read()
        doc_result = await document_processor.process_document(content, file.filename)
        
        if not doc_result["success"]:
            return JSONResponse(
                status_code=400,
                content=format_error_response(f"Document processing failed: {doc_result.get('error', 'Unknown error')}", 400)
            )
        
        # Analyze the document with Gemini
        analysis_result = await gemini_model.analyze_document(
            document_text=doc_result["text"],
            document_images=doc_result["image_paths"],
            query=query
        )
        
        if not analysis_result["success"]:
            return JSONResponse(
                status_code=500,
                content=format_error_response(f"Analysis failed: {analysis_result.get('error', 'Unknown error')}", 500)
            )
        
        response = {
            "document": {
                "filename": file.filename,
                "text_length": len(doc_result["text"]),
                "file_type": doc_result["file_type"]
            },
            "analysis": analysis_result
        }
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=format_error_response(f"An error occurred: {str(e)}", 500)
        )