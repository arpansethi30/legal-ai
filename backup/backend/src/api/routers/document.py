# backend/src/api/routers/document.py
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from src.services.document import DocumentService
from src.utils.helpers import format_error_response, get_file_extensions, validate_file_type

router = APIRouter(
    prefix="/document",
    tags=["document"],
    responses={404: {"description": "Not found"}},
)

# Initialize document service
document_service = DocumentService()

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
        
        # Process and analyze the document using the service
        content = await file.read()
        result = await document_service.analyze_document(content, file.filename, query)
        
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