# backend/src/api/routers/query.py
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from src.services.query import QueryService
from src.utils.helpers import format_error_response, get_file_extensions, validate_file_type

router = APIRouter(
    prefix="/query",
    tags=["query"],
    responses={404: {"description": "Not found"}},
)

# Initialize query service
query_service = QueryService()

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
        # Process uploaded file if any
        if file:
            # Validate file type
            allowed_types = get_file_extensions("all")
            if not validate_file_type(file.filename, allowed_types):
                return JSONResponse(
                    status_code=400,
                    content=format_error_response(f"Unsupported file type. Allowed types: {', '.join(allowed_types)}", 400)
                )
        
        # Process the query
        result = await query_service.process_query(query, context, file)
        
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