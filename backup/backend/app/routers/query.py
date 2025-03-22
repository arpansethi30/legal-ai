# backend/app/routers/query.py
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import sys
import os

# Fix imports to be relative to the project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from models.gemini import GeminiModel
from models.document_processor import DocumentProcessor
from utils.helpers import format_error_response, get_file_extensions, validate_file_type

router = APIRouter(
    prefix="/query",
    tags=["query"],
    responses={404: {"description": "Not found"}},
)

# Initialize components
gemini_model = GeminiModel()
document_processor = DocumentProcessor()

@router.post("/")
async def legal_query(
    query: str = Form(...),
    context: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Answer a legal query with optional context
    
    - **query**: The legal question to answer
    - **context**: Optional additional context text
    - **file**: Optional file with relevant information
    """
    try:
        image_paths = []
        
        # Process uploaded file if any
        if file:
            # Validate file type
            allowed_types = get_file_extensions("all")
            if not validate_file_type(file.filename, allowed_types):
                return JSONResponse(
                    status_code=400,
                    content=format_error_response(f"Unsupported file type. Allowed types: {', '.join(allowed_types)}", 400)
                )
            
            # Process the file
            content = await file.read()
            doc_result = await document_processor.process_document(content, file.filename)
            
            if doc_result["success"]:
                context = (context or "") + "\n\n" + doc_result["text"]
                image_paths = doc_result["image_paths"]
            else:
                return JSONResponse(
                    status_code=400,
                    content=format_error_response(f"Document processing failed: {doc_result.get('error', 'Unknown error')}", 400)
                )
        
        # Answer the query
        answer_result = await gemini_model.answer_query(
            query=query,
            context=context,
            image_paths=image_paths
        )
        
        if not answer_result["success"]:
            return JSONResponse(
                status_code=500,
                content=format_error_response(f"Query processing failed: {answer_result.get('error', 'Unknown error')}", 500)
            )
        
        response = {
            "query": query,
            "response": answer_result
        }
        
        return response
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=format_error_response(f"An error occurred: {str(e)}", 500)
        )