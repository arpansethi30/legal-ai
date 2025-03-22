# backend/src/api/routers/research.py
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from src.services.research import ResearchService
from src.utils.helpers import format_error_response

# Initialize router with prefix
router = APIRouter(
    prefix="/research",
    tags=["legal research"],
    responses={404: {"description": "Not found"}},
)

# Initialize service
research_service = ResearchService()

class ResearchRequest(BaseModel):
    query: str
    context: Optional[str] = None
    sources: Optional[str] = None
    jurisdiction: Optional[str] = None
    time_period_start: Optional[str] = None
    time_period_end: Optional[str] = None
    relevance_threshold: Optional[float] = None
    include_dissenting: Optional[bool] = None
    include_overruled: Optional[bool] = None
    result_format: Optional[str] = None
    max_results: Optional[int] = None

@router.post("")
async def conduct_research(request: ResearchRequest):
    """
    Conduct legal research on a specific query
    
    - **query**: The legal research question to answer
    - **context**: Optional additional context for the query
    - **sources**: Optional filter for sources (e.g., 'cases', 'statutes', 'treatises')
    - **jurisdiction**: Optional filter for legal jurisdiction
    """
    try:
        result = await research_service.conduct_research(
            query=request.query,
            context=request.context,
            sources=request.sources,
            jurisdiction=request.jurisdiction,
            time_period_start=request.time_period_start,
            time_period_end=request.time_period_end,
            relevance_threshold=request.relevance_threshold,
            include_dissenting=request.include_dissenting,
            include_overruled=request.include_overruled,
            result_format=request.result_format,
            max_results=request.max_results
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