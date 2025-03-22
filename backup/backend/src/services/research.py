# backend/src/services/research.py
from typing import Dict, Any, Optional

from src.models.gemini import GeminiModel

class ResearchService:
    """Service for legal research operations"""
    
    def __init__(self):
        """Initialize the research service"""
        self.gemini_model = GeminiModel()

    async def conduct_research(
        self, 
        query: str, 
        context: Optional[str] = None,
        sources: Optional[str] = None,
        jurisdiction: Optional[str] = None,
        time_period_start: Optional[str] = None,
        time_period_end: Optional[str] = None,
        relevance_threshold: Optional[float] = None,
        include_dissenting: Optional[bool] = None,
        include_overruled: Optional[bool] = None,
        result_format: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Conduct legal research on a specific query
        
        Args:
            query: The legal research question to answer
            context: Optional additional context for the query
            sources: Optional filter for sources
            jurisdiction: Optional filter for legal jurisdiction
            time_period_start: Optional start date for time period filtering
            time_period_end: Optional end date for time period filtering
            relevance_threshold: Optional minimum relevance score
            include_dissenting: Whether to include dissenting opinions
            include_overruled: Whether to include overruled cases
            result_format: Optional format for results (e.g., 'summary', 'detailed')
            max_results: Optional maximum number of results to return
            
        Returns:
            Dict with the success status and research results or error message
        """
        try:
            # Build parameters dictionary for research
            params = {
                "query": query,
                "context": context,
                "sources": sources,
                "jurisdiction": jurisdiction,
                "time_period": {
                    "start": time_period_start,
                    "end": time_period_end
                } if time_period_start or time_period_end else None,
                "relevance_threshold": relevance_threshold,
                "include_dissenting": include_dissenting,
                "include_overruled": include_overruled,
                "result_format": result_format,
                "max_results": max_results
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            # Conduct the research
            result = await self.gemini_model.conduct_legal_research(params)
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": f"Research failed: {result.get('error', 'Unknown error')}",
                    "status_code": 500
                }
            
            return {
                "success": True,
                "data": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An error occurred: {str(e)}",
                "status_code": 500
            } 